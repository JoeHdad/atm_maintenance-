Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ATM Maintenance System - Production Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BACKEND_DIR = ".\backend"
$FRONTEND_DIR = ".\frontend\atm_frontend"

Write-Host "[1/4] Verifying directories..." -ForegroundColor Yellow
if (-not (Test-Path $BACKEND_DIR)) { exit 1 }
if (-not (Test-Path $FRONTEND_DIR)) { exit 1 }
Write-Host "[OK] Directories verified" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] Building React frontend..." -ForegroundColor Yellow
Push-Location $FRONTEND_DIR
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
npm install
npm run build
if (-not (Test-Path "build")) { Pop-Location; exit 1 }
Write-Host "[OK] React build complete" -ForegroundColor Green
Pop-Location
Write-Host ""

Write-Host "[3/4] Collecting Django static files..." -ForegroundColor Yellow
Push-Location $BACKEND_DIR
if (Test-Path "staticfiles") { Remove-Item -Recurse -Force "staticfiles" }
python manage.py collectstatic --noinput --clear
if (-not (Test-Path "staticfiles")) { Pop-Location; exit 1 }
Write-Host "[OK] Static files collected" -ForegroundColor Green
Pop-Location
Write-Host ""

Write-Host "[4/4] Packaging media files..." -ForegroundColor Yellow
$mediaPath = "$BACKEND_DIR\media"
if (Test-Path $mediaPath) {
    if (Test-Path "media.zip") { Remove-Item "media.zip" -Force }
    Compress-Archive -Path "$mediaPath\*" -DestinationPath "media.zip" -Force
    Write-Host "[OK] Media packaged" -ForegroundColor Green
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRODUCTION BUILD COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files ready:" -ForegroundColor Green
Write-Host "  - frontend/atm_frontend/build/" -ForegroundColor Green
Write-Host "  - backend/staticfiles/" -ForegroundColor Green
Write-Host "  - media.zip" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. git add . && git commit -m 'Production build ready' && git push" -ForegroundColor Yellow
Write-Host "  2. Render auto-deploys" -ForegroundColor Yellow
Write-Host "  3. Upload build/ to Hostinger /public_html/" -ForegroundColor Yellow
Write-Host "  4. Extract media.zip to Hostinger /public_html/media/" -ForegroundColor Yellow
Write-Host ""
