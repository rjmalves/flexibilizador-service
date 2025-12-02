#!/bin/bash
# ==============================================================================
# Flexibilizador Service API Examples
#
# Usage:
#   ./curl_examples.sh                    # Run all examples
#   ./curl_examples.sh health             # Run health check only
#   ./curl_examples.sh flex BUCKET HASH   # Run flexibilization
#
# Environment:
#   FLEXIBILIZADOR_URL - Service base URL (default: http://localhost:8000)
# ==============================================================================

set -e

BASE_URL="${FLEXIBILIZADOR_URL:-http://localhost:8000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${YELLOW}=== $1 ===${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if jq is available for pretty-printing
if command -v jq &> /dev/null; then
    JSON_FORMATTER="jq"
else
    JSON_FORMATTER="cat"
    echo "Note: Install jq for pretty-printed JSON output"
fi

# ==============================================================================
# Health Check
# ==============================================================================
health_check() {
    print_header "Health Check"
    echo "GET $BASE_URL/health"
    echo ""

    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" == "200" ]; then
        print_success "Service is healthy"
        echo "$body" | $JSON_FORMATTER
    else
        print_error "Health check failed (HTTP $http_code)"
        echo "$body" | $JSON_FORMATTER
        return 1
    fi
}

# ==============================================================================
# Liveness Probe
# ==============================================================================
liveness_probe() {
    print_header "Liveness Probe"
    echo "GET $BASE_URL/health/live"
    echo ""

    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health/live")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" == "200" ]; then
        print_success "Service is alive"
        echo "$body" | $JSON_FORMATTER
    else
        print_error "Liveness probe failed (HTTP $http_code)"
        echo "$body" | $JSON_FORMATTER
        return 1
    fi
}

# ==============================================================================
# Readiness Probe
# ==============================================================================
readiness_probe() {
    print_header "Readiness Probe"
    echo "GET $BASE_URL/health/ready"
    echo ""

    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health/ready")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" == "200" ]; then
        print_success "Service is ready"
        echo "$body" | $JSON_FORMATTER
    else
        print_error "Readiness probe failed (HTTP $http_code)"
        echo "$body" | $JSON_FORMATTER
        return 1
    fi
}

# ==============================================================================
# Flexibilization
# ==============================================================================
flexibilize() {
    local bucket="${1:-decomp-bucket}"
    local execution_hash="${2:-abc123def456}"
    local program="${3:-DECOMP}"

    print_header "Flexibilization"
    echo "POST $BASE_URL/flex/"
    echo "Bucket: $bucket"
    echo "Hash: $execution_hash"
    echo "Program: $program"
    echo ""

    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/flex/" \
        -H "Content-Type: application/json" \
        -d "{
            \"bucket\": \"$bucket\",
            \"execution_hash\": \"$execution_hash\",
            \"program\": \"$program\",
            \"output_prefix\": \"ingest\"
        }")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" == "200" ]; then
        print_success "Flexibilization successful"
        echo "$body" | $JSON_FORMATTER
    else
        print_error "Flexibilization failed (HTTP $http_code)"
        echo "$body" | $JSON_FORMATTER
        return 1
    fi
}

# ==============================================================================
# Main
# ==============================================================================
main() {
    echo "Flexibilizador Service API Examples"
    echo "Base URL: $BASE_URL"

    case "${1:-all}" in
        health)
            health_check
            ;;
        live)
            liveness_probe
            ;;
        ready)
            readiness_probe
            ;;
        flex)
            flexibilize "${2:-}" "${3:-}" "${4:-}"
            ;;
        all)
            health_check
            liveness_probe
            readiness_probe
            echo ""
            echo -e "${YELLOW}Note: Flexibilization requires valid S3 artifacts${NC}"
            echo "Run: ./curl_examples.sh flex BUCKET HASH"
            ;;
        *)
            echo "Usage: $0 [health|live|ready|flex|all]"
            echo ""
            echo "Commands:"
            echo "  health              - Health check endpoint"
            echo "  live                - Liveness probe"
            echo "  ready               - Readiness probe"
            echo "  flex BUCKET HASH    - Run flexibilization"
            echo "  all                 - Run all health checks (default)"
            exit 1
            ;;
    esac
}

main "$@"
