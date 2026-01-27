@echo off
REM Auto-freeze script untuk Windows Command Prompt
REM Cara pakai: scripts\install.bat package-name
REM Contoh: scripts\install.bat requests

if "%~1"=="" (
    echo Error: Package name required!
    echo Usage: scripts\install.bat package-name
    exit /b 1
)

echo Installing package: %*
pip install %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Installation successful! Updating requirements.txt...
    pip freeze > requirements.txt
    echo requirements.txt has been updated!
) else (
    echo.
    echo Installation failed! requirements.txt not updated.
    exit /b 1
)
