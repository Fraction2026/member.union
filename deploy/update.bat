@echo off
REM ============================================================
REM   تحديث نظام الأرشيف الإلكتروني
REM   Update Electronic Archive
REM ============================================================
chcp 65001 >nul
title تحديث نظام الأرشيف

set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

echo.
echo ============================================================
echo  بدء تحديث البرنامج
echo ============================================================
echo.

REM --------- 1. إيقاف الخادم القديم ----------
echo [1/4] إيقاف الخادم القديم ...
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM uvicorn.exe /T >nul 2>&1
timeout /t 2 >nul

REM --------- 2. سحب آخر تحديث من git (لو مستخدم git) ----------
where git >nul 2>&1
if not errorlevel 1 (
    if exist .git (
        echo [2/4] جلب آخر تحديث من Git ...
        git stash >nul 2>&1
        git pull origin main
        git stash pop >nul 2>&1
    )
)

REM --------- 3. تحديث مكتبات Python ----------
echo [3/4] تحديث مكتبات Python ...
cd /d "%APP_DIR%backend"
python -m pip install --upgrade -r requirements.txt

REM --------- 4. إعادة بناء الواجهة ----------
echo [4/4] إعادة بناء واجهة الويب ...
cd /d "%APP_DIR%frontend"
set "REACT_APP_BACKEND_URL="
call yarn install
call yarn build
if errorlevel 1 (
    call npm install
    call npm run build
)

echo.
echo ============================================================
echo  ✅ التحديث اكتمل
echo  لإعادة تشغيل الخادم: شغّل   start_server.bat
echo ============================================================
echo.
pause
