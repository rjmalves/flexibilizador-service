# Deployment Guide

This guide covers deploying the Flexibilizador Service in production environments.

## Prerequisites

- Docker 24.0+
- Docker Compose v2
- AWS credentials (or MinIO/LocalStack)
- (Optional) Traefik for reverse proxy

## Quick Start

### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/your-org/flexibilizador-service
cd flexibilizador-service

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start service
docker compose up -d
```

### Using Install Script

```bash
cd deploy
sudo ./install.sh
```

## Configuration

### Environment Variables

Create a `.env` file in the installation directory:

```env
# Application
HOST=0.0.0.0
PORT=8000
ROOT_PATH=/api/v1/flex
LOG_LEVEL=INFO

# AWS S3
AWS_REGION=us-east-1
S3_ENDPOINT_URL=
DEFAULT_BUCKET=decomp-bucket

# Processing
TEMP_DIR=/tmp/flexibilizador
ZIP_COMPRESSION_LEVEL=6
MAX_TEMP_DIR_AGE_HOURS=24
```

### AWS Credentials

The service uses the standard boto3 credential chain:

1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM role (for EC2/ECS)

## Deployment Options

### 1. Docker Compose (Recommended)

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f
```

Stop service:

```bash
docker compose down
```

### 2. Docker Standalone

```bash
# Build image
docker build -t flexibilizador-service:latest .

# Run container
docker run -d \
  --name flexibilizador \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /tmp/flexibilizador:/tmp/flexibilizador \
  --env-file .env \
  flexibilizador-service:latest
```

### 3. systemd Service

Install:

```bash
cd deploy
sudo ./install.sh
```

Manage service:

```bash
sudo systemctl status flexibilizador
sudo systemctl start flexibilizador
sudo systemctl stop flexibilizador
sudo systemctl restart flexibilizador
```

View logs:

```bash
sudo journalctl -u flexibilizador -f
```

Uninstall:

```bash
sudo ./deploy/uninstall.sh --purge
```

## Traefik Integration

The Docker Compose configuration includes Traefik labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.flexibilizador.rule=PathPrefix(`/api/v1/flex`)"
  - "traefik.http.routers.flexibilizador.entrypoints=web"
  - "traefik.http.services.flexibilizador.loadbalancer.server.port=8000"
```

Ensure the container is on the same Docker network as Traefik:

```bash
docker network create hpc-network
```

## Health Checks

### Endpoints

| Endpoint            | Purpose     | Response                                         |
| ------------------- | ----------- | ------------------------------------------------ |
| `GET /health`       | Full status | `{"status": "healthy", "version": "2.0.0", ...}` |
| `GET /health/live`  | Liveness    | `{"status": "ok"}`                               |
| `GET /health/ready` | Readiness   | `{"status": "ready"}`                            |

### Docker Health Check

The Dockerfile includes a built-in health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')"
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Monitoring

### Logs

The service logs to stdout in INFO level by default. Configure with:

```env
LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR
```

View Docker logs:

```bash
docker compose logs -f flexibilizador
```

View systemd logs:

```bash
journalctl -u flexibilizador -f
```

### Metrics

Health endpoint provides basic metrics:

```bash
curl http://localhost:8000/health | jq
```

## Security

### Container Security

- Runs as non-root user (UID 1000)
- Minimal base image (python:3.12-slim)
- No development dependencies in production image
- Read-only filesystem support (except temp dir)

### Network Security

- Only expose port 8000
- Use Traefik for TLS termination
- Configure AWS credentials via IAM roles when possible

## Scaling

### Horizontal Scaling

For multiple instances:

```yaml
services:
  flexibilizador:
    deploy:
      replicas: 3
```

### Resource Limits

```yaml
services:
  flexibilizador:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 512M
```

## Troubleshooting

### Container Won't Start

```bash
docker compose logs flexibilizador
```

Check for:

- Missing environment variables
- Invalid AWS credentials
- Port already in use

### S3 Connection Issues

```bash
# Test S3 connectivity from container
docker exec flexibilizador python -c "
import boto3
s3 = boto3.client('s3')
print(s3.list_buckets())
"
```

### Health Check Failing

```bash
curl -v http://localhost:8000/health/live
```

Check:

- Service is running
- Port is exposed correctly
- No firewall blocking

## Backup & Recovery

### Configuration Backup

```bash
tar -czf flexibilizador-config.tar.gz .env docker-compose.yml
```

### Quick Recovery

```bash
# Pull latest image
docker compose pull

# Restart with fresh container
docker compose down
docker compose up -d
```
