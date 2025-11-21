@echo off
cd "G:\Git Project\Warehouse\run.bat"
waitress-serve --host=0.0.0.0 --port=5001
app:app
pause