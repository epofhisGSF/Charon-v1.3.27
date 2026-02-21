# CHARON Icon Troubleshooting Guide

## Problem: EXE Shows Default Python Icon

If `CHARON.exe` shows a Python logo instead of the CHARON icon, try these solutions in order:

---

## Solution 1: Use the Direct Build Script (RECOMMENDED)

This method explicitly tells PyInstaller to embed the icon:

```cmd
build_exe_with_icon.bat
```

This script:
- Verifies `charon_icon.ico` exists
- Cleans old builds completely
- Uses `--icon=charon_icon.ico` flag explicitly
- Builds fresh EXE with embedded icon

**After building:**
1. Navigate to `dist/`
2. Right-click `CHARON.exe` → Properties
3. Check if icon shows CHARON symbol

---

## Solution 2: Clear Windows Icon Cache

Windows caches icons and might show old icon even after rebuild.

**Method 1 - Quick (Command Prompt as Admin):**
```cmd
taskkill /f /im explorer.exe
del /f /s /q /a %localappdata%\IconCache.db
del /f /s /q /a %localappdata%\Microsoft\Windows\Explorer\iconcache*
start explorer.exe
```

**Method 2 - Manual:**
1. Close all programs
2. Open Task Manager (Ctrl+Shift+Esc)
3. Find "Windows Explorer" → End task
4. File → Run new task → `cmd`
5. Run:
   ```cmd
   del %localappdata%\IconCache.db /a
   del %localappdata%\Microsoft\Windows\Explorer\iconcache*.db /a
   ```
6. File → Run new task → `explorer.exe`

**Method 3 - Restart:**
```cmd
shutdown /r /t 0
```

---

## Solution 3: Rebuild from Scratch

Sometimes build cache gets corrupted.

```cmd
REM Delete all build artifacts
rmdir /s /q build
rmdir /s /q dist
del CHARON.spec

REM Rebuild fresh
build_exe_with_icon.bat
```

---

## Solution 4: Verify Icon File

Make sure the icon file is valid:

```cmd
REM Check icon exists
dir charon_icon.ico

REM Should show ~30-40 KB file
REM If missing or 0 KB, regenerate it
```

**To regenerate icon:**
```python
python create_icon.py
```
(or extract from the ZIP)

---

## Solution 5: Use PowerShell Fix Script

```powershell
.\fix_icon.ps1
```

This script:
- Verifies all files exist
- Attempts to use ResourceHacker if available
- Falls back to rebuild if needed

---

## Solution 6: Manual PyInstaller Command

If scripts fail, try manual build:

```cmd
pyinstaller --clean --onefile --windowed --icon=charon_icon.ico --name=CHARON drifter_tracker.py
```

---

## Verification Checklist

After building, verify icon in multiple places:

### ✅ Windows Explorer
- Navigate to `dist/`
- Icon should show CHARON symbol (not Python logo)

### ✅ Properties Dialog
- Right-click `CHARON.exe` → Properties
- Icon at top-left should be CHARON symbol

### ✅ Desktop Shortcut
- Create shortcut to `CHARON.exe`
- Shortcut icon should show CHARON symbol

### ✅ Taskbar
- Run `CHARON.exe`
- Taskbar icon should show CHARON symbol

### ✅ Alt+Tab
- Run `CHARON.exe`
- Press Alt+Tab
- CHARON should show correct icon

---

## Common Issues

### Issue: "Icon file not found"
**Solution:** Make sure you're running build from project directory where `charon_icon.ico` exists.

### Issue: Icon shows in Explorer but not taskbar
**Solution:** Windows is caching. Clear icon cache (Solution 2).

### Issue: Multiple icons in EXE
**Solution:** Rebuild from scratch (Solution 3).

### Issue: Build succeeds but still wrong icon
**Solution:** 
1. Check `charon_icon.ico` file size (should be ~30-40 KB)
2. Try different build method (Solution 1 or 6)
3. Clear cache (Solution 2)

---

## Advanced: Check Icon with ResourceHacker

Download ResourceHacker (free): https://www.angusj.com/resourcehacker/

1. Open `dist\CHARON.exe` in ResourceHacker
2. Expand "Icon Group" in left tree
3. Should see "MAINICON" or icon resources
4. If missing → Icon wasn't embedded → Rebuild

---

## Alternative: Post-Build Icon Injection

If PyInstaller completely fails to embed icon:

**Using ResourceHacker:**
```
ResourceHacker.exe -open CHARON.exe -save CHARON_new.exe -action addoverwrite -res charon_icon.ico -mask ICONGROUP,MAINICON,
```

**Using rcedit (Node.js):**
```
npm install -g rcedit
rcedit CHARON.exe --set-icon charon_icon.ico
```

---

## Files Needed

- `charon_icon.ico` - Multi-resolution icon (16,32,48,64,128,256)
- `build_exe_with_icon.bat` - Direct build script
- `fix_icon.ps1` - PowerShell fixer
- `charon.spec` - PyInstaller spec (icon line)

---

## Still Not Working?

If none of these work:

1. **Check PyInstaller version:**
   ```cmd
   pip show pyinstaller
   ```
   Should be 5.0+ (upgrade if older)

2. **Verify Python version:**
   ```cmd
   python --version
   ```
   Should be 3.8+ (3.11 recommended)

3. **Try on different computer:**
   Sometimes Windows permissions/policies block icon embedding

4. **Check antivirus:**
   Some AV software strips icons from executables

5. **Use portable EXE:**
   If all else fails, distribute folder with icon file:
   ```
   CHARON/
     ├── CHARON.exe
     └── charon_icon.ico
   ```

---

**CHARON v1.3.13+**

Icon embedding should work. Follow Solution 1 first. o7 🎨
