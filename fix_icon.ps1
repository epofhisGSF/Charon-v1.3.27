# CHARON Icon Fixer
# This script verifies and fixes the icon in CHARON.exe

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CHARON Icon Verification & Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if EXE exists
if (-not (Test-Path "dist\CHARON.exe")) {
    Write-Host "ERROR: dist\CHARON.exe not found!" -ForegroundColor Red
    Write-Host "Build the EXE first using build_exe.bat" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if icon exists
if (-not (Test-Path "charon_icon.ico")) {
    Write-Host "ERROR: charon_icon.ico not found!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Icon file found: charon_icon.ico" -ForegroundColor Green
Write-Host "Executable found: dist\CHARON.exe" -ForegroundColor Green
Write-Host ""

# Try to use ResourceHacker if available (optional)
if (Test-Path "C:\Program Files (x86)\Resource Hacker\ResourceHacker.exe") {
    Write-Host "ResourceHacker found - embedding icon..." -ForegroundColor Yellow
    
    & "C:\Program Files (x86)\Resource Hacker\ResourceHacker.exe" `
        -open "dist\CHARON.exe" `
        -save "dist\CHARON_with_icon.exe" `
        -action addoverwrite `
        -res "charon_icon.ico" `
        -mask ICONGROUP,MAINICON,
    
    if (Test-Path "dist\CHARON_with_icon.exe") {
        Remove-Item "dist\CHARON.exe"
        Rename-Item "dist\CHARON_with_icon.exe" "CHARON.exe"
        Write-Host "Icon embedded successfully!" -ForegroundColor Green
    }
} else {
    Write-Host "ResourceHacker not found (optional tool)" -ForegroundColor Yellow
    Write-Host "Rebuilding with PyInstaller instead..." -ForegroundColor Yellow
    Write-Host ""
    
    # Rebuild using the direct method
    & .\build_exe_with_icon.bat
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Right-click dist\CHARON.exe and select Properties" -ForegroundColor White
Write-Host "The icon should show the CHARON symbol (concentric circles with cross)" -ForegroundColor White
Write-Host ""
Write-Host "If you still see Python icon:" -ForegroundColor Yellow
Write-Host "1. Delete dist\CHARON.exe" -ForegroundColor Yellow
Write-Host "2. Run build_exe_with_icon.bat" -ForegroundColor Yellow
Write-Host "3. Clear Windows icon cache (see ICON_README.md)" -ForegroundColor Yellow
Write-Host ""

pause
