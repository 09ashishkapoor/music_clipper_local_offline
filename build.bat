@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Song Clipper - Build Script
echo ============================================
echo.

:: Check for Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    if exist "runtime\python\python.exe" (
        set "PYTHON=runtime\python\python.exe"
    ) else (
        echo [ERROR] Python not found. Please install Python 3.8+
        pause
        exit /b 1
    )
) else (
    set "PYTHON=python"
)

:: Install / verify PyInstaller
echo [1/3] Checking PyInstaller...
%PYTHON% -m pip show pyinstaller >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing PyInstaller...
    %PYTHON% -m pip install pyinstaller
)

:: Install app dependencies
echo [2/3] Installing dependencies...
%PYTHON% -m pip install -r requirements.txt

:: Run PyInstaller
echo [3/3] Building executable...
%PYTHON% -m PyInstaller song_clipper.spec --clean --noconfirm

echo.
if %ERRORLEVEL% equ 0 (
    echo ============================================
    echo  BUILD SUCCESSFUL!
    echo  Output: dist\SongClipper\SongClipper.exe
    echo ============================================
    echo.
    echo To distribute, copy the entire dist\SongClipper\ folder.
    echo Users also need FFmpeg in PATH or in tools\ffmpeg\
) else (
    echo [ERROR] Build failed. Check the output above for details.
)

echo.
pause
endlocal
