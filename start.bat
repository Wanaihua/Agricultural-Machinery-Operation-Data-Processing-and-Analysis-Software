@echo off
title AMOD Server
cd /d "%~dp0"

echo ========================================
echo   AMOD - Starting...
echo ========================================
echo.
echo [DEBUG] Work dir: %cd%
echo.

if not exist "%cd%\BackEnd\manage.py" (
    echo [ERROR] BackEnd\manage.py not found
    pause
    exit /b 1
)
echo [OK] manage.py found

REM Search Python - use full path to avoid Windows Store stub
set "PY="

REM 1. Conda AMOD env
if exist "D:\ProgramData\Anaconda3\envs\AMOD\python.exe" set "PY=D:\ProgramData\Anaconda3\envs\AMOD\python.exe"
if exist "C:\ProgramData\Anaconda3\envs\AMOD\python.exe" set "PY=C:\ProgramData\Anaconda3\envs\AMOD\python.exe"
if exist "%LOCALAPPDATA%\Anaconda3\envs\AMOD\python.exe" set "PY=%LOCALAPPDATA%\Anaconda3\envs\AMOD\python.exe"
if exist "%USERPROFILE%\Anaconda3\envs\AMOD\python.exe" set "PY=%USERPROFILE%\Anaconda3\envs\AMOD\python.exe"

REM 2. Conda base
if "%PY%"=="" if exist "D:\ProgramData\Anaconda3\python.exe" set "PY=D:\ProgramData\Anaconda3\python.exe"
if "%PY%"=="" if exist "C:\ProgramData\Anaconda3\python.exe" set "PY=C:\ProgramData\Anaconda3\python.exe"
if "%PY%"=="" if exist "%LOCALAPPDATA%\Anaconda3\python.exe" set "PY=%LOCALAPPDATA%\Anaconda3\python.exe"
if "%PY%"=="" if exist "%USERPROFILE%\Anaconda3\python.exe" set "PY=%USERPROFILE%\Anaconda3\python.exe"

REM 3. Common install paths
if "%PY%"=="" if exist "C:\Python314\python.exe" set "PY=C:\Python314\python.exe"
if "%PY%"=="" if exist "C:\Python313\python.exe" set "PY=C:\Python313\python.exe"
if "%PY%"=="" if exist "C:\Python312\python.exe" set "PY=C:\Python312\python.exe"
if "%PY%"=="" if exist "C:\Python311\python.exe" set "PY=C:\Python311\python.exe"
if "%PY%"=="" if exist "C:\Python310\python.exe" set "PY=C:\Python310\python.exe"
if "%PY%"=="" if exist "C:\Python39\python.exe" set "PY=C:\Python39\python.exe"
if "%PY%"=="" if exist "C:\Python3\python.exe" set "PY=C:\Python3\python.exe"
if "%PY%"=="" if exist "D:\Python314\python.exe" set "PY=D:\Python314\python.exe"
if "%PY%"=="" if exist "D:\Python313\python.exe" set "PY=D:\Python313\python.exe"
if "%PY%"=="" if exist "D:\Python312\python.exe" set "PY=D:\Python312\python.exe"
if "%PY%"=="" if exist "D:\Python311\python.exe" set "PY=D:\Python311\python.exe"
if "%PY%"=="" if exist "D:\Python310\python.exe" set "PY=D:\Python310\python.exe"
if "%PY%"=="" if exist "D:\Python39\python.exe" set "PY=D:\Python39\python.exe"

REM 4. System PATH
if "%PY%"=="" (
    where python >nul 2>&1
    if %errorlevel%==0 (
        REM Verify it's not Windows Store stub
        python -c "import sys; print(sys.executable)" >nul 2>&1
        if %errorlevel%==0 set "PY=python"
    )
)

if "%PY%"=="" (
    echo.
    echo ========================================
    echo   ERROR: Python not found!
    echo   Install Python 3.9+ or Anaconda
    echo ========================================
    pause
    exit /b 1
)

echo [OK] Python: %PY%
"%PY%" --version
echo.

echo [1/2] Installing dependencies...
"%PY%" -m pip install -r "%cd%\requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

echo [1.5] Running migrations...
cd /d "%cd%\BackEnd"
"%PY%" manage.py migrate --run-syncdb 2>nul
cd /d "%cd%"
echo.

echo [2/2] Starting Django server...
echo.
echo ========================================
echo   http://127.0.0.1:8000/
echo   Press Ctrl+C to stop
echo ========================================
echo.
cd /d "%cd%\BackEnd"
"%PY%" manage.py runserver 0.0.0.0:8000

echo.
echo Server stopped.
pause
