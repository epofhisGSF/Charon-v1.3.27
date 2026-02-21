# GitHub Deployment Guide for CHARON

This guide shows you how to upload CHARON to GitHub and create releases.

---

## 📦 **Step 1: Create GitHub Repository**

### **1.1 Create New Repository**

1. Go to https://github.com/new
2. Fill in details:
   - **Repository name**: `charon` (or `charon-eve-online`)
   - **Description**: "Wormhole Intelligence System for EVE Online - Track drifter wormholes, calculate routes with jumpbridges, analyze fleet mass"
   - **Visibility**: ✅ **Public** (for open-source transparency)
   - **Initialize**: ❌ Do NOT initialize with README (we have our own)
3. Click **Create repository**

### **1.2 Note Your Repository URL**

You'll get a URL like:
```
https://github.com/YOUR_USERNAME/charon.git
```

---

## 💻 **Step 2: Prepare Local Repository**

### **2.1 Navigate to Your Project**

```bash
cd path/to/drifter-tracker-python
```

### **2.2 Initialize Git**

```bash
git init
git add .
git commit -m "Initial commit - CHARON v1.3.23"
```

### **2.3 Connect to GitHub**

```bash
git remote add origin https://github.com/YOUR_USERNAME/charon.git
git branch -M main
git push -u origin main
```

**Note:** Replace `YOUR_USERNAME` with your actual GitHub username!

---

## 📝 **Step 3: Update README**

### **3.1 Rename GitHub README**

```bash
# Replace the old README with the GitHub version
mv README_GITHUB.md README.md
git add README.md
git commit -m "Add comprehensive README for GitHub"
git push
```

### **3.2 Update URLs in README**

Edit `README.md` and replace all instances of:
- `YOUR_USERNAME` → Your actual GitHub username
- `[Your Name/Corp]` → Your name or corporation
- `[Your Character Name]` → Your EVE character name
- `[Your Alliance Discord]` → Your Discord invite link (optional)

Example:
```markdown
**Created by:** John Doe / Goonswarm Federation
**In-game:** John Doe
**Discord**: https://discord.gg/your-invite
```

---

## 🏗️ **Step 4: Build the EXE**

### **4.1 Build on Windows**

```cmd
# Make sure you're in the project directory
cd path\to\drifter-tracker-python

# Run the build script
build_exe.bat

# The EXE will be in: dist\CHARON.exe
```

### **4.2 Test the EXE**

Before releasing, test the EXE:
1. Copy `CHARON.exe` to a clean folder (without Python installed)
2. Run it
3. Verify all features work:
   - Scanner tab
   - Routing tab (both modes)
   - Mass calculator
   - Check console shows: "✓ Loaded 188 ship types"

---

## 🚀 **Step 5: Create GitHub Release**

### **5.1 Go to Releases**

1. Go to your repository: `https://github.com/YOUR_USERNAME/charon`
2. Click **Releases** (right sidebar)
3. Click **Create a new release**

### **5.2 Fill in Release Details**

**Tag version:** `v1.3.23`

**Release title:** `CHARON v1.3.23 - Jumpbridge Routing & Fleet Mass Calculator`

**Description:**
```markdown
## 🎯 What's New in v1.3.23

### ✅ Features
- **Jumpbridge routing**: 112 Imperium jumpbridges pre-configured
- **Fleet mass calculator**: 188 ships including special editions
- **Advanced routing**: Hybrid gates + wormholes + jumpbridges
- **Progress indicators**: Visual feedback during route calculations

### 🐛 Fixes
- Ship masses load correctly on first startup
- Special edition ships (Metamorphosis, AT prizes) now recognized
- Jumpbridge counts display in routes

---

## 📥 Download & Install

### Windows (Recommended)
1. Download `CHARON.exe` below
2. Run it
3. First-time setup downloads EVE data (~2 minutes)
4. Done!

### Run from Source
See README for Python setup instructions.

---

## 🔒 Security
- 100% open source - inspect the code!
- No telemetry or data collection
- All processing happens locally
- HTTPS-only downloads from official EVE sources

---

## 📖 Documentation
- [README](https://github.com/YOUR_USERNAME/charon/blob/main/README.md) - Full usage guide
- [CHANGELOG](https://github.com/YOUR_USERNAME/charon/blob/main/CHANGELOG.md) - Version history
- [Jumpbridge Configuration](https://github.com/YOUR_USERNAME/charon/blob/main/jumpbridges.py) - Add your alliance JBs

---

**Made with ❤️ for EVE Online**

*Fly safe! o7*
```

### **5.3 Upload the EXE**

1. Drag and drop `CHARON.exe` into the **Attach binaries** section
2. OR click **Attach binaries** → select `dist/CHARON.exe`

**Important:** Rename it to `CHARON-v1.3.23.exe` before uploading for version clarity!

### **5.4 Publish Release**

1. ✅ Check "Set as the latest release"
2. Click **Publish release**

---

## 📂 **Step 6: Repository Organization**

### **6.1 Recommended File Structure**

Your GitHub repo should have:
```
charon/
├── README.md                    # Main documentation
├── LICENSE                      # MIT license
├── CHANGELOG.md                 # Version history
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── drifter_tracker.py          # Main application
├── eve_sde_loader.py           # SDE data loader
├── security_utils.py           # Security functions
├── jumpbridges.py              # JB configuration
├── special_ships.py            # Special ships database
├── jove_systems.py             # Region definitions
├── build_exe.bat               # Windows build script
├── build_exe.sh                # Linux build script
├── build_exe_with_icon.bat     # Icon build script
├── charon.spec                 # PyInstaller spec
├── charon_icon.ico             # App icon
├── charon_icon.png             # Icon preview
├── setup_sde.py                # SDE setup utility
├── run.bat                     # Windows launcher
├── run.sh                      # Linux launcher
├── sde_data/                   # EVE data (auto-downloaded)
│   ├── invTypes.csv
│   └── invGroups.csv
└── docs/                       # Additional documentation
    ├── QUICKSTART.md
    ├── ROUTING_ENHANCEMENTS.md
    ├── ICON_TROUBLESHOOTING.md
    └── SDE_README.md
```

### **6.2 Create Docs Folder (Optional)**

```bash
mkdir docs
mv QUICKSTART.md ROUTING_ENHANCEMENTS.md ICON_TROUBLESHOOTING.md ICON_README.md SDE_README.md docs/
git add docs/
git commit -m "Organize documentation"
git push
```

---

## 🎨 **Step 7: Add Repository Topics**

On your GitHub repository page:

1. Click ⚙️ (gear icon) next to **About**
2. Add topics:
   - `eve-online`
   - `wormhole`
   - `routing`
   - `pyqt6`
   - `python`
   - `gaming`
   - `nullsec`
3. Save changes

---

## 📊 **Step 8: Enable GitHub Features**

### **8.1 Issues**

Keep enabled for bug reports and feature requests.

### **8.2 Wiki (Optional)**

Create a wiki for extended documentation:
- Setup guides
- Troubleshooting
- Advanced configuration
- Developer documentation

### **8.3 Discussions (Optional)**

Enable for community discussions:
- Feature requests
- General questions
- EVE tactics using CHARON

---

## 🔄 **Step 9: Future Updates**

### **When You Release v1.3.24:**

1. **Update code** and test
2. **Update CHANGELOG.md**:
   ```markdown
   ## [1.3.24] - 2026-02-XX
   
   ### Added
   - New feature description
   
   ### Fixed
   - Bug fix description
   ```

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Release v1.3.24 - Feature description"
   git push
   ```

4. **Build new EXE**:
   ```cmd
   build_exe.bat
   ```

5. **Create new release**:
   - Tag: `v1.3.24`
   - Upload new EXE: `CHARON-v1.3.24.exe`

---

## 🛡️ **Security Best Practices**

### **What to Include:**
- ✅ Source code (transparency)
- ✅ README (documentation)
- ✅ LICENSE (MIT)
- ✅ Requirements.txt (dependencies)
- ✅ .gitignore (clean repo)

### **What NOT to Include:**
- ❌ Personal scan data (`scan_data.json`)
- ❌ Settings files (`settings.ini`)
- ❌ API keys or tokens
- ❌ Private alliance information
- ❌ Your character names (unless you want them public)

### **Privacy Note:**

The pre-configured jumpbridges in `jumpbridges.py` are **publicly known** Imperium jumpbridges. If you have:
- **Private JB networks**
- **Secret staging systems**
- **Operational security concerns**

You should:
1. Remove private JBs from `jumpbridges.py` before pushing
2. Add note: "Configure your alliance JBs in jumpbridges.py"
3. Keep private config local only

---

## 📧 **Step 10: Promote Your Release**

### **Where to Share:**

1. **Reddit**:
   - r/Eve
   - r/eveonline
   - Include: "Open source, inspectable code, MIT license"

2. **EVE Forums**:
   - Third-Party Developers section

3. **Discord**:
   - Your alliance/coalition
   - EVE development servers

4. **In-game**:
   - Corp mail
   - Alliance pings

### **Release Announcement Template:**

```
🚀 CHARON v1.3.23 Released - Wormhole Intelligence System

CHARON is an open-source drifter wormhole tracker with:
✅ Advanced routing (gates + wormholes + jumpbridges)
✅ Fleet mass calculator (188 ships)
✅ Imperium JB network pre-configured
✅ 100% local, no telemetry

📥 Download: https://github.com/YOUR_USERNAME/charon/releases/latest
📖 Source: https://github.com/YOUR_USERNAME/charon
🔒 Security: Open source, MIT license, fully inspectable

Made for EVE players, by EVE players. o7
```

---

## ✅ **Checklist Before Release**

- [ ] Code tested and working
- [ ] README.md updated with your info
- [ ] CHANGELOG.md current
- [ ] EXE built and tested
- [ ] Version numbers consistent (code, README, release tag)
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Release created with EXE attached
- [ ] Topics added to repository
- [ ] Private/sensitive data removed

---

## 🆘 **Common Issues**

### **Issue: EXE flagged by antivirus**

**Solution:** This is normal for PyInstaller EXEs. Users can:
1. Whitelist CHARON.exe
2. Run from source code instead
3. Build themselves from source

### **Issue: "This file is not commonly downloaded"**

**Solution:** Windows SmartScreen warning. Users should:
1. Click "More info"
2. Click "Run anyway"
3. This warning decreases as more people download

### **Issue: Large file size warning on GitHub**

**Solution:** EXE is 30-50MB (includes Python runtime). This is normal for PyInstaller apps.

---

## 📞 **Support**

If you need help:
- GitHub Issues (for bugs)
- GitHub Discussions (for questions)
- EVE Discord servers
- Reddit r/Eve

---

**You're ready to ship! 🚀**

*Fly safe! o7*
