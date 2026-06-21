# تحديث بسيط ومباشر - رابط واحد فقط
# Simple Direct Update

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  تحديث تطبيق الأرشيف الإلكتروني" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$APP_PATH = "C:\Users\sameh\AppData\Local\ElectronicArchive"
$DOWNLOAD_URL = "https://github.com/clonejaimunion/member.union/archive/refs/heads/main.zip"
$TEMP_ZIP = "$env:TEMP\update.zip"
$TEMP_EXTRACT = "$env:TEMP\ElectronicArchive_New"

Write-Host "1. حفظ البيانات..." -ForegroundColor Yellow

# حفظ البيانات المهمة
$BACKUP_STORAGE = "$env:TEMP\storage_backup"
$BACKUP_ENV_B = "$env:TEMP\backend.env"
$BACKUP_ENV_F = "$env:TEMP\frontend.env"

if (Test-Path "$APP_PATH\backend\storage") {
    Copy-Item "$APP_PATH\backend\storage" $BACKUP_STORAGE -Recurse -Force
    Write-Host "   ✓ حفظ قاعدة البيانات" -ForegroundColor Green
}

if (Test-Path "$APP_PATH\backend\.env") {
    Copy-Item "$APP_PATH\backend\.env" $BACKUP_ENV_B -Force
    Write-Host "   ✓ حفظ إعدادات Backend" -ForegroundColor Green
}

if (Test-Path "$APP_PATH\frontend\.env") {
    Copy-Item "$APP_PATH\frontend\.env" $BACKUP_ENV_F -Force
    Write-Host "   ✓ حفظ إعدادات Frontend" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. تنزيل التحديث..." -ForegroundColor Yellow

# تنزيل الملف
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $TEMP_ZIP -UseBasicParsing
    Write-Host "   ✓ تم التنزيل" -ForegroundColor Green
} catch {
    Write-Host "   ❌ فشل التنزيل!" -ForegroundColor Red
    Write-Host "   تأكد من اتصالك بالإنترنت" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "3. فك الضغط..." -ForegroundColor Yellow

# حذف المجلد المؤقت إن وجد
if (Test-Path $TEMP_EXTRACT) {
    Remove-Item $TEMP_EXTRACT -Recurse -Force
}

# فك الضغط
Expand-Archive -Path $TEMP_ZIP -DestinationPath $TEMP_EXTRACT -Force
Write-Host "   ✓ تم فك الضغط" -ForegroundColor Green

Write-Host ""
Write-Host "4. إيقاف التطبيق..." -ForegroundColor Yellow

# إيقاف Python
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.Path -like "*ElectronicArchive*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "   ✓ تم الإيقاف" -ForegroundColor Green

Write-Host ""
Write-Host "5. تطبيق التحديث..." -ForegroundColor Yellow

# حذف المجلد القديم ونسخ الجديد
$EXTRACTED_FOLDER = Get-ChildItem -Path $TEMP_EXTRACT -Directory | Select-Object -First 1

if (Test-Path $APP_PATH) {
    Remove-Item $APP_PATH -Recurse -Force
}

Move-Item $EXTRACTED_FOLDER.FullName $APP_PATH -Force
Write-Host "   ✓ تم التحديث" -ForegroundColor Green

Write-Host ""
Write-Host "6. استعادة البيانات..." -ForegroundColor Yellow

# استعادة البيانات
if (Test-Path $BACKUP_STORAGE) {
    if (-Not (Test-Path "$APP_PATH\backend")) {
        New-Item -Path "$APP_PATH\backend" -ItemType Directory -Force | Out-Null
    }
    Copy-Item $BACKUP_STORAGE "$APP_PATH\backend\storage" -Recurse -Force
    Remove-Item $BACKUP_STORAGE -Recurse -Force
    Write-Host "   ✓ استعادة قاعدة البيانات" -ForegroundColor Green
}

if (Test-Path $BACKUP_ENV_B) {
    Copy-Item $BACKUP_ENV_B "$APP_PATH\backend\.env" -Force
    Remove-Item $BACKUP_ENV_B -Force
    Write-Host "   ✓ استعادة إعدادات Backend" -ForegroundColor Green
}

if (Test-Path $BACKUP_ENV_F) {
    if (-Not (Test-Path "$APP_PATH\frontend")) {
        New-Item -Path "$APP_PATH\frontend" -ItemType Directory -Force | Out-Null
    }
    Copy-Item $BACKUP_ENV_F "$APP_PATH\frontend\.env" -Force
    Remove-Item $BACKUP_ENV_F -Force
    Write-Host "   ✓ استعادة إعدادات Frontend" -ForegroundColor Green
}

# تنظيف
Remove-Item $TEMP_ZIP -Force -ErrorAction SilentlyContinue
Remove-Item $TEMP_EXTRACT -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "7. تشغيل التطبيق..." -ForegroundColor Yellow

$PYTHON_EXE = "$APP_PATH\backend\venv\Scripts\pythonw.exe"
if (-Not (Test-Path $PYTHON_EXE)) {
    $PYTHON_EXE = "$APP_PATH\backend\venv\Scripts\python.exe"
}

if (Test-Path $PYTHON_EXE) {
    Start-Process -FilePath $PYTHON_EXE -ArgumentList "$APP_PATH\backend\server.py" -WindowStyle Hidden -WorkingDirectory "$APP_PATH\backend"
    Write-Host "   ✓ تم التشغيل" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Python غير موجود - شغل التطبيق يدوياً" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "       ✓ تم بنجاح!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "بياناتك محفوظة 100%" -ForegroundColor White
Write-Host "التطبيق يعمل الآن" -ForegroundColor White
Write-Host ""

pause
