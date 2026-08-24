$ErrorActionPreference = "Stop"
Write-Host "1/3 Subindo PostgreSQL e dashboard..."
docker compose up -d postgres dashboard

Write-Host "2/3 Executando ETL..."
docker compose run --rm etl

Write-Host "3/3 Status..."
docker compose ps

Write-Host ""
Write-Host "Dashboard: http://localhost:8501"
Write-Host "Banco: localhost:5432 / bike_sharing"
Write-Host "Para Hop Web (opcional): docker compose --profile hop up -d hop-web"
