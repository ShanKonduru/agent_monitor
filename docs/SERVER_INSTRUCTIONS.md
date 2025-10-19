# PulseGuard™ Documentation Server Commands

## Method 1: PowerShell Background Job (Recommended)

### Start the server:
```powershell
# Stop any existing jobs and start new one
Stop-Job * -ErrorAction SilentlyContinue
Remove-Job * -ErrorAction SilentlyContinue
Start-Job -ScriptBlock { Set-Location "C:\MyProjects\agent_monitor\docs"; python -m http.server 8002 } -Name "HttpServer"
```

### Open the documentation:
```powershell
# Wait for server to start, then open browser
Start-Sleep 3
start chrome "http://localhost:8002/documentation-enhanced.html"
```

### Check server status:
```powershell
Get-Job
```

### Stop the server:
```powershell
Stop-Job HttpServer
Remove-Job HttpServer
```

## Method 2: Separate Terminal Windows

### Terminal 1 (Keep this running):
```powershell
cd C:\MyProjects\agent_monitor\docs
python -m http.server 8002
```

### Terminal 2 (Open browser):
```powershell
start chrome "http://localhost:8002/documentation-enhanced.html"
```

## Method 3: Batch Files

### Double-click: `start-server.bat`
- This starts the HTTP server

### Double-click: `open-docs.bat` 
- This opens the documentation in Chrome
- Make sure the server is running first

## Available URLs

- **Enhanced Documentation**: http://localhost:8002/documentation-enhanced.html
- **Simple Documentation**: http://localhost:8002/simple.html
- **Original Documentation**: http://localhost:8002/documentation.html
- **Markdown File**: http://localhost:8002/PULSEGUARD_COMPREHENSIVE_DOCUMENTATION.md

## Features Available

- ✅ Interactive Mermaid diagrams
- ✅ Image fallbacks (PNG/SVG)
- ✅ Dark/Light theme toggle
- ✅ Search functionality
- ✅ Mobile responsive design
- ✅ Diagram download/fullscreen
- ✅ Smart navigation