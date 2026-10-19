# Sony ARW loader for GIMP 3.2 (macOS / Windows / Linux)

## Install

### macOS
`./install.sh` sets up:
- `~/.local/share/gimp-arw/venv` — Python 3.12 + rawpy (LibRaw), numpy, tifffile
- `~/.local/share/gimp-arw/arw2tiff.py` — the decoder
- `~/Library/Application Support/GIMP/3.2/plug-ins/file-arw-rawpy/` — GIMP load plug-in
- `~/.local/bin/arw2tiff` — command-line converter

### Linux
Needs python3 with venv support (Debian/Ubuntu: `sudo apt install python3-venv`).
`./install.sh` sets up:
- `~/.local/share/gimp-arw/venv` — Python + rawpy (LibRaw), numpy, tifffile
- `~/.local/share/gimp-arw/arw2tiff.py` — the decoder
- `~/.config/GIMP/3.2/plug-ins/file-arw-rawpy/` — GIMP load plug-in
- `~/.local/bin/arw2tiff` — command-line converter

This targets the distro-packaged GIMP. Flatpak/Snap GIMP isn't supported:
their sandbox can't run the external rawpy venv.

### Windows
Needs Python 3.9+ from [python.org](https://www.python.org/downloads/) (Note: GIMP's bundled
Python can't install rawpy). Use this instead:

    powershell -ExecutionPolicy Bypass -File install.ps1

For info this will be set up:
- `%LOCALAPPDATA%\gimp-arw\venv` — Python + rawpy (LibRaw), numpy, tifffile
- `%LOCALAPPDATA%\gimp-arw\arw2tiff.py` — the decoder
- `%APPDATA%\GIMP\3.2\plug-ins\file-arw-rawpy\` — GIMP load plug-in
- `%LOCALAPPDATA%\gimp-arw\bin\arw2tiff.cmd` — command-line converter

File -> Open (or drag in) any `.ARW`/`.SRF`/`.SR2`. Images open as
16-bit sRGB with camera white balance, no auto-brightening.

## Options
Put extra decoder flags in `~/.local/share/gimp-arw/options` (macOS / Linux)
(Windows: `%LOCALAPPDATA%\gimp-arw\options`), e.g.

    --linear        # linear gamma, useful for stacking/astro
    --half          # half resolution, fast
    --auto-bright   # let LibRaw brighten the image

## Command line
    arw2tiff *.ARW                 # photo.ARW -> photo.tif
    arw2tiff photo.ARW -o out.tif --linear

On Windows `cmd` doesn't expand `*.ARW`; list files explicitly or use
`for %f in (*.ARW) do arw2tiff "%f"`.

## Uninstall
macOS:

    rm -rf ~/.local/share/gimp-arw ~/.local/bin/arw2tiff \
      "$HOME/Library/Application Support/GIMP/3.2/plug-ins/file-arw-rawpy"

Linux:

    rm -rf ~/.local/share/gimp-arw ~/.local/bin/arw2tiff \
      ~/.config/GIMP/3.2/plug-ins/file-arw-rawpy

Windows (PowerShell):

    Remove-Item -Recurse "$env:LOCALAPPDATA\gimp-arw", "$env:APPDATA\GIMP\3.2\plug-ins\file-arw-rawpy"
