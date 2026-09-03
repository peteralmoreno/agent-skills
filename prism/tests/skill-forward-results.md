# PRISM Skill Forward-Test Results

## Prompt A

> Turn this into an engineering specification: "Add reliable bulk invoice export. It should be fast, secure, and retry safely." Do not ask me follow-up questions; make reasonable assumptions.

## Response A

# Bulk Invoice Export — Draft Engineering Specification

Status: Draft based on explicit assumptions. The assumed scope and proposed acceptance targets below should be confirmed before implementation.

## Problem

Users who need many invoices currently lack a dependable way to export them as one operation. Large exports may take too long for a synchronous request, and failures can force users to restart without knowing whether work was duplicated or partially completed.

Affected parties are authenticated finance and operations users, the invoice service, and the systems that process and store export artifacts.

The desired outcome is that an authorized user can request a bulk export, receive progress and a final downloadable artifact, and safely retry after client, worker, or dependency failures without missing, duplicating, or disclosing invoice data.

In scope:

- Asynchronous export of a user-selected or filtered set of invoices.
- Job creation, status reporting, automatic recovery from transient failures, and secure artifact download.
- CSV output for up to 100,000 invoices per job.
- Operational telemetry and audit events for the export lifecycle.

Non-goals:

- Creating or modifying invoices.
- Cross-tenant exports.
- Scheduled or emailed exports.
- PDF generation, custom templates, or formats other than CSV.
- Permanent archival of export files.

## Requirements

R1. An authenticated user may submit a bulk export request containing either invoice IDs or supported invoice filters, plus a client-generated idempotency key. The service must validate the request and return an export operation ID or a documented validation/authorization error.

R2. Submission must be asynchronous: the service must acknowledge an accepted request without waiting for the export file to be generated.

R3. A user may retrieve an operation's status. The public states must include `queued`, `running`, `succeeded`, and `failed`; a terminal response must include either authorized download information or a stable error code indicating why the operation could not complete.

R4. A successful artifact must contain exactly one row for every invoice that both matched the request at the operation's snapshot boundary and was authorized for that user and tenant. It must not include invoices outside that set.

R5. Repeating an equivalent request with the same tenant, requester, and idempotency key must refer to the same logical operation and must not create an additional export artifact or duplicate invoice rows. Reusing that key for a materially different request must return an idempotency-conflict error.

R6. A transient worker or dependency failure must be retried automatically within a bounded retry policy. Processing must resume or restart without changing the logical contents of the export. A permanent failure or exhausted retry budget must move the operation to `failed` with a diagnosable, non-sensitive error code.

R7. Only a currently authorized user from the originating tenant may view operation status or download its artifact. Authorization must be checked when the export is requested and again when status or download access is requested.

R8. For the assumed workload, the submission endpoint must meet the proposed latency target in M6, and accepted jobs must meet the proposed completion targets in M7.

R9. The service must emit audit records for request acceptance, terminal outcome, and artifact download. The records must identify the actor, tenant, operation, timestamp, and outcome without recording invoice contents or download credentials.

R10. Export artifacts must expire after the assumed retention period. After expiry, the service must not provide the artifact and must return a documented expiration result.

## Invariants

I1. Data from one tenant must never appear in another tenant's export, status response, artifact location, logs, or metrics.

I2. Invoice data and export artifacts must be encrypted in transit and at rest using the platform's approved mechanisms. Secrets, credentials, signed download tokens, and invoice contents must not be written to application logs.

I3. Retries, worker restarts, duplicate deliveries, and repeated client submissions must not change the logical export contents or create more than one successful artifact for an operation.

I4. Every job must use one stable invoice snapshot boundary. Invoice creation or modification after that boundary must not produce a mixed-time export.

I5. Every accepted operation must eventually reach either `succeeded` or `failed`; retry attempts must be bounded and observable.

I6. Authorization to create an export does not grant permanent access. Status and download access must remain tenant-scoped and must be denied when the actor is no longer authorized.

I7. A partial or corrupt artifact must never be exposed as a successful result. Only a fully finalized artifact whose integrity metadata has been recorded may be downloaded.

I8. Existing invoice read behavior and existing clients must remain compatible; bulk export introduces additive interfaces only.

I9. An artifact must become inaccessible no later than the configured retention deadline, including through previously issued download credentials.

## Solution

All decisions in this section are proposed unless the source prompt fixed them. The required outcomes are reliability, security, safe retry, and adequate performance; no particular queue or storage technology is fixed by the prompt.

S1. Use an asynchronous export workflow: the API validates and authorizes the request, persists an operation record, and enqueues work; workers generate the artifact; the status API reads the operation record. This keeps large jobs outside request time limits.

S2. Treat the operation record as the authoritative lifecycle state. Store the operation ID, tenant and requester identity, normalized request fingerprint, idempotency key, snapshot boundary, state, attempt count, progress, terminal error, artifact metadata, and retention deadline in a durable transactional store.

S3. Enforce idempotency with a uniqueness constraint on `(tenant, requester, idempotency_key)`. On a duplicate key, compare the normalized request fingerprint and return the existing operation or an idempotency conflict. Queue delivery may be at least once; workers must claim and transition jobs atomically.

S4. Resolve export membership against a stable database snapshot or immutable high-water mark, then read invoices in deterministic, bounded chunks. Stream rows to a temporary artifact so worker memory does not grow with export size.

S5. Finalize artifacts with an atomic publish step. Record size and checksum before moving the operation to `succeeded`; never expose the temporary object. Store artifacts in approved encrypted object storage.

S6. Use exponential backoff with jitter for errors classified as transient, with a proposed limit of five attempts. Persist attempt state before redelivery. Classify validation, authorization, and unsupported-request errors as permanent. The particular durable queue technology remains an open choice.

S7. Serve downloads through a short-lived, tenant-authorized mechanism, such as an application-mediated response or a signed URL issued only after authorization. A signed URL must expire within 15 minutes and never exceed the artifact retention deadline.

S8. Emit structured, non-sensitive logs, metrics, traces, and audit events keyed by operation ID. Alert on queue age, terminal failure rate, retry exhaustion, processing latency, and artifact-finalization errors.

Tradeoffs:

- A stable snapshot and durable operation state add storage and coordination cost, but are necessary for reproducible retries.
- At-least-once delivery is acceptable because idempotent claiming and atomic publication protect the external result; requiring exactly-once queue delivery would add complexity without removing the need for idempotency.
- Asynchronous completion adds a status workflow but avoids request timeouts and enables bounded recovery for large exports.

## Measures

M1. Integration tests request exports by IDs and filters and verify that the CSV contains exactly the authorized invoices at the recorded snapshot boundary, once each, with the documented schema.

M2. Tenant-isolation and authorization tests attempt job creation, status access, and artifact download using another tenant, an unauthorized role, and a user whose access was revoked after creation; every attempt must be denied without leaking existence or contents.

M3. Idempotency tests submit the same request and key concurrently and sequentially, redeliver queue messages, and restart a worker during generation. Each case must produce one logical operation, one published artifact, and identical artifact checksum. Reusing the key with a different normalized request must return the documented conflict.

M4. Fault-injection tests fail the worker, invoice reader, queue acknowledgement, and artifact store at each lifecycle boundary. Transient failures must recover within the retry budget; permanent or exhausted failures must reach `failed`; no temporary or corrupt artifact may be downloadable.

M5. Snapshot-consistency tests change invoices while an export is running and verify that the result reflects one documented snapshot boundary rather than a mixture of pre-change and post-change data.

M6. Proposed submission target: in a representative production-like environment with 50 concurrent submissions, the create-export endpoint has p95 latency of at most 2 seconds and p99 of at most 5 seconds, excluding rejected requests.

M7. Proposed processing targets while queue utilization is at or below 70%: p95 completion within 5 minutes for 10,000-invoice CSV exports and within 30 minutes for 100,000-invoice CSV exports. Benchmark reports must record row width, dataset shape, worker resources, concurrency, queue wait, processing time, and artifact size.

M8. Proposed reliability target: over a rolling 30-day production window, at least 99.9% of valid, authorized jobs complete successfully within their retry budget, excluding documented upstream outages beyond the export service's control. Dashboards must separately show first-attempt success, recovered jobs, retry exhaustion, queue age, and end-to-end latency.

M9. Security verification must include dependency and static scans, transport and storage encryption checks, log-scrubbing tests, signed-download expiry tests, and a review of tenant and role enforcement. No high- or critical-severity finding may remain open at release.

M10. Retention tests verify that artifacts and all download paths become inaccessible no later than 24 hours after success, and that cleanup is safe to repeat.

M11. Compatibility tests verify existing invoice read APIs and clients remain unchanged. Rollout must use a feature flag or limited tenant cohort, with a tested rollback that stops new submissions while preserving status and secure access for already accepted operations.

## Traceability

- R1, R5 -> I3 -> S2, S3 -> M3
- R2, R3 -> I5 -> S1, S2 -> M4, M8
- R4 -> I1, I4, I7 -> S4, S5 -> M1, M5
- R6 -> I3, I5, I7 -> S2, S3, S5, S6 -> M3, M4, M8
- R7 -> I1, I2, I6 -> S2, S7 -> M2, M9
- R8 -> I5 -> S1, S4 -> M6, M7, M8
- R9 -> I1, I2 -> S8 -> M2, M9
- R10 -> I9 -> S2, S7 -> M10
- The additive-compatibility guarantee I8 is implemented by S1's separate asynchronous interface and verified by M11; it protects the overall change rather than a single new behavior.

## Assumptions and open questions

Assumptions made because follow-up questions were disallowed:

- A1. The first release exports CSV, not PDFs or attachments.
- A2. One job contains at most 100,000 invoices; larger requests are rejected with a documented limit error.
- A3. Users may select invoices by explicit IDs or supported filters already understood by the invoice service.
- A4. The source of truth can provide a stable snapshot or high-water mark suitable for deterministic rereads.
- A5. Artifacts are retained for 24 hours, while job metadata and audit records follow existing platform retention policy.
- A6. Five attempts, a 15-minute download credential, the M6/M7 performance targets, and the M8 reliability objective are proposed acceptance baselines, not facts supplied by the requester.
- A7. The platform already has approved authentication, authorization, encryption, object storage, audit retention, and secret-management mechanisms that this feature can reuse.
- A8. Cancellation, scheduling, email delivery, localization, custom columns, and additional export formats are deferred.

Open questions to resolve during review:

- O1. Confirm the CSV schema, invoice filters, maximum row count, and behavior when the limit is exceeded.
- O2. Confirm whether legal or regulatory policy requires a different artifact or audit retention period.
- O3. Confirm the representative workload and service-level objectives; revise M6-M8 if the assumptions do not match production demand.
- O4. Confirm snapshot support and choose the durable queue and state-store technologies consistent with the existing platform.
- O5. Confirm whether users whose access is revoked should lose access immediately, as assumed, or retain access to previously created exports.

## Prompt B

> Review this spec: "Build exports with a queue. Use Redis. It must be scalable. We will know it works when QA likes it." Identify whether it is ready for implementation.

## Response B

**Verdict: Not ready.**

The text names two implementation choices but does not define the problem, observable export behavior, protected guarantees, objective acceptance evidence, or traceability needed for implementation. “Scalable” and “QA likes it” cannot produce a consistent engineering or acceptance decision.

## Problem

Missing. The spec does not identify:

- who needs exports or what current failure or opportunity motivates the work;
- what is being exported, from which system, or in what format;
- the desired user-visible outcome;
- scope boundaries such as maximum export size, synchronous versus asynchronous use, retention, cancellation, or supported clients;
- non-goals.

Without those boundaries, implementers cannot tell whether the queue is solving latency, reliability, traffic isolation, scheduled processing, or something else.

## Requirements

Not adequate. “Build exports with a queue” and “Use Redis” prescribe solution elements rather than observable promises. “It must be scalable” is an unbounded adjective: it has no workload, data size, concurrency, latency, throughput, or resource ceiling.

At minimum, proposed requirements should be added and numbered for:

- accepted inputs, authorization context, output format, and documented validation errors;
- submission and status behavior, including public lifecycle states and terminal outcomes;
- completeness and consistency of export contents;
- duplicate submission and retry behavior;
- maximum job size and concurrency behavior;
- artifact access and expiration;
- failure, timeout, and recovery behavior.

These should be stated as observable `R#` promises without assuming Redis is the requirement.

## Invariants

Missing. The spec needs explicit, testable guarantees for at least:

- tenant and user authorization boundaries;
- protection of exported data in transit, at rest, and in logs;
- idempotency under client retries and duplicate queue delivery;
- snapshot consistency and the prevention of missing or duplicate records;
- bounded retries and eventual terminal state;
- non-exposure of partial artifacts;
- compatibility with existing export consumers, if any.

## Solution

Incomplete. A queue and Redis do not define an export architecture. The spec must say what Redis is responsible for: queue transport, lifecycle state, deduplication, locking, cached metadata, or some combination. It also needs:

- component responsibilities and the end-to-end workflow;
- the durable source of truth for job state;
- delivery semantics and worker-claim behavior;
- idempotency-key and duplicate-delivery handling;
- snapshot or pagination strategy;
- artifact construction, storage, atomic publication, and cleanup;
- retry classification, backoff, attempt limits, and terminal-failure behavior;
- rationale for Redis, including durability and failover expectations;
- alternatives considered and the tradeoff that makes Redis preferable.

Redis should remain a proposed solution decision until its role and rationale are confirmed. If Redis is organizationally mandated, the spec should record that constraint and its source.

## Measures

Not adequate. “QA likes it” is subjective and neither reproducible nor traceable. QA review can supplement acceptance evidence, but it cannot replace defined pass/fail criteria.

Proposed measures should include:

- acceptance tests for exact, authorized export contents and documented errors;
- duplicate request, duplicate delivery, and worker-restart tests proving idempotency;
- fault injection for Redis, workers, source reads, and artifact storage;
- security tests for tenant isolation, authorization, token expiry, encryption, and log scrubbing;
- benchmarks at agreed row counts and concurrency, with explicit p95/p99 latency and throughput targets;
- operational signals for queue age, attempts, terminal failures, end-to-end duration, and artifact-finalization failures;
- rollout and rollback evidence.

The workload and target numbers must be confirmed rather than invented during implementation.

## Traceability

Missing. There are no numbered requirements, invariants, solution decisions, or measures to connect. Important chains should be explicit, for example:

- `R-retry -> I-idempotency -> S-operation identity and atomic worker claim -> M-duplicate delivery and restart tests`
- `R-performance -> I-bounded resource use -> S-chunked generation and queue-based workers -> M-load benchmark`
- `R-authorized download -> I-tenant isolation -> S-authorized artifact access -> M-cross-tenant denial tests`

Those examples are proposed shapes, not approved IDs or silent additions to the spec.

## Blocking ambiguities and unverified assumptions

- G1. Export subject, users, input selection, output format, and scope are unknown.
- G2. “Scalable” has no workload model or measurable target.
- G3. Reliability, retry, duplicate delivery, consistency, and terminal-failure behavior are unspecified.
- G4. Security and tenant boundaries are unspecified despite exports likely containing sensitive data.
- G5. Redis's exact role, durability settings, ownership, failover model, and rationale are unspecified.
- G6. Job state and artifact ownership are unspecified.
- G7. “QA likes it” is subjective and cannot establish acceptance.
- G8. No rollout, rollback, compatibility, monitoring, or operational ownership is defined.
- G9. No traceability exists between desired behavior, guarantees, design choices, and evidence.

## Minimum revision needed before implementation

The spec owner should first define and approve the problem and scope, then add numbered observable requirements, explicit invariants, and measurable targets. After that, Redis can be evaluated or confirmed as a numbered solution decision with a defined responsibility, rationale, and tradeoffs. Finally, each important requirement must be connected to objective tests or operational evidence. Until G1-G9 are resolved and the resulting chains are reviewable, implementation should not begin.

## Self-audit

Loading PRISM materially affected both the organization and the treatment of uncertainty:

- I used the required Problem -> Requirements -> Invariants -> Solution -> Measures sequence, followed by Traceability and Assumptions/open questions, instead of turning the prompts directly into an implementation plan.
- In Response A, I separated observable promises (`R#`) from technical choices (`S#`). The asynchronous workflow, operation record, queue semantics, storage flow, and retry mechanism appear as proposed solution decisions rather than being disguised as product requirements.
- I converted “fast,” “secure,” “reliable,” and “retry safely” into observable behavior, protected invariants, and verification evidence. Because the prompt supplied no thresholds, I did not present numbers as established facts: CSV scope, job size, retention, retry count, download-token duration, latency, completion, and reliability targets are explicitly labeled assumptions or proposals and repeated in the final uncertainty register.
- I made explicit traceability chains so a reviewer can follow important promises through the invariants that protect them, the decisions intended to satisfy them, and the measures that prove them.
- In Response B, I led with one permitted readiness verdict, assessed all six review views, identified subjective evidence and disconnected implementation choices, and assigned gap IDs because the supplied text had no usable requirement IDs.
- I treated Redis as a solution choice whose role and rationale are missing, not as an observable requirement. I proposed revision shapes without silently converting them into an approved rewritten specification.
- I honored the no-follow-up constraint for Prompt A by making bounded assumptions while keeping them visible. I also stopped at specification and review work; I did not inspect an application repository, create an implementation plan, or modify product code.

## Comparison to baseline

The forward run corrected the three baseline gaps:

- It used the explicit Problem, Requirements, Invariants, Solution, Measures, and Traceability structure in both modes.
- It still supplied useful draft detail under the no-follow-up constraint, but isolated invented limits, targets, formats, and technology choices as proposals, assumptions, or open questions instead of presenting them as approved facts.
- It reviewed the weak specification through a repeatable five-view rubric, treated Redis as an unconfirmed solution choice, replaced subjective acceptance with objective measure categories, and showed example traceability chains without silently rewriting the input.
