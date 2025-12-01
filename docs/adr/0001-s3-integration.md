# ADR-0001: S3 Integration for Artifact Storage

## Status

Accepted

## Context

The Flexibilizador Service previously read DECOMP files from the local filesystem on an HPC head node. This approach had several limitations:

1. **Tight coupling**: Service was bound to the specific file system structure
2. **Scalability**: Could not scale horizontally across multiple nodes
3. **Environment dependency**: Required specific mount points and permissions
4. **Migration blocker**: New HPC cluster stores all artifacts in S3

The infrastructure team decided to centralize all artifact storage in S3, which requires the service to integrate with S3 for both reading input files and writing processed outputs.

## Decision

Implement S3 integration with the following approach:

1. **S3Repository abstraction**: Create a repository class that encapsulates all S3 operations
2. **S3UnitOfWork**: Coordinate the download → process → upload workflow
3. **Temporary directory processing**: Download files to a temp directory, process, then upload results
4. **Zip packaging**: Store flexibilized outputs as zip files in S3

### Input Artifacts Location

```
s3://decomp-bucket/artifacts/<execution_hash>/
├── entradas/
│   └── deck_processado.zip    # Input deck (required)
└── saidas/
    ├── inviab_unic.<ext>      # Infeasibility report (required)
    └── relato.<ext>           # Execution report (required)
```

### Output Artifact Location

```
s3://decomp-bucket/ingest/<execution_hash>_flexibilizado.zip
```

## Consequences

### Positive

- **Decoupled from filesystem**: Service can run anywhere with S3 access
- **Centralized storage**: All artifacts in one place with consistent access patterns
- **Horizontal scaling**: Multiple instances can process different executions
- **Cloud-native**: Aligns with modern infrastructure practices
- **Audit trail**: S3 versioning and logging for compliance

### Negative

- **Network latency**: S3 operations add latency vs local filesystem
- **Credentials management**: Requires IAM roles or credentials
- **Cost**: S3 API calls incur costs (minimal for expected volume)
- **Complexity**: Additional abstraction layer to maintain

### Neutral

- Processing time dominated by file parsing, not I/O
- Existing file parsing logic remains unchanged
- Testing requires S3 mocking (moto library)
