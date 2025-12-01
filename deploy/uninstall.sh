#!/bin/bash
# =============================================================================
# Flexibilizador Service Uninstallation Script
# =============================================================================
# Usage: sudo ./uninstall.sh [--purge]
#   --purge: Remove all data and configuration
# =============================================================================

set -euo pipefail

# Configuration
SERVICE_NAME="flexibilizador"
INSTALL_DIR="/opt/flexibilizador-service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Options
PURGE=false

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

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --purge)
                PURGE=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

stop_service() {
    log_info "Stopping service..."
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
        log_info "Service stopped"
    else
        log_info "Service was not running"
    fi
}

disable_service() {
    log_info "Disabling service..."
    
    if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
        systemctl disable "$SERVICE_NAME"
        log_info "Service disabled"
    else
        log_info "Service was not enabled"
    fi
}

remove_containers() {
    log_info "Removing Docker containers..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        cd "$INSTALL_DIR"
        docker compose down --remove-orphans 2>/dev/null || true
        log_info "Containers removed"
    fi
}

remove_images() {
    log_info "Removing Docker images..."
    
    # Remove the service image
    docker rmi flexibilizador-service:2.0.0 2>/dev/null || true
    docker rmi flexibilizador-service:latest 2>/dev/null || true
    
    # Remove dangling images from builds
    docker image prune -f 2>/dev/null || true
    
    log_info "Images removed"
}

remove_service_file() {
    log_info "Removing systemd service file..."
    
    if [[ -f "$SERVICE_FILE" ]]; then
        rm -f "$SERVICE_FILE"
        systemctl daemon-reload
        log_info "Service file removed"
    else
        log_info "Service file not found"
    fi
}

remove_install_dir() {
    if [[ "$PURGE" == true ]]; then
        log_info "Removing installation directory (purge mode)..."
        
        if [[ -d "$INSTALL_DIR" ]]; then
            rm -rf "$INSTALL_DIR"
            log_info "Installation directory removed"
        else
            log_info "Installation directory not found"
        fi
    else
        log_warn "Installation directory preserved at $INSTALL_DIR"
        log_warn "Use --purge to remove all files"
    fi
}

cleanup_temp() {
    log_info "Cleaning up temporary files..."
    rm -rf /tmp/flexibilizador/* 2>/dev/null || true
}

print_summary() {
    echo ""
    echo "============================================================================="
    log_info "Uninstallation complete!"
    echo "============================================================================="
    echo ""
    
    if [[ "$PURGE" == true ]]; then
        echo "All files have been removed."
    else
        echo "Installation directory preserved at: $INSTALL_DIR"
        echo "To remove all files, run: sudo ./uninstall.sh --purge"
    fi
    echo ""
}

# Main execution
main() {
    parse_args "$@"
    
    log_info "Starting Flexibilizador Service uninstallation..."
    
    if [[ "$PURGE" == true ]]; then
        log_warn "PURGE mode enabled - all data will be removed"
    fi
    
    check_root
    stop_service
    disable_service
    remove_containers
    remove_images
    remove_service_file
    remove_install_dir
    cleanup_temp
    print_summary
}

main "$@"
