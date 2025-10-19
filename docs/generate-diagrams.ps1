# PulseGuard Mermaid Diagram Generator
Write-Host "Generating PulseGuard Mermaid Diagrams..." -ForegroundColor Green
Write-Host ""

$diagrams = @(
    @{name="System Architecture"; file="system-architecture"},
    @{name="Alert Management"; file="alert-management"},
    @{name="Deployment Architecture"; file="deployment-architecture"},
    @{name="Alert Lifecycle"; file="alert-lifecycle"}
)

foreach ($diagram in $diagrams) {
    Write-Host "Generating $($diagram.name)..." -ForegroundColor Yellow
    npx mmdc -i "diagrams\$($diagram.file).mmd" -o "images\$($diagram.file).png" -w 1200 -H 800
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $($diagram.name) generated successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to generate $($diagram.name)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "All diagrams processed!" -ForegroundColor Green
Write-Host "Images saved to: images\" -ForegroundColor Cyan

# List generated files
Write-Host ""
Write-Host "Generated files:" -ForegroundColor Cyan
Get-ChildItem "images\*.png" | ForEach-Object {
    $size = [math]::Round($_.Length / 1KB, 2)
    Write-Host "  $($_.Name) ($size KB)" -ForegroundColor Gray
}