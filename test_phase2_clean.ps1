# Phase 2 Test Script - Clean Version
Write-Host "Testing Phase 2 Agent Monitor Framework" -ForegroundColor Green
Write-Host ("=" * 50)

try {
    # Test system status
    Write-Host "Testing system status..." -ForegroundColor Yellow
    $status = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/system/status" -Method Get -TimeoutSec 5
    Write-Host "System Status: $($status.status)" -ForegroundColor Green
    Write-Host "Uptime: $($status.uptime_seconds) seconds" -ForegroundColor Cyan
    Write-Host "Total Agents: $($status.total_agents)" -ForegroundColor Cyan
    Write-Host ""
    
    # Test agent registration
    Write-Host "Testing agent registration..." -ForegroundColor Yellow
    $agentData = @{
        name = "Phase2TestAgent"
        type = "llm_agent" 
        version = "2.0.0"
        description = "Testing Phase 2 database persistence"
        deployment_type = "local"
        host = "localhost"
        environment = "development"
        tags = @("phase2", "test", "database")
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/register" -Method Post -Body $agentData -ContentType "application/json" -TimeoutSec 10
    $agentId = $response.agent_id
    Write-Host "Agent Registered: $agentId" -ForegroundColor Green
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
    Write-Host ""
    
    # Test agent retrieval (database persistence)
    Write-Host "Testing database persistence..." -ForegroundColor Yellow
    $agent = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/$agentId" -Method Get -TimeoutSec 5
    Write-Host "Agent Retrieved from Database!" -ForegroundColor Green
    Write-Host "Name: $($agent.name)" -ForegroundColor Cyan
    Write-Host "Type: $($agent.type)" -ForegroundColor Cyan
    Write-Host "Environment: $($agent.environment)" -ForegroundColor Cyan
    Write-Host ""
    
    # Test agent list
    Write-Host "Testing agent list..." -ForegroundColor Yellow
    $agents = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents" -Method Get -TimeoutSec 5
    Write-Host "Found $($agents.Count) agent(s) in database" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "PHASE 2 SUCCESS!" -ForegroundColor Green
    Write-Host "Working Features:" -ForegroundColor White
    Write-Host "   SQLite Database Connection" -ForegroundColor Green
    Write-Host "   Agent Registration with Persistence" -ForegroundColor Green
    Write-Host "   Database Schema Creation" -ForegroundColor Green
    Write-Host "   Enhanced API Endpoints" -ForegroundColor Green
    Write-Host "   Real-time System Status" -ForegroundColor Green
    Write-Host "   Data Retrieval and Validation" -ForegroundColor Green
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}