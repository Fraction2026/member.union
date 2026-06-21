# سكريبت تحديث تطبيق الأرشيف الإلكتروني
# Electronic Archive Update Script

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  تحديث تطبيق الأرشيف الإلكتروني" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$APP_PATH = "C:\Users\sameh\AppData\Local\ElectronicArchive"
$BACKUP_PATH = "$APP_PATH`_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# التحقق من وجود المجلد
if (-Not (Test-Path $APP_PATH)) {
    Write-Host "خطأ: المجلد غير موجود: $APP_PATH" -ForegroundColor Red
    Write-Host "Error: Directory not found: $APP_PATH" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "الخطوة 1: إنشاء نسخة احتياطية..." -ForegroundColor Yellow
Write-Host "Step 1: Creating backup..." -ForegroundColor Yellow

# نسخ احتياطي كامل
try {
    Copy-Item -Path $APP_PATH -Destination $BACKUP_PATH -Recurse -Force
    Write-Host "تم إنشاء النسخة الاحتياطية في: $BACKUP_PATH" -ForegroundColor Green
} catch {
    Write-Host "فشل إنشاء النسخة الاحتياطية!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "الخطوة 2: تهيئة Git في المجلد الحالي..." -ForegroundColor Yellow
Write-Host "Step 2: Initializing Git..." -ForegroundColor Yellow

cd $APP_PATH

# التحقق من وجود git
if (-Not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "تحذير: Git غير مثبت على النظام!" -ForegroundColor Red
    Write-Host "قم بتثبيت Git من: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "بعد تثبيت Git، قم بتشغيل هذا السكريبت مرة أخرى" -ForegroundColor Yellow
    pause
    exit 1
}

# تهيئة git إذا لم يكن موجوداً
if (-Not (Test-Path ".git")) {
    git init
    Write-Host "تم تهيئة Git" -ForegroundColor Green
} else {
    Write-Host "Git موجود بالفعل" -ForegroundColor Green
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  الخطوة 3: ربط المستودع بـ GitHub" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "الآن تحتاج إلى إكمال حفظ الكود على GitHub:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. ارجع لواجهة Emergent (المتصفح)" -ForegroundColor White
Write-Host "2. اضغط على زر 'Save to Github'" -ForegroundColor White
Write-Host "3. إذا طلب منك إذن GitHub:" -ForegroundColor White
Write-Host "   - اختر 'All repositories'" -ForegroundColor White
Write-Host "   - اضغط 'Install & Authorize' أو 'Save'" -ForegroundColor White
Write-Host "4. انتظر حتى يظهر لك رابط المستودع (Repository URL)" -ForegroundColor White
Write-Host "5. انسخ الرابط (يبدأ بـ https://github.com/...)" -ForegroundColor White
Write-Host ""
Write-Host "الصق رابط GitHub هنا:" -ForegroundColor Cyan
$GITHUB_URL = Read-Host "GitHub URL"

if ([string]::IsNullOrWhiteSpace($GITHUB_URL)) {
    Write-Host "لم يتم إدخال رابط!" -ForegroundColor Red
    Write-Host "سيتم حفظ الإعدادات للتشغيل لاحقاً" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "لإكمال الربط لاحقاً، قم بتشغيل الأمر التالي في PowerShell:" -ForegroundColor Yellow
    Write-Host "cd '$APP_PATH'" -ForegroundColor White
    Write-Host "git remote add origin <GITHUB_URL>" -ForegroundColor White
    Write-Host "git fetch origin" -ForegroundColor White
    Write-Host "git reset --hard origin/main" -ForegroundColor White
    pause
    exit 0
}

Write-Host ""
Write-Host "الخطوة 4: ربط وتحديث الكود..." -ForegroundColor Yellow

# إزالة remote قديم إن وجد
git remote remove origin 2>$null

# إضافة remote جديد
git remote add origin $GITHUB_URL

# جلب التحديثات
Write-Host "جلب التحديثات من GitHub..." -ForegroundColor Yellow
git fetch origin

# التحقق من الفرع الرئيسي
$MAIN_BRANCH = git remote show origin | Select-String -Pattern "HEAD branch:" | ForEach-Object { $_.ToString().Split(':')[1].Trim() }

if ([string]::IsNullOrWhiteSpace($MAIN_BRANCH)) {
    $MAIN_BRANCH = "main"
}

Write-Host "الفرع الرئيسي: $MAIN_BRANCH" -ForegroundColor Green

# حفظ ملفات مهمة
Write-Host "حفظ الملفات المهمة..." -ForegroundColor Yellow
$TEMP_STORAGE = "$env:TEMP\ElectronicArchive_Storage_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$TEMP_ENV_BACKEND = "$env:TEMP\backend.env"
$TEMP_ENV_FRONTEND = "$env:TEMP\frontend.env"

if (Test-Path "$APP_PATH\backend\storage") {
    Copy-Item -Path "$APP_PATH\backend\storage" -Destination $TEMP_STORAGE -Recurse -Force
}
if (Test-Path "$APP_PATH\backend\.env") {
    Copy-Item -Path "$APP_PATH\backend\.env" -Destination $TEMP_ENV_BACKEND -Force
}
if (Test-Path "$APP_PATH\frontend\.env") {
    Copy-Item -Path "$APP_PATH\frontend\.env" -Destination $TEMP_ENV_FRONTEND -Force
}

# تطبيق التحديثات
Write-Host "تطبيق التحديثات..." -ForegroundColor Yellow
git reset --hard origin/$MAIN_BRANCH

# استعادة الملفات المهمة
Write-Host "استعادة الملفات المهمة..." -ForegroundColor Yellow
if (Test-Path $TEMP_STORAGE) {
    if (Test-Path "$APP_PATH\backend\storage") {
        Remove-Item -Path "$APP_PATH\backend\storage" -Recurse -Force
    }
    Copy-Item -Path $TEMP_STORAGE -Destination "$APP_PATH\backend\storage" -Recurse -Force
    Remove-Item -Path $TEMP_STORAGE -Recurse -Force
}
if (Test-Path $TEMP_ENV_BACKEND) {
    Copy-Item -Path $TEMP_ENV_BACKEND -Destination "$APP_PATH\backend\.env" -Force
    Remove-Item -Path $TEMP_ENV_BACKEND -Force
}
if (Test-Path $TEMP_ENV_FRONTEND) {
    Copy-Item -Path $TEMP_ENV_FRONTEND -Destination "$APP_PATH\frontend\.env" -Force
    Remove-Item -Path $TEMP_ENV_FRONTEND -Force
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "  تم التحديث بنجاح!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "الخطوة 5: إعادة تشغيل التطبيق..." -ForegroundColor Yellow

# البحث عن عمليات Python وإيقافها
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.Path -like "*ElectronicArchive*"} | Stop-Process -Force

# إعادة التشغيل
Start-Sleep -Seconds 2

$BACKEND_PATH = "$APP_PATH\backend"
$PYTHON_EXE = "$APP_PATH\backend\venv\Scripts\pythonw.exe"

if (-Not (Test-Path $PYTHON_EXE)) {
    $PYTHON_EXE = "$APP_PATH\backend\venv\Scripts\python.exe"
}

if (Test-Path $PYTHON_EXE) {
    Start-Process -FilePath $PYTHON_EXE -ArgumentList "$BACKEND_PATH\server.py" -WindowStyle Hidden -WorkingDirectory $BACKEND_PATH
    Write-Host "تم إعادة تشغيل الخادم الخلفي" -ForegroundColor Green
} else {
    Write-Host "تحذير: لم يتم العثور على Python!" -ForegroundColor Yellow
    Write-Host "قد تحتاج لتشغيل التطبيق يدوياً" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "الإصدار الحالي:" -ForegroundColor Cyan
git log -1 --oneline

Write-Host ""
Write-Host "✓ تم التحديث والتشغيل بنجاح" -ForegroundColor Green
Write-Host "✓ النسخة الاحتياطية محفوظة في: $BACKUP_PATH" -ForegroundColor Green
Write-Host ""
Write-Host "لاستخدام هذا السكريبت مستقبلاً للتحديثات:" -ForegroundColor Yellow
Write-Host "قم بتشغيله مباشرة وسيقوم بجلب آخر التحديثات تلقائياً" -ForegroundColor Yellow
Write-Host ""

pause
