# API Examples

This directory contains example code for interacting with the Flexibilizador Service API.

## Files

| File               | Description                     |
| ------------------ | ------------------------------- |
| `flexibilize.py`   | Python example using httpx      |
| `curl_examples.sh` | Shell script with curl examples |

## Prerequisites

For Python examples:

```bash
pip install httpx
```

For curl examples:

```bash
# jq is optional but recommended for pretty-printing JSON
apt-get install jq  # Debian/Ubuntu
brew install jq     # macOS
```

## Quick Start

### Python

```bash
# Flexibilize an execution
python flexibilize.py decomp-bucket abc123def456
```

### curl

```bash
# Make script executable
chmod +x curl_examples.sh

# Run examples
./curl_examples.sh
```

## Environment Variables

| Variable             | Default                 | Description      |
| -------------------- | ----------------------- | ---------------- |
| `FLEXIBILIZADOR_URL` | `http://localhost:8000` | Service base URL |

## API Overview

### Health Check

```bash
curl http://localhost:8000/health
```

### Flexibilize

```bash
curl -X POST http://localhost:8000/flex/ \
  -H "Content-Type: application/json" \
  -d '{
    "bucket": "decomp-bucket",
    "execution_hash": "abc123def456",
    "program": "DECOMP"
  }'
```

## Response Format

### Success (200)

```json
{
  "success": true,
  "execution_hash": "abc123def456",
  "output_key": "ingest/abc123def456_flexibilizado.zip",
  "flexibilizations": [
    {
      "type": "VOLUME_MINIMO",
      "target": "UHE_001",
      "original_value": 100.0,
      "new_value": 90.0,
      "reason": "Infeasibility in period 1"
    }
  ],
  "message": "Flexibilization completed successfully"
}
```

### Error (4xx/5xx)

```json
{
  "error": "ARTIFACT_NOT_FOUND",
  "message": "Required S3 objects not found",
  "details": {
    "bucket": "decomp-bucket",
    "missing_keys": ["artifacts/abc123/entradas/deck_processado.zip"]
  }
}
```
