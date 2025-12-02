# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Flexibilizador Service.

## What is an ADR?

An Architecture Decision Record captures an important architectural decision made along with its context and consequences. ADRs provide documentation for future developers (including your future self) about why certain decisions were made.

## ADR Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [0001](./0001-s3-integration.md) | S3 Integration for Artifact Storage | Accepted | 2024-12 |
| [0002](./0002-async-boto3.md) | Async boto3 with ThreadPoolExecutor | Accepted | 2024-12 |
| [0003](./0003-exception-hierarchy.md) | Custom Exception Hierarchy | Accepted | 2024-12 |

## Template

When adding a new ADR, use the following template:

```markdown
# ADR-NNNN: [Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Context

[What is the issue that we're seeing that motivates this decision?]

## Decision

[What is the change that we're proposing and/or doing?]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Drawback 2]

### Neutral
- [Observation 1]
```

## References

- [Michael Nygard's original ADR article](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub Organization](https://adr.github.io/)
