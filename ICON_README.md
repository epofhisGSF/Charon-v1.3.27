# CHARON Icon - Building Guide

## Icon Design

**Theme:** Dark monochrome militaristic  
**Symbol:** ⦰ (Greek ferry symbol - CHARON the ferryman)

**Design Elements:**
- Dark circle background (#0a0a0f)
- Concentric circles (ferry wheel)
- Cross in center (ferryman's pole)
- Accent border (#4a4a55)
- White symbols (#e8e8e8)

## Files

- `charon_icon.png` - 256x256 PNG preview
- `charon_icon.ico` - Multi-resolution Windows icon (16, 32, 48, 64, 128, 256)

## Icon Sizes in ICO

The ICO file contains 6 resolutions:
- 256x256 - Taskbar (Windows 7+), Desktop shortcuts
- 128x128 - Medium icons
- 64x64 - Standard list view
- 48x48 - Classic desktop icons
- 32x32 - Small icons, toolbars
- 16x16 - System tray, file lists

## PyInstaller Integration

The icon is automatically embedded during EXE build:

```python
# charon.spec
exe = EXE(
    ...
    icon=os.path.abspath('charon_icon.ico'),
    ...
)
```

## Building EXE with Icon

### Windows:
```cmd
build_exe.bat
```

### Result:
- `dist/CHARON.exe` with embedded icon
- Icon shows in Windows Explorer
- Icon shows in taskbar
- Icon shows in Alt+Tab
- Icon shows in desktop shortcuts

## Verifying Icon

After building the EXE:

1. **In Windows Explorer:**
   - Navigate to `dist/`
   - Right-click `CHARON.exe` → Properties
   - Icon should show CHARON symbol (not floppy disk)

2. **In Taskbar:**
   - Run `CHARON.exe`
   - Check taskbar - should show CHARON icon

3. **Desktop Shortcut:**
   - Create shortcut to `CHARON.exe`
   - Icon should display correctly

## Troubleshooting

### Icon shows as floppy disk with warning ⚠️

**Cause:** ICO file is corrupted or wrong format

**Fix:**
```bash
# Regenerate the icon
python create_icon.py

# Rebuild EXE
build_exe.bat
```

### Icon doesn't show at all

**Cause:** Path issue in spec file

**Check:**
- `charon_icon.ico` exists in project root
- Path in `charon.spec` is correct
- PyInstaller version is up to date

**Fix:**
```cmd
pip install --upgrade pyinstaller
build_exe.bat --clean
```

### Icon looks pixelated

**Cause:** Missing size in ICO

**Fix:** Icon file already contains all 6 required sizes. If still pixelated, Windows might be caching old icon.

**Clear Windows icon cache:**
```cmd
del %localappdata%\IconCache.db /a
shutdown /r /t 0
```

## Recreating Icon

If you want to regenerate or modify the icon:

```python
from PIL import Image, ImageDraw

# Create your custom design
# See full code in create_icon.py

# Save as multi-resolution ICO
img.save('charon_icon.ico', 
         format='ICO',
         sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])
```

## Icon Preview

The PNG preview can be viewed:
- Open `charon_icon.png` in any image viewer
- Shows full 256x256 resolution
- Transparent background

---

**CHARON v1.3.12+**

Professional icon. Windows-compatible. Looks sharp at all sizes. o7 🎨
