docker compose down -v
if (Test-Path ".\dataset\hour.csv") { Remove-Item ".\dataset\hour.csv" }
if (Test-Path ".\dataset\hour_tratado.csv") { Remove-Item ".\dataset\hour_tratado.csv" }
Write-Host "Ambiente resetado. Execute novamente .\start.ps1"
