@echo off
echo ========================================
echo CHARON - Building with Icon (Direct)
echo ========================================
echo.

REM Verify icon exists
if not exist charon_icon.ico (
    echo ERROR: charon_icon.ico not found!
    pause
    exit /b 1
)

REM Clean old builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build directly with PyInstaller command line (icon embedded)
echo Building CHARON.exe with embedded icon...
echo.

pyinstaller ^
    --name=CHARON ^
    --onefile ^
    --windowed ^
    --icon=charon_icon.ico ^
    --add-data "eve_sde_loader.py;." ^
    --add-data "jove_systems.py;." ^
    --add-data "security_utils.py;." ^
    --add-data "sde_data;sde_data" ^
    --add-data "README.md;." ^
    --add-data "QUICKSTART.md;." ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=requests ^
    --hidden-import=zipfile ^
    --hidden-import=csv ^
    --clean ^
    drifter_tracker.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Executable: dist\CHARON.exe
echo Icon should be embedded in the EXE.
echo.
echo Right-click CHARON.exe and check Properties
echo to verify the icon is showing correctly.
echo.
pause
