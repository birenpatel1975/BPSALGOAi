#!/bin/bash
# ROBOAi - Create Desktop Shortcuts for Linux

echo "================================================================"
echo "        Creating ROBOAi Desktop Shortcuts"
echo "================================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="$HOME/Desktop"

# Create desktop directory if it doesn't exist
mkdir -p "$DESKTOP_DIR"

echo "Creating shortcuts on desktop..."
echo ""

# Create Start Platform desktop entry
cat > "$DESKTOP_DIR/roboai-start-platform.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ROBOAi - Start Platform
Comment=Start ROBOAi Trading Platform
Exec=x-terminal-emulator -e "$SCRIPT_DIR/start_roboai.sh"
Icon=system-run
Path=$SCRIPT_DIR
Terminal=true
Categories=Office;Finance;
EOF
chmod +x "$DESKTOP_DIR/roboai-start-platform.desktop"
echo "[OK] Created: roboai-start-platform.desktop"

# Create Stop Platform desktop entry
cat > "$DESKTOP_DIR/roboai-stop-platform.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ROBOAi - Stop Platform
Comment=Stop ROBOAi Trading Platform
Exec=x-terminal-emulator -e "$SCRIPT_DIR/stop_roboai.sh"
Icon=process-stop
Path=$SCRIPT_DIR
Terminal=true
Categories=Office;Finance;
EOF
chmod +x "$DESKTOP_DIR/roboai-stop-platform.desktop"
echo "[OK] Created: roboai-stop-platform.desktop"

# Create Start Dashboard desktop entry
cat > "$DESKTOP_DIR/roboai-dashboard.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ROBOAi - Dashboard
Comment=Start ROBOAi Web Dashboard
Exec=x-terminal-emulator -e "$SCRIPT_DIR/start_dashboard.sh"
Icon=applications-internet
Path=$SCRIPT_DIR
Terminal=true
Categories=Office;Finance;Network;
EOF
chmod +x "$DESKTOP_DIR/roboai-dashboard.desktop"
echo "[OK] Created: roboai-dashboard.desktop"

# Create Open Dashboard URL desktop entry
cat > "$DESKTOP_DIR/roboai-open-dashboard.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Link
Name=ROBOAi - Open Dashboard
Comment=Open ROBOAi Web Dashboard in Browser
URL=http://localhost:5000
Icon=web-browser
Categories=Office;Finance;Network;
EOF
chmod +x "$DESKTOP_DIR/roboai-open-dashboard.desktop"
echo "[OK] Created: roboai-open-dashboard.desktop"

# Make all desktop entries trusted (for Ubuntu/GNOME)
if command -v gio &> /dev/null; then
    gio set "$DESKTOP_DIR/roboai-start-platform.desktop" "metadata::trusted" yes 2>/dev/null
    gio set "$DESKTOP_DIR/roboai-stop-platform.desktop" "metadata::trusted" yes 2>/dev/null
    gio set "$DESKTOP_DIR/roboai-dashboard.desktop" "metadata::trusted" yes 2>/dev/null
    gio set "$DESKTOP_DIR/roboai-open-dashboard.desktop" "metadata::trusted" yes 2>/dev/null
fi

echo ""
echo "================================================================"
echo "                   Shortcuts Created!"
echo "================================================================"
echo ""
echo "Desktop shortcuts created in: $DESKTOP_DIR"
echo "   1. roboai-start-platform.desktop"
echo "   2. roboai-stop-platform.desktop"
echo "   3. roboai-dashboard.desktop"
echo "   4. roboai-open-dashboard.desktop"
echo ""
echo "Note: On some systems, you may need to right-click the shortcuts"
echo "      and select 'Allow Launching' or 'Trust' to use them."
echo ""
echo "You can now start/stop the platform from your desktop!"
echo ""
