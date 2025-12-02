# ADR-0002: Async boto3 with ThreadPoolExecutor

## Status

Accepted

## Context

The Flexibilizador Service uses FastAPI, an async Python framework. However, boto3 (the AWS SDK for Python) is synchronous and does not provide native async support. We needed to decide how to integrate S3 operations without blocking the async event loop.

Options considered:

1. **Use boto3 synchronously**: Simple but blocks the event loop
2. **Use aiobotocore**: Native async, but different API and less documented
3. **Wrap boto3 with ThreadPoolExecutor**: Run sync boto3 in a thread pool
4. **Use aioboto3**: Async wrapper around boto3, but adds dependency

## Decision

Use boto3 wrapped with `asyncio.get_event_loop().run_in_executor()` with a `ThreadPoolExecutor`.

```python
async def download_file(self, bucket: str, key: str, local_path: Path) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        self._executor,
        self._sync_download,
        bucket,
        key,
        local_path,
    )

def _sync_download(self, bucket: str, key: str, local_path: Path) -> None:
    self._s3.download_file(bucket, key, str(local_path))
```

### Configuration

- ThreadPoolExecutor with `max_workers=4` (configurable via settings)
- Single executor instance per S3Repository (shared across operations)
- Executor lifecycle managed by repository

## Consequences

### Positive

- **Familiar API**: Standard boto3 API, extensive documentation available
- **Non-blocking**: I/O operations don't block the async event loop
- **Well-tested**: boto3 is the official AWS SDK with extensive testing
- **Compatibility**: Works with moto for testing without modifications
- **Simplicity**: Minimal wrapper code required

### Negative

- **Thread overhead**: Creates threads for each concurrent operation
- **Not truly async**: Operations still block within their thread
- **Resource usage**: Thread pool consumes memory and OS resources
- **Max concurrency**: Limited by thread pool size

### Neutral

- Performance is adequate for expected workload (< 100 concurrent operations)
- Thread pool size can be tuned based on observed performance
- Pattern is well-established in Python async ecosystem

## Alternatives Considered

### aiobotocore

```python
# Would require different API
async with get_session().create_client('s3') as client:
    await client.get_object(Bucket=bucket, Key=key)
```

Rejected because:
- Different API from boto3
- Less community documentation
- Would not work with moto out of the box

### aioboto3

```python
async with aioboto3.client('s3') as client:
    await client.download_file(bucket, key, local_path)
```

Rejected because:
- Additional dependency
- Wrapper may lag behind boto3 releases
- Our workload doesn't require true async I/O performance
