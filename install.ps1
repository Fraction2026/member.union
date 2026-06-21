# Electronic Archive - Full Installation Script
# تثبيت كامل للأرشيف الإلكتروني

param(
    [string]$InstallPath = "C:\Users\sameh\AppData\Local\ElectronicArchive"
)

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  تثبيت الأرشيف الإلكتروني" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# GitHub repository info
$REPO = "clonejaimunion/member.union"
$BRANCH = "main"

# Try to download from GitHub
$urls = @(
    "https://github.com/$REPO/archive/refs/heads/main.zip",
    "https://github.com/$REPO/archive/refs/heads/master.zip"
)

$downloaded = $false
$zipFile = "$env:TEMP\member_union.zip"

Write-Host "محاولة التحميل من GitHub..." -ForegroundColor Yellow

foreach ($url in $urls) {
    try {
        Write-Host "  جاري المحاولة: $url" -ForegroundColor Gray
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $zipFile -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
        Write-Host "  ✓ تم التحميل!" -ForegroundColor Green
        $downloaded = $true
        break
    }
    catch {
        Write-Host "  × فشل" -ForegroundColor Red
    }
}

if (-not $downloaded) {
    Write-Host ""
    Write-Host "════════════════════════════════════" -ForegroundColor Red
    Write-Host "  ❌ فشل التحميل من GitHub" -ForegroundColor Red
    Write-Host "════════════════════════════════════" -ForegroundColor Red
    Write-Host ""
    Write-Host "السبب المحتمل:" -ForegroundColor Yellow
    Write-Host "  • المستودع خاص (Private)" -ForegroundColor White
    Write-Host "  • لا يوجد اتصال بالإنترنت" -ForegroundColor White
    Write-Host ""
    Write-Host "الحل:" -ForegroundColor Yellow
    Write-Host "  1. افتح: https://github.com/$REPO/settings" -ForegroundColor Cyan
    Write-Host "  2. في 'Danger Zone' → 'Change visibility' → 'Public'" -ForegroundColor White
    Write-Host "  3. أعد تشغيل هذا السكريبت" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "════════════════════════════════════" -ForegroundColor Green
Write-Host "  بدء التثبيت" -ForegroundColor Green
Write-Host "════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# Backup existing installation
if (Test-Path $InstallPath) {
    Write-Host "1. نسخ احتياطي للبيانات الموجودة..." -ForegroundColor Yellow
    
    $backupPath = "$InstallPath`_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    $tempBackup = "$env:TEMP\ea_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    
    # Backup critical data
    if (Test-Path "$InstallPath\backend\storage") {
        Copy-Item "$InstallPath\backend\storage" "$tempBackup\storage" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ قاعدة البيانات" -ForegroundColor Green
    }
    
    if (Test-Path "$InstallPath\backend\.env") {
        Copy-Item "$InstallPath\backend\.env" "$tempBackup\backend.env" -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ إعدادات Backend" -ForegroundColor Green
    }
    
    if (Test-Path "$InstallPath\frontend\.env") {
        Copy-Item "$InstallPath\frontend\.env" "$tempBackup\frontend.env" -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ إعدادات Frontend" -ForegroundColor Green
    }
    
    # Full backup
    Copy-Item $InstallPath $backupPath -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ نسخة احتياطية كاملة: $backupPath" -ForegroundColor Green
}

# Stop existing processes
Write-Host ""
Write-Host "2. إيقاف العمليات الحالية..." -ForegroundColor Yellow

$pythonProcesses = Get-Process | Where-Object {
    ($_.ProcessName -like "*python*") -and 
    (($_.CommandLine -like "*uvicorn*") -or ($_.CommandLine -like "*ElectronicArchive*"))
}

if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ إيقاف عملية: $($_.Id)" -ForegroundColor Green
    }
}

Start-Sleep -Seconds 2

# Extract files
Write-Host ""
Write-Host "3. استخراج الملفات..." -ForegroundColor Yellow

$extractPath = "$env:TEMP\ea_extract_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

$extractedFolder = Get-ChildItem -Path $extractPath -Directory | Select-Object -First 1

if (-not $extractedFolder) {
    Write-Host "   ❌ فشل الاستخراج!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "   ✓ تم الاستخراج" -ForegroundColor Green

# Remove old installation
if (Test-Path $InstallPath) {
    Write-Host ""
    Write-Host "4. إزالة النسخة القديمة..." -ForegroundColor Yellow
    Remove-Item $InstallPath -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ تم" -ForegroundColor Green
}

# Install new version
Write-Host ""
Write-Host "5. تثبيت النسخة الجديدة..." -ForegroundColor Yellow

Move-Item $extractedFolder.FullName $InstallPath -Force
Write-Host "   ✓ تم التثبيت في: $InstallPath" -ForegroundColor Green

# Restore data
if (Test-Path $tempBackup) {
    Write-Host ""
    Write-Host "6. استعادة البيانات..." -ForegroundColor Yellow
    
    if (Test-Path "$tempBackup\storage") {
        New-Item -Path "$InstallPath\backend" -ItemType Directory -Force -ErrorAction SilentlyContinue | Out-Null
        Copy-Item "$tempBackup\storage" "$InstallPath\backend\storage" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ قاعدة البيانات" -ForegroundColor Green
    }
    
    if (Test-Path "$tempBackup\backend.env") {
        Copy-Item "$tempBackup\backend.env" "$InstallPath\backend\.env" -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ إعدادات Backend" -ForegroundColor Green
    }
    
    if (Test-Path "$tempBackup\frontend.env") {
        New-Item -Path "$InstallPath\frontend" -ItemType Directory -Force -ErrorAction SilentlyContinue | Out-Null
        Copy-Item "$tempBackup\frontend.env" "$InstallPath\frontend\.env" -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ إعدادات Frontend" -ForegroundColor Green
    }
    
    # Clean up temp backup
    Remove-Item $tempBackup -Recurse -Force -ErrorAction SilentlyContinue
}

# Configure for offline use
Write-Host ""
Write-Host "7. إعداد للعمل بدون إنترنت..." -ForegroundColor Yellow

# Set backend to use localhost MongoDB
$backendEnv = "$InstallPath\backend\.env"
if (Test-Path $backendEnv) {
    $envContent = Get-Content $backendEnv -Raw
    if ($envContent -notmatch 'MONGO_URL=') {
        Add-Content $backendEnv "`nMONGO_URL=mongodb://localhost:27017"
        Write-Host "   ✓ إضافة MONGO_URL" -ForegroundColor Green
    }
    elseif ($envContent -match 'MONGO_URL=.*emergent.*|MONGO_URL=.*cloud.*') {
        $envContent = $envContent -replace 'MONGO_URL=.*', 'MONGO_URL=mongodb://localhost:27017'
        Set-Content $backendEnv $envContent
        Write-Host "   ✓ تحديث MONGO_URL للمحلي" -ForegroundColor Green
    }
    
    if ($envContent -notmatch 'DB_NAME=') {
        Add-Content $backendEnv "`nDB_NAME=member_union"
        Write-Host "   ✓ إضافة DB_NAME" -ForegroundColor Green
    }
}
else {
    New-Item -Path $backendEnv -ItemType File -Force | Out-Null
    Set-Content $backendEnv "MONGO_URL=mongodb://localhost:27017`nDB_NAME=member_union"
    Write-Host "   ✓ إنشاء .env جديد" -ForegroundColor Green
}

# Set frontend to use localhost backend
$frontendEnv = "$InstallPath\frontend\.env"
if (-not (Test-Path "$InstallPath\frontend")) {
    New-Item -Path "$InstallPath\frontend" -ItemType Directory -Force | Out-Null
}

$frontendEnvContent = "REACT_APP_BACKEND_URL=http://localhost:8090"
Set-Content $frontendEnv $frontendEnvContent
Write-Host "   ✓ إعداد Frontend" -ForegroundColor Green

# Clean up
Write-Host ""
Write-Host "8. تنظيف..." -ForegroundColor Yellow
Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   ✓ تم" -ForegroundColor Green

# Start application
Write-Host ""
Write-Host "9. تشغيل التطبيق..." -ForegroundColor Yellow

$pythonExe = "C:\Python314\python.exe"
if (-not (Test-Path $pythonExe)) {
    # Try to find python in PATH
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
}

if ($pythonExe -and (Test-Path $pythonExe)) {
    $backendPath = "$InstallPath\backend"
    $startArgs = "-m uvicorn server:app --host 0.0.0.0 --port 8090"
    
    Start-Process -FilePath $pythonExe `
                  -ArgumentList $startArgs `
                  -WindowStyle Hidden `
                  -WorkingDirectory $backendPath
    
    Write-Host "   ✓ تم تشغيل Backend" -ForegroundColor Green
    
    # Wait a moment for server to start
    Start-Sleep -Seconds 3
    
    # Open in browser
    Start-Process "http://localhost:8090"
    Write-Host "   ✓ فتح المتصفح" -ForegroundColor Green
}
else {
    Write-Host "   ⚠ Python غير موجود في: C:\Python314\python.exe" -ForegroundColor Yellow
    Write-Host "   قم بتشغيل Backend يدوياً من: $InstallPath\backend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "════════════════════════════════════" -ForegroundColor Green
Write-Host "      ✓ اكتمل التثبيت!" -ForegroundColor Green
Write-Host "════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "الموقع: $InstallPath" -ForegroundColor White
Write-Host "الرابط: http://localhost:8090" -ForegroundColor Cyan
Write-Host ""
Write-Host "ملاحظة: التطبيق الآن يعمل 100% بدون إنترنت!" -ForegroundColor Green
Write-Host ""

pause
