#!/bin/bash

# ===========================================
# Waitlist Service Management Script
# Purpose: Manage the lifecycle of waitlist service
# Platform: Compatible with Linux and macOS
# ===========================================

# Strict error handling
set -euo pipefail
IFS=$'\n\t'

# Configuration
readonly SERVICE_NAME="waitlist-service"
readonly POSTGRES_VOLUME="waitlist_postgres_data"
readonly LOG_FILE="/tmp/${SERVICE_NAME}.log"

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# ===========================================
# Utility Functions
# ===========================================

log() {
    local level=$1
    shift
    echo -e "${level}[$(date +'%Y-%m-%d %H:%M:%S')] $*${NC}" | tee -a "$LOG_FILE"
}

info() { log "${GREEN}" "$@"; }
warn() { log "${YELLOW}" "$@"; }
error() { log "${RED}" "$@"; }

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Ensure required volumes exist
ensure_volume() {
    if ! docker volume ls | grep -q "$POSTGRES_VOLUME"; then
        info "Creating persistent volume for PostgreSQL..."
        docker volume create "$POSTGRES_VOLUME"
    fi
}

# ===========================================
# Service Management Functions
# ===========================================

start_services() {
    check_docker
    ensure_volume
    info "Starting services..."
    if docker-compose up -d; then
        info "Services started successfully"
        info "Use 'docker-compose logs -f' to view logs"
    else
        error "Failed to start services"
        exit 1
    fi
}

stop_services() {
    check_docker
    info "Stopping services..."
    if docker-compose down; then
        info "Services stopped successfully"
    else
        error "Failed to stop services"
        exit 1
    fi
}

restart_services() {
    info "Restarting services..."
    stop_services
    start_services
}

clean_services() {
    check_docker
    warn "WARNING: This will remove all data. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        info "Cleaning up services and data..."
        docker-compose down -v
        docker volume rm "$POSTGRES_VOLUME" 2>/dev/null || true
        info "Cleanup complete"
    else
        info "Cleanup cancelled"
    fi
}

show_status() {
    check_docker
    info "Service Status:"
    docker-compose ps
    echo
    info "Container Resources:"
    docker stats --no-stream $(docker-compose ps -q)
}

show_usage() {
    cat << EOF
Usage: $0 <command>

Commands:
    start   - Start the services
    stop    - Stop the services (preserves data)
    restart - Restart the services
    status  - Show service status and resource usage
    clean   - Stop services and remove all data (WARNING: destructive)
    help    - Show this help message

Example:
    $0 start    # Start all services
EOF
}

# ===========================================
# Main Execution
# ===========================================

main() {
    # Create log file if it doesn't exist
    touch "$LOG_FILE"

    case "${1:-help}" in
        start)   start_services ;;
        stop)    stop_services ;;
        restart) restart_services ;;
        status)  show_status ;;
        clean)   clean_services ;;
        help)    show_usage ;;
        *)       error "Unknown command: ${1:-}"; show_usage; exit 1 ;;
    esac
}

main "$@"
