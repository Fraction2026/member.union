# سكريبت التحديث السريع - للاستخدام المتكرر
# Quick Update Script - For Regular Updates

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "   تحديث سريع - Quick Update" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$APP_PATH = "C:\Users\sameh\AppData\Local\ElectronicArchive"

if (-Not (Test-Path $APP_PATH)) {
    Write-Host "❌ المجلد غير موجود!" -ForegroundColor Red
    pause
    exit 1
}

cd $APP_PATH

if (-Not (Test-Path ".git")) {
    Write-Host "❌ Git غير مُعد! قم بتشغيل setup_github.ps1 أولاً" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "جلب التحديثات..." -ForegroundColor Yellow

# حفظ البيانات مؤقتاً
$TEMP_STORAGE = "$env:TEMP\EA_Storage_Temp"
$TEMP_ENV_B = "$env:TEMP\ea_backend.env"
$TEMP_ENV_F = "$env:TEMP\ea_frontend.env"

if (Test-Path "backend\storage") {
    Copy-Item "backend\storage" $TEMP_STORAGE -Recurse -Force
}
if (Test-Path "backend\.env") {
    Copy-Item "backend\.env" $TEMP_ENV_B -Force
}
if (Test-Path "frontend\.env") {
    Copy-Item "frontend\.env" $TEMP_ENV_F -Force
}

# التحديث
git fetch origin
git reset --hard origin/main

# استعادة البيانات
if (Test-Path $TEMP_STORAGE) {
    Remove-Item "backend\storage" -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item $TEMP_STORAGE "backend\storage" -Recurse -Force
    Remove-Item $TEMP_STORAGE -Recurse -Force
}
if (Test-Path $TEMP_ENV_B) {
    Copy-Item $TEMP_ENV_B "backend\.env" -Force
    Remove-Item $TEMP_ENV_B -Force
}
if (Test-Path $TEMP_ENV_F) {
    Copy-Item $TEMP_ENV_F "frontend\.env" -Force
    Remove-Item $TEMP_ENV_F -Force
}

Write-Host "✓ تم التحديث" -ForegroundColor Green

# إعادة التشغيل
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.Path -like "*ElectronicArchive*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

$PY = "backend\venv\Scripts\pythonw.exe"
if (-Not (Test-Path $PY)) { $PY = "backend\venv\Scripts\python.exe" }

if (Test-Path $PY) {
    Start-Process -FilePath $PY -ArgumentList "backend\server.py" -WindowStyle Hidden -WorkingDirectory "backend"
    Write-Host "✓ تم إعادة التشغيل" -ForegroundColor Green
}

Write-Host ""
git log -1 --oneline
Write-Host ""
pause
