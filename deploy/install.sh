#!/bin/bash
# =============================================================================
# Flexibilizador Service Installation Script
# =============================================================================
# Usage: sudo ./install.sh
# =============================================================================

set -euo pipefail

# Configuration
SERVICE_NAME="flexibilizador"
INSTALL_DIR="/opt/flexibilizador-service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose v2 is not installed"
        exit 1
    fi
    
    log_info "Docker and Docker Compose are available"
}

create_install_dir() {
    log_info "Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
}

copy_files() {
    log_info "Copying application files..."
    
    # Copy essential files
    cp "$PROJECT_DIR/docker-compose.yml" "$INSTALL_DIR/"
    cp "$PROJECT_DIR/Dockerfile" "$INSTALL_DIR/"
    cp "$PROJECT_DIR/requirements.txt" "$INSTALL_DIR/"
    cp "$PROJECT_DIR/main.py" "$INSTALL_DIR/"
    
    # Copy app directory
    cp -r "$PROJECT_DIR/app" "$INSTALL_DIR/"
    
    # Copy environment example if exists
    if [[ -f "$PROJECT_DIR/.env.example" ]]; then
        cp "$PROJECT_DIR/.env.example" "$INSTALL_DIR/.env.example"
    fi
    
    # Create .env from example if it doesn't exist
    if [[ ! -f "$INSTALL_DIR/.env" ]] && [[ -f "$INSTALL_DIR/.env.example" ]]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        log_warn "Created .env from .env.example - please configure it"
    fi
}

install_service() {
    log_info "Installing systemd service..."
    
    cp "$SCRIPT_DIR/flexibilizador.service" "$SERVICE_FILE"
    systemctl daemon-reload
}

build_image() {
    log_info "Building Docker image..."
    cd "$INSTALL_DIR"
    docker compose build
}

create_network() {
    log_info "Creating Docker network if not exists..."
    docker network create hpc-network 2>/dev/null || true
}

start_service() {
    log_info "Starting service..."
    systemctl start "$SERVICE_NAME"
}

enable_service() {
    log_info "Enabling service for auto-start on boot..."
    systemctl enable "$SERVICE_NAME"
}

check_status() {
    log_info "Checking service status..."
    sleep 5  # Wait for container to start
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_info "Service is running"
        
        # Check health endpoint
        if curl -s http://localhost:8000/health/live | grep -q "ok"; then
            log_info "Health check passed"
        else
            log_warn "Health check not responding yet (may still be starting)"
        fi
    else
        log_error "Service failed to start"
        systemctl status "$SERVICE_NAME" --no-pager
        exit 1
    fi
}

print_summary() {
    echo ""
    echo "============================================================================="
    log_info "Installation complete!"
    echo "============================================================================="
    echo ""
    echo "Installation directory: $INSTALL_DIR"
    echo "Service name: $SERVICE_NAME"
    echo ""
    echo "Useful commands:"
    echo "  sudo systemctl status $SERVICE_NAME    # Check status"
    echo "  sudo systemctl restart $SERVICE_NAME   # Restart service"
    echo "  sudo journalctl -u $SERVICE_NAME -f    # View logs"
    echo "  curl http://localhost:8000/health      # Check health"
    echo ""
    echo "Configuration file: $INSTALL_DIR/.env"
    echo ""
}

# Main execution
main() {
    log_info "Starting Flexibilizador Service installation..."
    
    check_root
    check_docker
    create_install_dir
    copy_files
    install_service
    create_network
    build_image
    enable_service
    start_service
    check_status
    print_summary
}

main "$@"
