# PRISM Skill Baseline Evaluation

## Prompt A

> Turn this into an engineering specification: "Add reliable bulk invoice export. It should be fast, secure, and retry safely." Do not ask me follow-up questions; make reasonable assumptions.

## Response A

### Engineering specification: Reliable bulk invoice export

#### Objective

Allow authorized users to export large sets of invoices asynchronously. The export must provide a consistent dataset, protect financial and customer information, complete within defined performance targets, and remain safe under worker crashes, duplicate requests, and retries.

#### Assumptions

- The product is multi-tenant.
- Invoice data already has an authoritative database and tenant-scoped authorization model.
- CSV is the initial export format.
- Generated files are stored in encrypted object storage.
- A single export may contain up to 100,000 invoices.
- Exports are snapshots: later invoice edits do not change a completed file.
- Export files expire after 24 hours.

#### User flow

1. An authenticated user selects invoices by explicit IDs or supported filters.
2. The client submits an export request with an idempotency key.
3. The service authorizes the request, records the export job, and returns immediately.
4. A background worker generates the file.
5. The client polls job status or receives an existing product notification.
6. When complete, the user requests a short-lived download URL.
7. The file and its download access expire after 24 hours.

#### API

`POST /v1/invoice-exports`

Request:

```json
{
  "invoice_ids": ["inv_123", "inv_456"],
  "format": "csv"
}
```

Alternatively, the request may contain a supported filter object instead of `invoice_ids`. Supplying both is invalid.

Required header:

```text
Idempotency-Key: <client-generated unique value>
```

Response:

- `202 Accepted` for a newly queued job.
- `200 OK` with the original job when the same tenant, user, request body, and idempotency key are replayed.
- `409 Conflict` when an idempotency key is reused with a different request body.
- `400 Bad Request` for invalid filters or unsupported formats.
- `403 Forbidden` when the caller lacks export permission.
- `429 Too Many Requests` when tenant limits are exceeded.

Example:

```json
{
  "export_id": "exp_abc",
  "status": "queued",
  "created_at": "2026-09-02T15:00:00Z",
  "expires_at": "2026-09-03T15:00:00Z"
}
```

`GET /v1/invoice-exports/{export_id}` returns:

- Status: `queued`, `running`, `succeeded`, `failed`, `canceled`, or `expired`
- Progress counts when available
- A stable error code and retryability flag on failure
- File size, row count, checksum, and schema version on success

`POST /v1/invoice-exports/{export_id}/download` returns a single-use or short-lived signed URL valid for no more than 10 minutes. Authorization is checked again when this endpoint is called.

`POST /v1/invoice-exports/{export_id}/cancel` requests cancellation of a queued or running export.

#### Export contents

- Output is a UTF-8 CSV file inside a ZIP archive.
- The CSV has a documented, versioned column schema.
- Dates use ISO 8601; monetary values use integer minor units plus currency code.
- Rows are ordered deterministically by invoice ID.
- Fields beginning with spreadsheet formula control characters (`=`, `+`, `-`, or `@`) are neutralized.
- The ZIP includes a manifest containing export ID, schema version, creation time, row count, and SHA-256 checksum.
- An invoice that the caller is not authorized to access must never appear in the export.
- The selected dataset is fixed at job creation using a database snapshot marker or equivalent immutable selection boundary.

#### Reliability and retry behavior

- The database job record is the source of truth; the queue only signals available work.
- Queue delivery may be at least once. Workers must therefore be idempotent.
- A worker acquires a renewable lease before processing. Expired leases allow another worker to resume the job.
- Output is written to an export-specific temporary object and published atomically only after generation and checksum validation.
- Retries reuse the same export ID and never expose partial files.
- Transient failures are retried up to five times with exponential backoff and jitter.
- Permanent failures, such as invalid stored criteria or authorization loss, fail immediately with a stable error code.
- Retry progress is checkpointed by deterministic page boundary so already completed pages need not be regenerated.
- Only one final object may be attached to an export record. Duplicate worker completions are resolved with a conditional database update.
- A reconciliation process requeues jobs whose leases expired and deletes orphaned temporary objects.
- Canceling a job prevents publication and schedules partial output for deletion.

#### Security

- Require a dedicated invoice-export permission.
- Enforce tenant scope at request creation, data retrieval, status lookup, and download.
- Re-evaluate access before issuing a download URL.
- Encrypt files in transit and at rest with managed keys.
- Never place invoice contents, customer PII, signed URLs, or authorization tokens in application logs or queue payloads.
- Queue messages contain only the export ID and routing metadata.
- Audit job creation, completion, download, cancellation, expiration, and administrative access.
- Limit signed URLs to the generated object and use a maximum 10-minute lifetime.
- Delete expired files and revoke their availability.
- Apply per-user and per-tenant concurrency and daily-volume limits.
- Treat exported filenames and cell values as untrusted input.

#### Performance and capacity targets

- `POST` acknowledgment: p95 under 500 ms, excluding client network latency.
- Status lookup: p95 under 300 ms.
- A 10,000-invoice export completes within 2 minutes at p95.
- A 100,000-invoice export completes within 10 minutes at p95 under documented normal load.
- Support at least 20 concurrently running exports and 500 queued exports per tenant without cross-tenant starvation.
- Workers stream records and multipart-upload output; they must not hold the complete export in memory.
- Database reads use bounded pages and must not lock invoice rows for the duration of the export.

#### Observability and operations

Record metrics for:

- Queue delay and total completion time
- Throughput and exported row count
- Attempts, retries, lease expirations, and terminal failures
- Active jobs by tenant
- Generated bytes and storage cleanup failures
- Unauthorized and rate-limited requests

Structured logs include export ID, tenant ID, state transition, attempt number, and stable error code, but no invoice contents or signed URL.

Alert when:

- Completion SLO falls below 99% over 30 days
- Oldest queued job exceeds 5 minutes
- Terminal failure rate exceeds 1% over 15 minutes
- Expired files or temporary objects fail cleanup
- Queue depth or worker saturation exceeds operational thresholds

#### Acceptance criteria

1. An authorized user can request, monitor, and download a CSV export containing the correct invoice snapshot.
2. Repeating an identical request with the same idempotency key returns the same export and does not create another job.
3. Reusing an idempotency key with different input returns `409`.
4. Duplicate queue delivery and concurrent workers produce only one published file.
5. Killing a worker during generation causes the job to resume or retry without exposing a partial or duplicate export.
6. Transient database, queue, and object-storage failures follow the retry policy and eventually succeed when the dependency recovers.
7. Permanent failures finish with a stable, actionable error and are not retried indefinitely.
8. Cross-tenant access to job status, file content, or download URLs is denied and covered by automated tests.
9. Expired and canceled exports cannot be downloaded, and their objects are deleted.
10. Formula-injection test values are neutralized in the CSV.
11. Load tests demonstrate the latency and completion targets at the stated capacity.
12. Audit events exist for every security-relevant lifecycle action.
13. Chaos tests covering duplicate delivery, lease expiry, worker termination, and publish races do not create corrupt or multiple final files.

#### Out of scope

- PDF, XLSX, and accounting-platform-specific formats
- Scheduled recurring exports
- Emailing export files as attachments
- Exports larger than 100,000 invoices
- Changes to invoice calculation or invoice authorization rules

## Prompt B

> Review this spec: "Build exports with a queue. Use Redis. It must be scalable. We will know it works when QA likes it." Identify whether it is ready for implementation.

## Response B

The spec is not ready for implementation.

It establishes only three broad directions: exports should run asynchronously, Redis is expected somewhere in the solution, and scalability matters. None is precise enough to implement or verify consistently. “QA likes it” is subjective and cannot serve as an acceptance criterion.

Major gaps include:

- User workflow, API contract, export format, filters, maximum size, and file retention
- Definition of “scalable,” including throughput, concurrency, latency, and dataset targets
- Authorization, tenant isolation, encryption, audit requirements, and download controls
- Job states and their allowed transitions
- Retry policy, idempotency behavior, duplicate-delivery handling, worker leases, and crash recovery
- Snapshot consistency and behavior when invoices change during generation
- Storage and atomic publication of completed files
- Cancellation, expiration, cleanup, and permanent-failure behavior
- Rate limits and tenant fairness
- Monitoring, alerting, operational ownership, and measurable service objectives
- Objective automated acceptance tests

“Use Redis” is also incomplete as an architecture decision. The spec must state whether Redis is the queue, a broker backing a specific queue library, a cache, or a coordination mechanism. If it is the queue backend, the design must define persistence, replication, failover, delivery semantics, acknowledgement behavior, visibility or lease handling, dead-letter treatment, and what happens if Redis loses queued data. The authoritative job state should normally live in durable application storage rather than only in Redis.

Before implementation, the spec needs measurable requirements and contracts equivalent to those above. At minimum, stakeholders must approve the export limits and format, security model, API, consistency rules, performance targets, retry/idempotency model, failure handling, and executable acceptance criteria. Redis should then be accepted or rejected based on those requirements rather than treated as the design itself.

## Self-audit

I naturally organized Prompt A around objective, assumptions, interface, data contract, lifecycle, reliability, security, performance, operations, acceptance criteria, and scope. For Prompt B, I gave a readiness verdict, identified missing implementation decisions, examined the named technology choice, and listed the conditions for readiness.

I invented decisions because the prompt prohibited follow-up questions. These include CSV-in-ZIP output, API paths, a 100,000-invoice limit, 24-hour retention, 10-minute signed URLs, five retries, specific latency/completion targets, concurrency limits, job states, snapshot semantics, and Redis not being the authoritative job store. I labeled them as assumptions or concrete specification choices; they require product and architecture validation before adoption. I did not inspect repository context or any PRISM material.

## Observed baseline gaps

- It did not use explicit PRISM P/R/I/S/M labels or traceability.
- It invented many concrete decisions under pressure.
- Its review correctly rejected subjective proof but did not map findings to a repeatable five-view rubric.
