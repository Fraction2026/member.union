# تحديث مباشر - جميع الاحتمالات
# Direct Update - All Possibilities

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  تحديث الأرشيف الإلكتروني" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$APP_PATH = "C:\Users\sameh\AppData\Local\ElectronicArchive"

# قائمة الروابط المحتملة
$URLS = @(
    "https://github.com/clonejaimunion/member.union/archive/refs/heads/main.zip",
    "https://github.com/clonejaimunion/member.union/archive/refs/heads/master.zip",
    "https://github.com/clonejaimunion/member.union/archive/main.zip",
    "https://github.com/clonejaimunion/member.union/archive/master.zip"
)

$TEMP_ZIP = "$env:TEMP\update.zip"
$DOWNLOAD_SUCCESS = $false

Write-Host "محاولة التنزيل من GitHub..." -ForegroundColor Yellow

foreach ($URL in $URLS) {
    try {
        Write-Host "جاري المحاولة..." -ForegroundColor Gray
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $URL -OutFile $TEMP_ZIP -UseBasicParsing -ErrorAction Stop
        $DOWNLOAD_SUCCESS = $true
        Write-Host "✓ تم التنزيل بنجاح!" -ForegroundColor Green
        break
    } catch {
        Write-Host "× فشل" -ForegroundColor Red
        continue
    }
}

if (-Not $DOWNLOAD_SUCCESS) {
    Write-Host ""
    Write-Host "════════════════════════════════════" -ForegroundColor Red
    Write-Host "  ⚠ المستودع خاص أو غير متاح" -ForegroundColor Red
    Write-Host "════════════════════════════════════" -ForegroundColor Red
    Write-Host ""
    Write-Host "الحل:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. افتح المستودع على GitHub:" -ForegroundColor White
    Write-Host "   https://github.com/clonejaimunion/member.union" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. اذهب إلى Settings (الإعدادات)" -ForegroundColor White
    Write-Host ""
    Write-Host "3. في قسم 'Danger Zone' اضغط على:" -ForegroundColor White
    Write-Host "   'Change visibility' → اجعله 'Public'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "4. شغل السكريبت مرة أخرى" -ForegroundColor White
    Write-Host ""
    Write-Host "════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "أو" -ForegroundColor Yellow
    Write-Host "════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "حمّل الكود يدوياً:" -ForegroundColor White
    Write-Host ""
    Write-Host "1. افتح: https://github.com/clonejaimunion/member.union" -ForegroundColor Cyan
    Write-Host "2. اضغط الزر الأخضر 'Code'" -ForegroundColor White
    Write-Host "3. اختر 'Download ZIP'" -ForegroundColor White
    Write-Host "4. احفظ الملف في: $env:TEMP\update.zip" -ForegroundColor White
    Write-Host "5. شغل السكريبت مرة أخرى" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "════════════════════════════════════" -ForegroundColor Green
Write-Host "  البدء في التحديث" -ForegroundColor Green
Write-Host "════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# حفظ البيانات
Write-Host "1. حفظ البيانات..." -ForegroundColor Yellow
$BACKUP_STORAGE = "$env:TEMP\storage_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$BACKUP_ENV_B = "$env:TEMP\backend_env_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$BACKUP_ENV_F = "$env:TEMP\frontend_env_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

if (Test-Path "$APP_PATH\backend\storage") {
    Copy-Item "$APP_PATH\backend\storage" $BACKUP_STORAGE -Recurse -Force
    Write-Host "   ✓ قاعدة البيانات" -ForegroundColor Green
}
if (Test-Path "$APP_PATH\backend\.env") {
    Copy-Item "$APP_PATH\backend\.env" $BACKUP_ENV_B -Force
    Write-Host "   ✓ إعدادات Backend" -ForegroundColor Green
}
if (Test-Path "$APP_PATH\frontend\.env") {
    Copy-Item "$APP_PATH\frontend\.env" $BACKUP_ENV_F -Force
    Write-Host "   ✓ إعدادات Frontend" -ForegroundColor Green
}

# فك الضغط
Write-Host ""
Write-Host "2. فك الضغط..." -ForegroundColor Yellow
$TEMP_EXTRACT = "$env:TEMP\EA_Extract_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Expand-Archive -Path $TEMP_ZIP -DestinationPath $TEMP_EXTRACT -Force
Write-Host "   ✓ تم" -ForegroundColor Green

# إيقاف التطبيق
Write-Host ""
Write-Host "3. إيقاف التطبيق..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.Path -like "*ElectronicArchive*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "   ✓ تم" -ForegroundColor Green

# التحديث
Write-Host ""
Write-Host "4. تطبيق التحديث..." -ForegroundColor Yellow
$EXTRACTED = Get-ChildItem -Path $TEMP_EXTRACT -Directory | Select-Object -First 1

if (Test-Path $APP_PATH) {
    Remove-Item $APP_PATH -Recurse -Force
}
Move-Item $EXTRACTED.FullName $APP_PATH -Force
Write-Host "   ✓ تم" -ForegroundColor Green

# استعادة البيانات
Write-Host ""
Write-Host "5. استعادة البيانات..." -ForegroundColor Yellow

if (Test-Path $BACKUP_STORAGE) {
    Copy-Item $BACKUP_STORAGE "$APP_PATH\backend\storage" -Recurse -Force
    Write-Host "   ✓ قاعدة البيانات" -ForegroundColor Green
}
if (Test-Path $BACKUP_ENV_B) {
    Copy-Item $BACKUP_ENV_B "$APP_PATH\backend\.env" -Force
    Write-Host "   ✓ Backend" -ForegroundColor Green
}
if (Test-Path $BACKUP_ENV_F) {
    Copy-Item $BACKUP_ENV_F "$APP_PATH\frontend\.env" -Force
    Write-Host "   ✓ Frontend" -ForegroundColor Green
}

# تنظيف
Remove-Item $TEMP_ZIP -Force -ErrorAction SilentlyContinue
Remove-Item $TEMP_EXTRACT -Recurse -Force -ErrorAction SilentlyContinue

# التشغيل
Write-Host ""
Write-Host "6. تشغيل التطبيق..." -ForegroundColor Yellow
$PY = "$APP_PATH\backend\venv\Scripts\pythonw.exe"
if (-Not (Test-Path $PY)) { $PY = "$APP_PATH\backend\venv\Scripts\python.exe" }

if (Test-Path $PY) {
    Start-Process -FilePath $PY -ArgumentList "$APP_PATH\backend\server.py" -WindowStyle Hidden -WorkingDirectory "$APP_PATH\backend"
    Write-Host "   ✓ تم" -ForegroundColor Green
}

Write-Host ""
Write-Host "════════════════════════════════════" -ForegroundColor Green
Write-Host "      ✓ تم التحديث بنجاح!" -ForegroundColor Green
Write-Host "════════════════════════════════════" -ForegroundColor Green
Write-Host ""

pause
