@echo off
set PGPASSWORD=Aass13579
set BACKUP_DIR=M:\Database
set DB_NAME=Database
set USER=postgres
set DATE=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%

D:\ALLAH\Postgresql\bin\pg_dump.exe -U %USER% -F c -b -v -f "%BACKUP_DIR%\%DB_NAME%-%DATE%.backup" %DB_NAME%