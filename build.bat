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
echo [1/4] Checking PyInstaller...
%PYTHON% -m pip show pyinstaller >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing PyInstaller...
    %PYTHON% -m pip install pyinstaller
)

:: Install app dependencies
echo [2/4] Installing dependencies...
%PYTHON% -m pip install -r requirements.txt

:: Run PyInstaller
echo [3/4] Building executable...
%PYTHON% -m PyInstaller song_clipper.spec --clean --noconfirm

if %ERRORLEVEL% neq 0 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  EXE BUILD SUCCESSFUL!
echo  Output: dist\SongClipper\SongClipper.exe
echo ============================================
echo.

:: Optional: Build Inno Setup installer
echo [4/4] Checking for Inno Setup...

:: Check common install locations
set "ISCC="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe"
if exist "%ProgramFiles(x86)%\Inno Setup 6\iscc.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\iscc.exe"
if exist "%ProgramFiles%\Inno Setup 6\iscc.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\iscc.exe"
where iscc >nul 2>nul && set "ISCC=iscc"

if defined ISCC (
    echo Building installer with Inno Setup...
    "%ISCC%" installer.iss
    if not errorlevel 1 (
        echo.
        echo ============================================
        echo  INSTALLER BUILD SUCCESSFUL!
        echo  Output: installer_output\SongClipper-Setup-v2.0.0.exe
        echo ============================================
    ) else (
        echo [WARN] Installer build failed, but EXE is still available.
    )
) else (
    echo [INFO] Inno Setup not found - skipping installer build.
    echo        Install from: https://jrsoftware.org/isinfo.php
    echo        Or via WinGet: winget install JRSoftware.InnoSetup
)

echo.
pause
endlocal
