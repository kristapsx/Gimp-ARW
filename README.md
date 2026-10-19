# Sony ARW loader for GIMP 3.2 (macOS)

`./install.sh` sets up:
- `~/.local/share/gimp-arw/venv` — Python 3.12 + rawpy (LibRaw), numpy, tifffile
- `~/.local/share/gimp-arw/arw2tiff.py` — the decoder
- `~/Library/Application Support/GIMP/3.2/plug-ins/file-arw-rawpy/` — GIMP load plug-in
- `~/.local/bin/arw2tiff` — command-line converter

Restart GIMP, then File → Open (or drag in) any `.ARW`/`.SRF`/`.SR2`. Images open as
16-bit sRGB with camera white balance, no auto-brightening.

## Options
Put extra decoder flags in `~/.local/share/gimp-arw/options`, e.g.

    --linear        # linear gamma, useful for stacking/astro
    --half          # half resolution, fast
    --auto-bright   # let LibRaw brighten the image

## Command line
    arw2tiff *.ARW                 # photo.ARW -> photo.tif
    arw2tiff photo.ARW -o out.tif --linear

## Uninstall
    rm -rf ~/.local/share/gimp-arw ~/.local/bin/arw2tiff \
      "$HOME/Library/Application Support/GIMP/3.2/plug-ins/file-arw-rawpy"
