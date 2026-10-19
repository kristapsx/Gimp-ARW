#!/bin/bash
# Install the rawpy-based ARW loader for GIMP 3.2 on macOS / Linux (Windows: install.ps1).
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$HOME/.local/share/gimp-arw"

case "$(uname -s)" in
Darwin)
    PLUGIN_DIR="$HOME/Library/Application Support/GIMP/3.2/plug-ins/file-arw-rawpy"
    PY="$(brew --prefix python@3.12)/bin/python3.12"
    ;;
Linux)
    PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/GIMP/3.2/plug-ins/file-arw-rawpy"
    PY=""
    for c in python3.14 python3.13 python3.12 python3; do
        if command -v "$c" >/dev/null &&
            "$c" -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
            PY="$(command -v "$c")"
            break
        fi
    done
    if [ -z "$PY" ]; then
        echo "Python 3.9+ not found; install python3 from your package manager." >&2
        exit 1
    fi
    if [ ! -x "$HOME_DIR/venv/bin/python" ] && ! "$PY" -c 'import venv, ensurepip' 2>/dev/null; then
        echo "$PY can't create virtual environments." >&2
        echo "On Debian/Ubuntu: sudo apt install python3-venv" >&2
        exit 1
    fi
    ;;
*)
    echo "Unsupported OS $(uname -s); on Windows use install.ps1." >&2
    exit 1
    ;;
esac

mkdir -p "$HOME_DIR" "$PLUGIN_DIR"

if [ ! -x "$HOME_DIR/venv/bin/python" ]; then
    "$PY" -m venv "$HOME_DIR/venv"
fi
"$HOME_DIR/venv/bin/pip" install -q --upgrade rawpy numpy tifffile

install -m 755 "$SRC/arw2tiff.py" "$HOME_DIR/arw2tiff.py"
install -m 755 "$SRC/file-arw-rawpy.py" "$PLUGIN_DIR/file-arw-rawpy.py"
if [ "$(uname -s)" = Darwin ]; then
    xattr -dr com.apple.quarantine "$HOME_DIR/arw2tiff.py" "$PLUGIN_DIR" 2>/dev/null || true
fi

# command-line helper: arw2tiff photo.ARW -> photo.tif
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/arw2tiff" <<EOF
#!/bin/bash
exec "$HOME_DIR/venv/bin/python" "$HOME_DIR/arw2tiff.py" "\$@"
EOF
chmod 755 "$HOME/.local/bin/arw2tiff"

echo "Installed. Restart GIMP, then File > Open any .ARW."
echo "CLI: ~/.local/bin/arw2tiff (add ~/.local/bin to PATH if needed)"
