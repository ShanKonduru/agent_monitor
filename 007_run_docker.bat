@echo off
echo Starting Agent Monitor with Docker...
cd docker
docker-compose up -d
echo Agent Monitor services started. Access at http://localhost:8000