#!/bin/bash

# Docker Production Deployment Script
# This script helps deploy the Agent Monitor Framework in various scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Agent Monitor - Docker Deploy${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

show_help() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    dev             Start development environment (basic setup)
    prod            Start production environment (full agent fleet)
    scale           Scale production agents up/down
    stop            Stop all containers
    clean           Stop and remove all containers and volumes
    logs            Show logs for specific service
    status          Show status of all services
    dashboard       Open monitoring dashboard
    help            Show this help message

Options:
    --replicas N    Number of replicas for scaling (default: 2)
    --service NAME  Specific service name for logs/status

Examples:
    $0 dev                          # Start development environment
    $0 prod                         # Start production with full agent fleet
    $0 scale --replicas 3           # Scale to 3 replicas
    $0 logs --service llm-agent-1   # Show logs for LLM agent
    $0 status                       # Show all service status
    $0 clean                        # Clean everything

EOF
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_success "Docker is available"
}

start_development() {
    print_info "Starting development environment..."
    
    docker-compose -f docker/docker-compose.yml up -d --build
    
    print_success "Development environment started!"
    print_info "Services:"
    print_info "  - Monitor API: http://localhost:8000"
    print_info "  - Dashboard: http://localhost:8000/dashboard"
    print_info "  - PostgreSQL: localhost:5432"
    print_info "  - Redis: localhost:6379"
    print_info "  - InfluxDB: http://localhost:8086"
    print_info "  - Grafana: http://localhost:3000 (admin/admin)"
}

start_production() {
    print_info "Starting production environment with agent fleet..."
    
    # Check if we need to build images
    if ! docker images | grep -q "agent_monitor"; then
        print_info "Building images..."
        docker-compose -f docker/docker-compose-production.yml build
    fi
    
    docker-compose -f docker/docker-compose-production.yml up -d
    
    print_success "Production environment started!"
    print_info "Services:"
    print_info "  - Monitor API: http://localhost:8000"
    print_info "  - Dashboard: http://localhost:80 (via nginx)"
    print_info "  - Grafana: http://localhost:80/grafana (admin/admin)"
    print_info ""
    print_info "Agents deployed:"
    print_info "  - 2x LLM Agents (GPT-4, Claude)"
    print_info "  - 2x API Agents (Gateway, Auth Service)"
    print_info "  - 2x Data Agents (ETL Pipeline, Analytics)"
    print_info "  - 1x Monitor Agent (System Monitor)"
    print_info ""
    print_warning "Wait 30-60 seconds for all agents to register..."
}

scale_agents() {
    local replicas=${1:-2}
    print_info "Scaling production agents to $replicas replicas..."
    
    docker-compose -f docker/docker-compose-production.yml up -d --scale api-agent-1=$replicas --scale llm-agent-1=$replicas
    
    print_success "Scaled agents to $replicas replicas"
}

stop_all() {
    print_info "Stopping all containers..."
    
    docker-compose -f docker/docker-compose.yml down 2>/dev/null || true
    docker-compose -f docker/docker-compose-production.yml down 2>/dev/null || true
    
    print_success "All containers stopped"
}

clean_all() {
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        
        docker-compose -f docker/docker-compose.yml down -v --remove-orphans 2>/dev/null || true
        docker-compose -f docker/docker-compose-production.yml down -v --remove-orphans 2>/dev/null || true
        
        print_success "Cleanup complete"
    else
        print_info "Cleanup cancelled"
    fi
}

show_logs() {
    local service=${1:-""}
    
    if [ -n "$service" ]; then
        print_info "Showing logs for $service..."
        
        # Try production first, then development
        if docker-compose -f docker/docker-compose-production.yml ps | grep -q "$service"; then
            docker-compose -f docker/docker-compose-production.yml logs -f "$service"
        elif docker-compose -f docker/docker-compose.yml ps | grep -q "$service"; then
            docker-compose -f docker/docker-compose.yml logs -f "$service"
        else
            print_error "Service '$service' not found"
            exit 1
        fi
    else
        print_info "Available services:"
        docker-compose -f docker/docker-compose-production.yml ps --services 2>/dev/null || \
        docker-compose -f docker/docker-compose.yml ps --services 2>/dev/null || \
        print_error "No running services found"
    fi
}

show_status() {
    print_info "Service Status:"
    echo
    
    # Check production first
    if docker-compose -f docker/docker-compose-production.yml ps 2>/dev/null | grep -q "Up"; then
        print_info "Production Environment:"
        docker-compose -f docker/docker-compose-production.yml ps
    elif docker-compose -f docker/docker-compose.yml ps 2>/dev/null | grep -q "Up"; then
        print_info "Development Environment:"
        docker-compose -f docker/docker-compose.yml ps
    else
        print_warning "No services are currently running"
        print_info "Use '$0 dev' or '$0 prod' to start services"
    fi
}

open_dashboard() {
    print_info "Opening monitoring dashboard..."
    
    # Check which environment is running
    if docker-compose -f docker/docker-compose-production.yml ps 2>/dev/null | grep -q "nginx.*Up"; then
        print_info "Production dashboard: http://localhost/"
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost/"
        elif command -v open &> /dev/null; then
            open "http://localhost/"
        fi
    elif docker-compose -f docker/docker-compose.yml ps 2>/dev/null | grep -q "monitor.*Up"; then
        print_info "Development dashboard: http://localhost:8000/"
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:8000/"
        elif command -v open &> /dev/null; then
            open "http://localhost:8000/"
        fi
    else
        print_warning "No monitoring services are running"
        print_info "Start with '$0 dev' or '$0 prod' first"
    fi
}

# Main script logic
print_header
check_docker

case "${1:-help}" in
    "dev")
        start_development
        ;;
    "prod")
        start_production
        ;;
    "scale")
        replicas=2
        if [ "$2" = "--replicas" ] && [ -n "$3" ]; then
            replicas=$3
        fi
        scale_agents $replicas
        ;;
    "stop")
        stop_all
        ;;
    "clean")
        clean_all
        ;;
    "logs")
        service=""
        if [ "$2" = "--service" ] && [ -n "$3" ]; then
            service=$3
        fi
        show_logs $service
        ;;
    "status")
        show_status
        ;;
    "dashboard")
        open_dashboard
        ;;
    "help"|*)
        show_help
        ;;
esac