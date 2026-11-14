# setup.ps1
# Run this once from the project root to install dependencies and generate datasets.
# Usage: .\setup.ps1

Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "`nGenerating datasets..." -ForegroundColor Cyan
python data/generate_dataset.py

Write-Host "`nSetup complete." -ForegroundColor Green
