@echo off
echo ========================================
echo CHARON - Building Windows Executable
echo ========================================
echo.

REM Check if pyinstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    echo.
)

REM Verify icon file exists
if not exist charon_icon.ico (
    echo ERROR: charon_icon.ico not found!
    echo Make sure you're running this from the project directory.
    pause
    exit /b 1
)
echo Icon file found: charon_icon.ico
echo.

REM Build the executable
echo Building CHARON.exe...
echo This may take several minutes...
echo.

pyinstaller charon.spec --clean

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED
    echo ========================================
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Your executable is located at:
echo   dist\CHARON.exe
echo.
echo You can distribute this single file!
echo.
echo File size: 
dir dist\CHARON.exe | find "CHARON.exe"
echo.
pause
