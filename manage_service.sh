#!/bin/bash

# Set error handling
set -e

# Function to show usage
show_usage() {
    echo "Usage: $0 [start|stop|restart|clean]"
    echo "  start   - Start the services"
    echo "  stop    - Stop the services (preserves data)"
    echo "  restart - Restart the services (preserves data)"
    echo "  clean   - Stop services and remove all data (WARNING: destructive)"
}

# Ensure volume exists
ensure_volume() {
    if ! docker volume ls | grep -q waitlist_postgres_data; then
        echo "Creating persistent volume for PostgreSQL..."
        docker volume create waitlist_postgres_data
    fi
}

# Start services
start_services() {
    ensure_volume
    echo "Starting services..."
    docker-compose up -d
    echo "Services started. Use 'docker-compose logs -f' to view logs"
}

# Stop services
stop_services() {
    echo "Stopping services..."
    docker-compose down
    echo "Services stopped"
}

# Clean everything
clean_services() {
    echo "WARNING: This will remove all data! Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Cleaning up everything..."
        docker-compose down -v
        docker volume rm waitlist_postgres_data || true
        echo "Cleanup complete"
    else
        echo "Operation cancelled"
    fi
}

# Main logic
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        ;;
    clean)
        clean_services
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
