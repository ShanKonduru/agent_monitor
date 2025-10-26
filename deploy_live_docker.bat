@echo off
echo 🐳 Deploying Live Agent Monitor System on Docker
echo =====================================================

echo.
echo 🛑 Stopping any existing containers...
docker-compose -f docker-compose.production.yml down

echo.
echo 🧹 Cleaning up old images (optional)...
docker system prune -f

echo.
echo 🔨 Building new images...
docker-compose -f docker-compose.production.yml build --no-cache

echo.
echo 🚀 Starting all services...
docker-compose -f docker-compose.production.yml up -d

echo.
echo ⏱️ Waiting for services to be ready...
timeout /t 10

echo.
echo 📊 Checking service status...
docker-compose -f docker-compose.production.yml ps

echo.
echo 🌐 Services should be available at:
echo    📊 Dashboard: http://localhost:8000/static/pulseguard-enterprise-dashboard.html
echo    📡 API Docs: http://localhost:8000/docs
echo    🗄️ Database: localhost:5432
echo.
echo 🔍 To view logs: docker-compose -f docker-compose.production.yml logs -f
echo 🛑 To stop: docker-compose -f docker-compose.production.yml down
echo.
echo ✅ Live Agent Monitor System deployed successfully!
pause