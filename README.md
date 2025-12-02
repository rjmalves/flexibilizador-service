# Flexibilizador Service

REST API for applying flexibilizations to DECOMP executions with infeasibilities.

## Overview

The Flexibilizador Service is a microservice that automatically relaxes constraint limits in DECOMP optimization models when infeasibilities are detected. It reads DECOMP artifacts from S3, applies flexibilization rules based on the detected violations, and uploads the modified deck back to S3.

## Features

- **S3 Integration**: Reads DECOMP artifacts from S3 and uploads flexibilized results
- **Async Processing**: Uses boto3 with async wrappers for efficient I/O
- **Health Checks**: Kubernetes/Docker compatible health endpoints
- **Docker Deployment**: Production-ready container with multi-stage build
- **Traefik Integration**: Built-in labels for reverse proxy routing
- **Systemd Service**: Auto-start on boot with proper lifecycle management

## Quick Start

### Prerequisites

- Python 3.12+
- AWS credentials configured (or LocalStack for development)
- Docker and Docker Compose (for deployment)

### Installation (Development)

```bash
git clone https://github.com/your-org/flexibilizador-service
cd flexibilizador-service

# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Or using pip
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Installation (Production)

```bash
cd deploy
sudo ./install.sh
```

### Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

| Variable                | Description                           | Default               |
| ----------------------- | ------------------------------------- | --------------------- |
| `HOST`                  | Bind address                          | `0.0.0.0`             |
| `PORT`                  | Listen port                           | `8000`                |
| `ROOT_PATH`             | URL prefix for reverse proxy          | `/api/v1/flex`        |
| `LOG_LEVEL`             | Logging level                         | `INFO`                |
| `AWS_REGION`            | AWS region for S3                     | `us-east-1`           |
| `S3_ENDPOINT_URL`       | Custom S3 endpoint (MinIO/LocalStack) | (empty)               |
| `DEFAULT_BUCKET`        | Default S3 bucket                     | `decomp-bucket`       |
| `TEMP_DIR`              | Temporary file directory              | `/tmp/flexibilizador` |
| `ZIP_COMPRESSION_LEVEL` | Compression level (0-9)               | `6`                   |

## API Reference

### POST /flex/

Apply flexibilization to a DECOMP execution.

**Request:**

```json
{
  "bucket": "decomp-bucket",
  "execution_hash": "abc123def456",
  "program": "DECOMP",
  "output_prefix": "ingest"
}
```

**Response (Success):**

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

**Error Response:**

```json
{
  "error_code": "ARTIFACT_NOT_FOUND",
  "message": "Could not find execution artifacts",
  "details": {
    "bucket": "decomp-bucket",
    "key": "artifacts/abc123/entradas/deck_processado.zip"
  }
}
```

### Health Endpoints

| Endpoint            | Description                     | Use Case                   |
| ------------------- | ------------------------------- | -------------------------- |
| `GET /health`       | Full health status with version | Monitoring                 |
| `GET /health/live`  | Simple liveness check           | Kubernetes liveness probe  |
| `GET /health/ready` | Readiness check                 | Kubernetes readiness probe |

## S3 Bucket Structure

The service expects the following S3 structure:

```
s3://bucket/
├── artifacts/
│   └── <execution_hash>/
│       ├── entradas/
│       │   └── deck_processado.zip    # Input (downloaded)
│       └── saidas/
│           ├── inviab_unic.<ext>      # Downloaded
│           └── relato.<ext>           # Downloaded
│
└── ingest/
    └── <execution_hash>_flexibilizado.zip   # Output (uploaded)
```

## Deployment

### Docker

```bash
# Build image
docker build -t flexibilizador-service:latest .

# Run container
docker run -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e DEFAULT_BUCKET=decomp-bucket \
  flexibilizador-service:latest
```

### Docker Compose

```bash
# Start with Docker Compose
docker compose up -d

# View logs
docker compose logs -f
```

### Systemd Service

```bash
# Install service
cd deploy
sudo ./install.sh

# Manage service
sudo systemctl status flexibilizador
sudo systemctl restart flexibilizador
sudo journalctl -u flexibilizador -f
```

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### With Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Development Server

```bash
python main.py
# or with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Using LocalStack

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Migration from v1.x

See [MIGRATION.md](docs/MIGRATION.md) for upgrading from the filesystem-based v1.x to S3-based v2.0.

### Key Changes

| v1.x                         | v2.x                                             |
| ---------------------------- | ------------------------------------------------ |
| Filesystem paths             | S3 bucket + execution_hash                       |
| Base62 encoded paths         | Direct S3 keys                                   |
| PM2 managed                  | Docker + systemd                                 |
| `POST /flex` with `id` field | `POST /flex/` with `bucket` and `execution_hash` |

## Flexibilization Results

Each flexibilization result contains:

| Field           | Description                                |
| --------------- | ------------------------------------------ |
| `flexType`      | Constraint type (RE, EV, TI, HQ, HE, etc.) |
| `flexStage`     | Stage number                               |
| `flexCode`      | Constraint identifier code                 |
| `flexPatamar`   | Load level (when applicable)               |
| `flexLimit`     | Limit type (L. INF, L. SUP)                |
| `flexSubsystem` | Subsystem (SE, S, NE, N)                   |
| `flexAmount`    | Amount of flexibilization applied          |

## License

See [LICENSE](LICENSE) file.
