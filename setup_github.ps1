# سكريبت تحديث تطبيق الأرشيف الإلكتروني - الإعداد الأولي
# Electronic Archive Update Script - Initial Setup

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  إعداد تطبيق الأرشيف الإلكتروني" -ForegroundColor Cyan
Write-Host "  Initial Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$APP_PATH = "C:\Users\sameh\AppData\Local\ElectronicArchive"
$GITHUB_URL = "https://github.com/clonejaimunion/member.union.git"
$BACKUP_PATH = "$APP_PATH`_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# التحقق من وجود المجلد
if (-Not (Test-Path $APP_PATH)) {
    Write-Host "خطأ: المجلد غير موجود: $APP_PATH" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "المجلد: $APP_PATH" -ForegroundColor White
Write-Host "المستودع: $GITHUB_URL" -ForegroundColor White
Write-Host ""

# التحقق من وجود git
Write-Host "التحقق من Git..." -ForegroundColor Yellow
if (-Not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git غير مثبت على النظام!" -ForegroundColor Red
    Write-Host ""
    Write-Host "قم بتثبيت Git من: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "بعد التثبيت، أعد تشغيل PowerShell وشغل السكريبت مرة أخرى" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}
Write-Host "✓ Git موجود" -ForegroundColor Green
Write-Host ""

Write-Host "الخطوة 1/5: إنشاء نسخة احتياطية كاملة..." -ForegroundColor Yellow
try {
    Copy-Item -Path $APP_PATH -Destination $BACKUP_PATH -Recurse -Force
    Write-Host "✓ تم الحفظ في: $BACKUP_PATH" -ForegroundColor Green
} catch {
    Write-Host "❌ فشل إنشاء النسخة الاحتياطية!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "الخطوة 2/5: حفظ البيانات والإعدادات..." -ForegroundColor Yellow

$TEMP_STORAGE = "$env:TEMP\ElectronicArchive_Storage_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$TEMP_ENV_BACKEND = "$env:TEMP\backend_env_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$TEMP_ENV_FRONTEND = "$env:TEMP\frontend_env_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

if (Test-Path "$APP_PATH\backend\storage") {
    Copy-Item -Path "$APP_PATH\backend\storage" -Destination $TEMP_STORAGE -Recurse -Force
    Write-Host "✓ تم حفظ قاعدة البيانات" -ForegroundColor Green
}
if (Test-Path "$APP_PATH\backend\.env") {
    Copy-Item -Path "$APP_PATH\backend\.env" -Destination $TEMP_ENV_BACKEND -Force
    Write-Host "✓ تم حفظ إعدادات Backend" -ForegroundColor Green
}
if (Test-Path "$APP_PATH\frontend\.env") {
    Copy-Item -Path "$APP_PATH\frontend\.env" -Destination $TEMP_ENV_FRONTEND -Force
    Write-Host "✓ تم حفظ إعدادات Frontend" -ForegroundColor Green
}

Write-Host ""
Write-Host "الخطوة 3/5: تهيئة Git والربط بـ GitHub..." -ForegroundColor Yellow

cd $APP_PATH

# تهيئة git
if (-Not (Test-Path ".git")) {
    git init
    Write-Host "✓ تم تهيئة Git" -ForegroundColor Green
} else {
    Write-Host "✓ Git موجود بالفعل" -ForegroundColor Green
}

# إزالة remote قديم وإضافة الجديد
git remote remove origin 2>$null
git remote add origin $GITHUB_URL
Write-Host "✓ تم الربط بـ GitHub" -ForegroundColor Green

Write-Host ""
Write-Host "الخطوة 4/5: جلب آخر التحديثات..." -ForegroundColor Yellow

git fetch origin 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ فشل الاتصال بـ GitHub!" -ForegroundColor Red
    Write-Host "تأكد من اتصالك بالإنترنت" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "لإعادة المحاولة لاحقاً:" -ForegroundColor Yellow
    Write-Host "cd '$APP_PATH'" -ForegroundColor White
    Write-Host "git fetch origin" -ForegroundColor White
    Write-Host "git reset --hard origin/main" -ForegroundColor White
    pause
    exit 1
}

# تحديد الفرع الرئيسي
$MAIN_BRANCH = "main"
$branches = git branch -r
if ($branches -match "origin/master") {
    $MAIN_BRANCH = "master"
}

Write-Host "✓ تم جلب التحديثات من الفرع: $MAIN_BRANCH" -ForegroundColor Green

# تطبيق التحديثات
git reset --hard origin/$MAIN_BRANCH 2>&1 | Out-Null
Write-Host "✓ تم تطبيق التحديثات" -ForegroundColor Green

Write-Host ""
Write-Host "الخطوة 5/5: استعادة البيانات والإعدادات..." -ForegroundColor Yellow

# استعادة الملفات
if (Test-Path $TEMP_STORAGE) {
    if (Test-Path "$APP_PATH\backend\storage") {
        Remove-Item -Path "$APP_PATH\backend\storage" -Recurse -Force
    }
    Copy-Item -Path $TEMP_STORAGE -Destination "$APP_PATH\backend\storage" -Recurse -Force
    Remove-Item -Path $TEMP_STORAGE -Recurse -Force
    Write-Host "✓ تم استعادة قاعدة البيانات" -ForegroundColor Green
}

if (Test-Path $TEMP_ENV_BACKEND) {
    Copy-Item -Path $TEMP_ENV_BACKEND -Destination "$APP_PATH\backend\.env" -Force
    Remove-Item -Path $TEMP_ENV_BACKEND -Force
    Write-Host "✓ تم استعادة إعدادات Backend" -ForegroundColor Green
}

if (Test-Path $TEMP_ENV_FRONTEND) {
    Copy-Item -Path $TEMP_ENV_FRONTEND -Destination "$APP_PATH\frontend\.env" -Force
    Remove-Item -Path $TEMP_ENV_FRONTEND -Force
    Write-Host "✓ تم استعادة إعدادات Frontend" -ForegroundColor Green
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "     ✓ تم التحديث بنجاح!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

Write-Host "إعادة تشغيل التطبيق..." -ForegroundColor Yellow

# إيقاف العمليات القديمة
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.Path -like "*ElectronicArchive*"} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

# إعادة التشغيل
$BACKEND_PATH = "$APP_PATH\backend"
$PYTHON_EXE = "$APP_PATH\backend\venv\Scripts\pythonw.exe"

if (-Not (Test-Path $PYTHON_EXE)) {
    $PYTHON_EXE = "$APP_PATH\backend\venv\Scripts\python.exe"
}

if (Test-Path $PYTHON_EXE) {
    Start-Process -FilePath $PYTHON_EXE -ArgumentList "$BACKEND_PATH\server.py" -WindowStyle Hidden -WorkingDirectory $BACKEND_PATH
    Write-Host "✓ تم إعادة تشغيل التطبيق" -ForegroundColor Green
} else {
    Write-Host "⚠ تحذير: لم يتم العثور على Python" -ForegroundColor Yellow
    Write-Host "قم بتشغيل التطبيق يدوياً" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "الإصدار الحالي:" -ForegroundColor Cyan
git log -1 --pretty=format:"%h - %s (%ar)" 2>$null
Write-Host ""
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✓ النسخة الاحتياطية: $BACKUP_PATH" -ForegroundColor White
Write-Host "✓ رابط المستودع: $GITHUB_URL" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

pause
