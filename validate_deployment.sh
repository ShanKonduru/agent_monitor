#!/bin/bash
# validate_deployment.sh - Validate Agent Monitor deployment

set -e

echo "🔍 Agent Monitor Deployment Validation"
echo "======================================"

# Configuration
MONITOR_PORT=${MONITOR_PORT:-8000}
DB_PORT=${DB_PORT:-5432}
HOST=${HOST:-localhost}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "ℹ️  $1"
}

# Check if Docker is running
check_docker() {
    info "Checking Docker..."
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running or not accessible"
        exit 1
    fi
    success "Docker is running"
}

# Check if containers are running
check_containers() {
    info "Checking containers..."
    
    # Get running containers
    CONTAINERS=$(docker-compose -f docker-compose.production.yml ps --services --filter "status=running" 2>/dev/null || echo "")
    
    if echo "$CONTAINERS" | grep -q "postgres"; then
        success "PostgreSQL container is running"
    else
        error "PostgreSQL container is not running"
        return 1
    fi
    
    if echo "$CONTAINERS" | grep -q "monitor-dashboard"; then
        success "Monitor dashboard container is running"
    else
        error "Monitor dashboard container is not running"
        return 1
    fi
    
    if echo "$CONTAINERS" | grep -q "container-agent"; then
        success "Agent containers are running"
    else
        warning "No agent containers detected"
    fi
}

# Check database connectivity
check_database() {
    info "Checking database connectivity..."
    
    if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U agent_monitor -d agent_monitor >/dev/null 2>&1; then
        success "Database is accessible"
        
        # Check if tables exist
        TABLE_COUNT=$(docker-compose -f docker-compose.production.yml exec -T postgres psql -U agent_monitor -d agent_monitor -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' \n' || echo "0")
        
        if [ "$TABLE_COUNT" -gt 0 ]; then
            success "Database tables exist (count: $TABLE_COUNT)"
        else
            warning "Database tables not found - may need initialization"
        fi
    else
        error "Database is not accessible"
        return 1
    fi
}

# Check API endpoints
check_api() {
    info "Checking API endpoints..."
    
    # Wait for service to be ready
    sleep 5
    
    # System status endpoint
    if curl -f -s "http://$HOST:$MONITOR_PORT/api/v1/system/status" >/dev/null 2>&1; then
        success "System status endpoint is responsive"
    else
        error "System status endpoint failed"
        return 1
    fi
    
    # Health check endpoint
    if curl -f -s "http://$HOST:$MONITOR_PORT/health" >/dev/null 2>&1; then
        success "Health check endpoint is responsive"
    else
        warning "Health check endpoint failed"
    fi
    
    # Dashboard endpoint
    if curl -f -s "http://$HOST:$MONITOR_PORT/" >/dev/null 2>&1; then
        success "Dashboard is accessible"
    else
        error "Dashboard is not accessible"
        return 1
    fi
}

# Check agent registration
check_agents() {
    info "Checking agent registration..."
    
    AGENT_COUNT=$(curl -s "http://$HOST:$MONITOR_PORT/api/v1/agents/" 2>/dev/null | jq length 2>/dev/null || echo "0")
    
    if [ "$AGENT_COUNT" -gt 0 ]; then
        success "Agents registered (count: $AGENT_COUNT)"
    else
        warning "No agents registered yet"
    fi
}

# Check system resources
check_resources() {
    info "Checking system resources..."
    
    # Memory usage
    MEMORY_USAGE=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep agent_monitor || echo "")
    
    if [ -n "$MEMORY_USAGE" ]; then
        success "Container resource usage:"
        echo "$MEMORY_USAGE"
    else
        warning "Could not retrieve resource usage"
    fi
}

# Get service information
get_service_info() {
    info "Service Information:"
    echo "===================="
    echo "🌐 Dashboard: http://$HOST:$MONITOR_PORT"
    echo "📚 API Docs: http://$HOST:$MONITOR_PORT/docs"
    echo "🗃️  Admin: http://$HOST:$MONITOR_PORT/admin"
    echo "🔍 Health: http://$HOST:$MONITOR_PORT/health"
    echo ""
    
    # Container status
    echo "📦 Container Status:"
    docker-compose -f docker-compose.production.yml ps 2>/dev/null || echo "Could not retrieve container status"
    echo ""
}

# Show logs if there are issues
show_logs_on_failure() {
    if [ $? -ne 0 ]; then
        error "Deployment validation failed!"
        echo ""
        info "Recent logs from monitor-dashboard:"
        docker-compose -f docker-compose.production.yml logs --tail=20 monitor-dashboard 2>/dev/null || echo "Could not retrieve logs"
        echo ""
        info "To view full logs run:"
        echo "docker-compose -f docker-compose.production.yml logs -f"
        exit 1
    fi
}

# Main validation sequence
main() {
    echo "Starting validation at $(date)"
    echo ""
    
    check_docker
    check_containers || show_logs_on_failure
    check_database || show_logs_on_failure
    check_api || show_logs_on_failure
    check_agents
    check_resources
    
    echo ""
    success "🎉 Deployment validation completed successfully!"
    echo ""
    
    get_service_info
}

# Run validation
main "$@"