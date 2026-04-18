@echo off
setlocal

:: Resolve script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check for embedded runtime
if exist "runtime\python\python.exe" (
    set "PYTHON_EXE=runtime\python\python.exe"
) else (
    :: Fallback to system python for development if runtime not yet bundled
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_EXE=python"
        echo [INFO] Local runtime not found. Using system Python.
    ) else (
        echo [ERROR] No Python runtime found. Please ensure runtime\python\ exists.
        pause
        exit /b 1
    )
)

:: Run the app
"%PYTHON_EXE%" app\main.py

if %ERRORLEVEL% neq 0 (
    echo [ERROR] App crashed or failed to start.
    pause
)

endlocal
