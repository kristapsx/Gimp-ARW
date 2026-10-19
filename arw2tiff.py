#!/usr/bin/env python3
"""Convert Sony ARW (or any LibRaw-supported RAW) to a 16-bit RGB TIFF.

Usage:
    arw2tiff.py INPUT.ARW [-o OUTPUT.tif] [--linear] [--half] [--auto-bright]
    arw2tiff.py INPUT.ARW -o THUMB.jpg --thumb   (embedded preview; prints "W H")
"""
import argparse
import sys
from pathlib import Path

import rawpy
import tifffile


def convert(src, dst, linear=False, half=False, auto_bright=False):
    with rawpy.imread(str(src)) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            output_bps=16,
            no_auto_bright=not auto_bright,
            output_color=rawpy.ColorSpace.sRGB,
            gamma=(1, 1) if linear else (2.222, 4.5),
            half_size=half,
        )
    tifffile.imwrite(str(dst), rgb, photometric="rgb", compression=None)
    return rgb.shape


def extract_thumb(src, dst):
    """Write the embedded JPEG preview; return full image size (w, h)."""
    with rawpy.imread(str(src)) as raw:
        thumb = raw.extract_thumb()
        if thumb.format != rawpy.ThumbFormat.JPEG:
            raise ValueError("no embedded JPEG preview")
        Path(dst).write_bytes(thumb.data)
        return raw.sizes.width, raw.sizes.height


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="+", help="RAW file(s)")
    ap.add_argument("-o", "--output", help="output TIFF (only with a single input)")
    ap.add_argument("--linear", action="store_true", help="linear gamma (for stacking/astro)")
    ap.add_argument("--half", action="store_true", help="half-size, fast")
    ap.add_argument("--auto-bright", action="store_true", help="let LibRaw auto-brighten")
    ap.add_argument("--thumb", action="store_true", help="extract embedded JPEG preview")
    args = ap.parse_args()

    if args.output and len(args.input) > 1:
        ap.error("--output works with a single input only")

    if args.thumb:
        if not args.output:
            ap.error("--thumb needs --output")
        w, h = extract_thumb(args.input[0], args.output)
        print(w, h)
        return 0

    rc = 0
    for src in map(Path, args.input):
        dst = Path(args.output) if args.output else src.with_suffix(".tif")
        try:
            shape = convert(src, dst, args.linear, args.half, args.auto_bright)
            print(f"{src} -> {dst} {shape[1]}x{shape[0]}", file=sys.stderr)
        except Exception as e:
            print(f"{src}: {e}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
