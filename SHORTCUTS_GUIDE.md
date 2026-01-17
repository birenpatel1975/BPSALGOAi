# ROBOAi Desktop Shortcuts Guide

## Creating Desktop Shortcuts

ROBOAi provides automated scripts to create desktop shortcuts for easy access to all platform functions.

### Windows

**Run the shortcut creator:**
```batch
create_shortcuts.bat
```

This will create 4 shortcuts on your desktop:
1. **ROBOAi - Start Platform.lnk** - Starts the trading platform (console mode)
2. **ROBOAi - Stop Platform.lnk** - Stops the trading platform
3. **ROBOAi - Dashboard.lnk** - Starts the web dashboard server
4. **ROBOAi - Open Dashboard.url** - Opens http://localhost:5000 in browser

### Linux/Mac

**Run the shortcut creator:**
```bash
./create_shortcuts.sh
```

This will create 4 desktop entries:
1. **roboai-start-platform.desktop** - Starts the trading platform
2. **roboai-stop-platform.desktop** - Stops the trading platform
3. **roboai-dashboard.desktop** - Starts the web dashboard server
4. **roboai-open-dashboard.desktop** - Opens http://localhost:5000 in browser

**Note**: On some Linux systems (Ubuntu/GNOME), you may need to:
- Right-click the desktop file → "Allow Launching" or "Trust"
- Or double-click and select "Trust and Launch"

## Usage Workflow

### Typical Startup Sequence

1. **Start Dashboard** (Recommended first)
   - Double-click "ROBOAi - Dashboard"
   - Wait for server to start
   - Look for "Running on http://0.0.0.0:5000"

2. **Open Dashboard in Browser**
   - Double-click "ROBOAi - Open Dashboard"
   - Or manually open http://localhost:5000

3. **Control from Web UI**
   - Use the web dashboard to start/stop the platform
   - Toggle modes (Paper/Live, Algo/Manual)
   - Monitor everything in real-time

### Alternative: Console Mode

If you prefer console-based operation:

1. **Start Platform**
   - Double-click "ROBOAi - Start Platform"
   - Platform runs in console with detailed logs

2. **Stop Platform**
   - Double-click "ROBOAi - Stop Platform"
   - Or press Ctrl+C in the console

## Shortcut Details

### Windows Shortcuts

#### Start Platform
- **Target**: `start_roboai.bat`
- **Icon**: System process icon
- **Action**: Opens console window and starts trading platform

#### Stop Platform
- **Target**: `stop_roboai.bat`
- **Icon**: Stop icon
- **Action**: Finds and terminates ROBOAi processes

#### Dashboard
- **Target**: `start_dashboard.bat`
- **Icon**: Web/network icon
- **Action**: Starts Flask web server on port 5000

#### Open Dashboard
- **Target**: `http://localhost:5000`
- **Type**: Internet shortcut (.url)
- **Action**: Opens default browser to dashboard

### Linux/Mac Desktop Entries

#### Start Platform
- **Exec**: `x-terminal-emulator -e start_roboai.sh`
- **Icon**: system-run
- **Terminal**: Yes (shows console output)

#### Stop Platform
- **Exec**: `x-terminal-emulator -e stop_roboai.sh`
- **Icon**: process-stop
- **Terminal**: Yes

#### Dashboard
- **Exec**: `x-terminal-emulator -e start_dashboard.sh`
- **Icon**: applications-internet
- **Terminal**: Yes (shows server logs)

#### Open Dashboard
- **Type**: Link (URL)
- **URL**: `http://localhost:5000`
- **Icon**: web-browser

## Customization

### Windows

Edit shortcuts properties:
1. Right-click shortcut → Properties
2. Modify "Target" or "Start in" as needed
3. Change icon via "Change Icon" button

### Linux/Mac

Edit .desktop files:
```bash
nano ~/Desktop/roboai-dashboard.desktop
```

Key fields:
- `Exec`: Command to run
- `Icon`: Icon name or path
- `Terminal`: true/false (show terminal)
- `Path`: Working directory

## Troubleshooting

### Windows

**Shortcuts don't work:**
1. Verify paths in shortcut properties
2. Run `create_shortcuts.bat` again
3. Check if scripts exist in installation directory

**Permission issues:**
- Run as Administrator if needed
- Ensure scripts are not blocked (Properties → Unblock)

### Linux/Mac

**Desktop entries don't appear:**
1. Check Desktop directory exists: `ls ~/Desktop`
2. Verify files are executable: `chmod +x ~/Desktop/roboai-*.desktop`
3. Check system uses XDG desktop entries

**Desktop entries not trusted:**
- Right-click → "Allow Launching" (Ubuntu)
- Or use: `gio set ~/Desktop/roboai-*.desktop "metadata::trusted" yes`

**Terminal emulator not found:**
Edit .desktop file and replace `x-terminal-emulator` with:
- `gnome-terminal -e` (GNOME)
- `konsole -e` (KDE)
- `xfce4-terminal -e` (XFCE)
- `xterm -e` (fallback)

## Manual Shortcut Creation

If automated creation fails, create manually:

### Windows Manual Creation

1. **Right-click Desktop** → New → Shortcut
2. **Browse to**: `C:\path\to\BPSALGOAi\start_dashboard.bat`
3. **Name**: "ROBOAi - Dashboard"
4. **Click Finish**

### Linux Manual Creation

Create file `~/Desktop/roboai-dashboard.desktop`:
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=ROBOAi - Dashboard
Exec=/path/to/BPSALGOAi/start_dashboard.sh
Icon=applications-internet
Terminal=true
```

Make executable:
```bash
chmod +x ~/Desktop/roboai-dashboard.desktop
```

## Best Practices

### Recommended Setup

1. **Create All Shortcuts**: Run create script once after installation
2. **Organize Desktop**: Create a "ROBOAi" folder on desktop
3. **Pin to Taskbar**: Pin frequently used shortcuts (Windows)
4. **Add to Favorites**: Add to application menu (Linux)

### Typical Usage

**For Web Dashboard Users:**
- Use: "Dashboard" + "Open Dashboard" shortcuts
- Control everything from browser

**For Console Users:**
- Use: "Start Platform" + "Stop Platform" shortcuts
- Monitor via console logs

**For Power Users:**
- Use both modes simultaneously
- Dashboard for monitoring, Console for detailed logs

## Icons

The shortcuts use system icons by default:

**Windows:**
- Process/Run: Shell32.dll icon 137
- Stop: Shell32.dll icon 131
- Web: Shell32.dll icon 14

**Linux:**
- Process: `system-run`
- Stop: `process-stop`
- Web: `applications-internet`
- Browser: `web-browser`

To use custom icons:
1. Download/create .ico (Windows) or .png (Linux)
2. Edit shortcut properties
3. Point to custom icon file

## Security Notes

- Shortcuts execute scripts in the installation directory
- Ensure scripts are from trusted source
- Review script contents before first use
- Keep installation directory secure

## Uninstalling Shortcuts

**Windows:**
- Delete .lnk and .url files from Desktop

**Linux/Mac:**
- Delete .desktop files from ~/Desktop
- Or run: `rm ~/Desktop/roboai-*.desktop`

## Updates

When updating ROBOAi:
1. Shortcuts should continue working
2. If paths change, re-run create script
3. Old shortcuts are overwritten automatically

---

**Quick Start**: Run `create_shortcuts.bat` (Windows) or `./create_shortcuts.sh` (Linux) to create all shortcuts!
