#!/bin/bash
# Install the rawpy-based ARW loader for GIMP 3.2 on macOS.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$HOME/.local/share/gimp-arw"
PLUGIN_DIR="$HOME/Library/Application Support/GIMP/3.2/plug-ins/file-arw-rawpy"
PY="$(brew --prefix python@3.12)/bin/python3.12"

mkdir -p "$HOME_DIR" "$PLUGIN_DIR"

if [ ! -x "$HOME_DIR/venv/bin/python" ]; then
    "$PY" -m venv "$HOME_DIR/venv"
fi
"$HOME_DIR/venv/bin/pip" install -q --upgrade rawpy numpy tifffile

install -m 755 "$SRC/arw2tiff.py" "$HOME_DIR/arw2tiff.py"
install -m 755 "$SRC/file-arw-rawpy.py" "$PLUGIN_DIR/file-arw-rawpy.py"
xattr -dr com.apple.quarantine "$HOME_DIR/arw2tiff.py" "$PLUGIN_DIR" 2>/dev/null || true

# command-line helper: arw2tiff photo.ARW -> photo.tif
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/arw2tiff" <<EOF
#!/bin/bash
exec "$HOME_DIR/venv/bin/python" "$HOME_DIR/arw2tiff.py" "\$@"
EOF
chmod 755 "$HOME/.local/bin/arw2tiff"

echo "Installed. Restart GIMP, then File > Open any .ARW."
echo "CLI: ~/.local/bin/arw2tiff (add ~/.local/bin to PATH if needed)"
