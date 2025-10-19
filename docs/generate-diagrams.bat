@echo off
echo Generating PulseGuard Mermaid Diagrams...
echo.

echo Generating System Architecture...
npx mmdc -i diagrams\system-architecture.mmd -o images\system-architecture.png -w 1200 -H 800

echo Generating Alert Management...
npx mmdc -i diagrams\alert-management.mmd -o images\alert-management.png -w 1200 -H 800

echo Generating Deployment Architecture...
npx mmdc -i diagrams\deployment-architecture.mmd -o images\deployment-architecture.png -w 1200 -H 800

echo Generating Alert Lifecycle...
npx mmdc -i diagrams\alert-lifecycle.mmd -o images\alert-lifecycle.png -w 1200 -H 800

echo.
echo All diagrams generated successfully!
echo Images saved to: images\
pause