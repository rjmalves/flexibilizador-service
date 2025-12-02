# Migration Guide: v1.x to v2.0

This guide covers migrating from the filesystem-based v1.x to the S3-based v2.0 architecture.

## Overview of Changes

### API Changes

| Aspect         | v1.x                           | v2.0                        |
| -------------- | ------------------------------ | --------------------------- |
| **Input**      | Base62-encoded filesystem path | S3 bucket + execution_hash  |
| **Endpoint**   | `POST /flex`                   | `POST /flex/`               |
| **Path Field** | `id` (base62 encoded)          | `bucket` + `execution_hash` |
| **Storage**    | Local filesystem               | AWS S3                      |
| **Output**     | Modified files in place        | Uploaded to S3              |

### Request Format

**v1.x Request:**

```json
{
  "id": "IgMI7zzpD0irzRysgz7ia2z2KbKEIQEpZ2GpEhUvJGvNxpMlD65iC9oeOQ4",
  "program": "DECOMP",
  "rules": []
}
```

**v2.0 Request:**

```json
{
  "bucket": "decomp-bucket",
  "execution_hash": "abc123def456",
  "program": "DECOMP",
  "output_prefix": "ingest"
}
```

### Response Format

**v1.x Response:**

```json
[
  {
    "flexType": "RE",
    "flexStage": 1,
    "flexCode": 45,
    "flexPatamar": "MED",
    "flexLimit": "FOLGAINF",
    "flexSubsystem": "SE",
    "flexAmount": 100.0
  }
]
```

**v2.0 Response:**

```json
{
  "success": true,
  "execution_hash": "abc123def456",
  "output_key": "ingest/abc123def456_flexibilizado.zip",
  "flexibilizations": [
    {
      "flexType": "RE",
      "flexStage": 1,
      "flexCode": 45,
      "flexPatamar": "MED",
      "flexLimit": "FOLGAINF",
      "flexSubsystem": "SE",
      "flexAmount": 100.0
    }
  ],
  "message": "Applied 1 flexibilizations"
}
```

## Migration Steps

### 1. Update Your S3 Bucket Structure

Ensure your S3 bucket follows this structure:

```
s3://your-bucket/
├── artifacts/
│   └── <execution_hash>/
│       ├── entradas/
│       │   └── deck_processado.zip
│       └── saidas/
│           ├── inviab_unic.<ext>
│           └── relato.<ext>
└── ingest/
    └── (output will be placed here)
```

### 2. Update API Calls

Replace base62 encoded paths with bucket and execution_hash:

**Python (Before):**

```python
import base62
import requests

path = "/cases/decomp/run123"
encoded = base62.encodebytes(path.encode())

response = requests.post(
    "http://localhost:5052/flex",
    json={
        "id": encoded,
        "program": "DECOMP"
    }
)
```

**Python (After):**

```python
import requests

response = requests.post(
    "http://localhost:8000/flex/",
    json={
        "bucket": "decomp-bucket",
        "execution_hash": "run123",
        "program": "DECOMP"
    }
)

data = response.json()
if data["success"]:
    output_key = data["output_key"]
    # Download from s3://{bucket}/{output_key}
```

### 3. Update Error Handling

v2.0 uses structured error responses:

```python
response = requests.post(url, json=payload)

if response.status_code == 404:
    error = response.json()
    print(f"Error: {error['error_code']}")
    print(f"Message: {error['message']}")
    print(f"Details: {error['details']}")
elif response.status_code == 422:
    # Parse error or no infeasibilities
    pass
elif response.status_code == 500:
    # Internal error
    pass
```

### 4. Update Environment Variables

| v1.x                      | v2.0                     | Notes                   |
| ------------------------- | ------------------------ | ----------------------- |
| `PORT=5052`               | `PORT=8000`              | Default port changed    |
| `ROOT_PATH=/api/v1/rules` | `ROOT_PATH=/api/v1/flex` | Path prefix changed     |
| -                         | `AWS_REGION=us-east-1`   | New: AWS region         |
| -                         | `S3_ENDPOINT_URL=`       | New: Custom S3 endpoint |
| -                         | `DEFAULT_BUCKET=`        | New: Default bucket     |
| `URI_PATTERN=BASE62`      | (removed)                | No longer needed        |

### 5. Update Deployment

**Before (PM2):**

```bash
pm2 start main.py --name flexibilizador
```

**After (Docker):**

```bash
docker compose up -d
```

**Or with systemd:**

```bash
sudo ./deploy/install.sh
sudo systemctl start flexibilizador
```

## Rollback Plan

If you need to rollback to v1.x:

1. Stop v2.0 service
2. Restore v1.x codebase
3. Reinstall PM2 process
4. Verify base62-encoded requests work

## Compatibility Notes

- The `rules` parameter is no longer supported in v2.0 (use default behavior)
- Health endpoints moved to `/health/live` and `/health/ready`
- OpenAPI docs still available at `/docs` in debug mode

## Support

For migration assistance, open an issue in the repository.
