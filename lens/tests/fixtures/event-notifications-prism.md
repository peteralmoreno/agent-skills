# PRISM — Event notifications

Status: Approved (illustrative example)

## Problem
New subscriber integrations currently require coordinated changes.

## Requirements
R1. Publish domain change events for new subscribers.
R2. Support a later migration path for existing consumers.

## Invariants
I1. Existing consumers remain compatible during changes.

## Solution
S1. Publish domain change events to a dedicated Kafka topic.

## Measures
M1. Integration test demonstrates event publication for new consumers.
M2. Existing-consumer contract test remains compatible.

## Traceability
R1 -> I1 -> S1 -> M1
R2 -> I1 -> S1 -> M2
