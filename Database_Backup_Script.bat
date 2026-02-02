@echo off
setlocal enabledelayedexpansion

REM ===== تنظیمات =====
set PG_DUMP=E:\ALLAH\Database\bin\pg_dump.exe
set DB_NAME=Database
set DB_USER=postgres
set DB_PASSWORD=Aass13579
set HOST=localhost
set PORT=5002
set BACKUP_DIR=E:\ALLAH\Backup
set LOG_FILE=E:\ALLAH\Backup\logs.txt
REM =====================

REM تاریخ و ساعت
set DATE=%date:~-4,4%-%date:~-7,2%-%date:~-10,2%
set TIME=%time:~0,2%-%time:~3,2%-%time:~6,2%
if "%TIME:~0,1%"==" " set TIME=0%TIME:~1%

set FILE_NAME=%BACKUP_DIR%\%DB_NAME%_%DATE%_%TIME%.backup

echo ====================================== >> "%LOG_FILE%"
echo Start backup at %DATE% %TIME% >> "%LOG_FILE%"

REM تنظیم متغیر محیطی برای pg_dump
set PGPASSWORD=%DB_PASSWORD%

REM اجرای pg_dump و ثبت خطا در لاگ
%PG_DUMP% -h %HOST% -p %PORT% -U %DB_USER% -F c -f "%FILE_NAME%" %DB_NAME% >> "%LOG_FILE%" 2>&1

IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Backup failed! >> "%LOG_FILE%"
    echo ErrorLevel: %ERRORLEVEL% >> "%LOG_FILE%"
    exit /b %ERRORLEVEL%
)

echo Backup SUCCESSFUL >> "%LOG_FILE%"
echo =============================== >> "%LOG_FILE%"

endlocal