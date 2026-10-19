#!/usr/bin/env python3
# GIMP 3 plug-in: load Sony ARW/SRF/SR2 via rawpy (LibRaw), no darktable needed.
# Decoding runs in an external venv (see install.sh) and comes back as a 16-bit TIFF.

import os
import shlex
import subprocess
import sys
import tempfile

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, GObject, GLib, Gio

HOME = os.path.expanduser('~/.local/share/gimp-arw')
VENV_PY = os.path.join(HOME, 'venv', 'bin', 'python')
CONVERTER = os.path.join(HOME, 'arw2tiff.py')
OPTIONS = os.path.join(HOME, 'options')  # optional extra flags, e.g. "--linear"

LOAD_PROC = 'file-arw-rawpy-load'
THUMB_PROC = 'file-arw-rawpy-load-thumb'


def run_converter(args):
    if not os.path.exists(VENV_PY):
        raise RuntimeError(f'rawpy venv not found at {VENV_PY}; run install.sh')
    proc = subprocess.run([VENV_PY, CONVERTER] + args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f'arw2tiff exited with {proc.returncode}')
    return proc.stdout


def extra_options():
    try:
        with open(OPTIONS) as f:
            return shlex.split(f.read(), comments=True)
    except FileNotFoundError:
        return []


def load_arw(procedure, run_mode, file, metadata, flags, config, data):
    tmpdir = tempfile.mkdtemp(prefix='gimp-arw-')
    tif = os.path.join(tmpdir, 'decoded.tif')
    try:
        Gimp.progress_init(f'Decoding {file.get_basename()}')
        run_converter([file.get_path(), '-o', tif] + extra_options())
        image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(tif))
    except Exception as e:
        return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                           GLib.Error(str(e))), flags
    finally:
        if os.path.exists(tif):
            os.remove(tif)
        os.rmdir(tmpdir)
        Gimp.progress_end()

    return Gimp.ValueArray.new_from_values([
        GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS),
        GObject.Value(Gimp.Image, image),
    ]), flags


def thumbnail_arw(procedure, file, thumb_size, config, data):
    tmpdir = tempfile.mkdtemp(prefix='gimp-arw-')
    jpg = os.path.join(tmpdir, 'thumb.jpg')
    try:
        w, h = map(int, run_converter([file.get_path(), '-o', jpg, '--thumb']).split())
        image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(jpg))
    except Exception as e:
        return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                           GLib.Error(str(e)))
    finally:
        if os.path.exists(jpg):
            os.remove(jpg)
        os.rmdir(tmpdir)

    return Gimp.ValueArray.new_from_values([
        GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS),
        GObject.Value(Gimp.Image, image),
        GObject.Value(GObject.TYPE_INT, w),
        GObject.Value(GObject.TYPE_INT, h),
        GObject.Value(Gimp.ImageType, Gimp.ImageType.RGB_IMAGE),
        GObject.Value(GObject.TYPE_INT, 1),
    ])


class FileArwRawpy(Gimp.PlugIn):
    def do_set_i18n(self, procname):
        return False

    def do_query_procedures(self):
        return [THUMB_PROC, LOAD_PROC]

    def do_create_procedure(self, name):
        if name == LOAD_PROC:
            procedure = Gimp.LoadProcedure.new(self, name, Gimp.PDBProcType.PLUGIN,
                                               load_arw, None)
            procedure.set_menu_label('Sony raw (rawpy)')
            procedure.set_documentation('Load Sony ARW/SRF/SR2 raw files via rawpy/LibRaw',
                                        'Decodes the raw file to 16-bit sRGB with camera white balance.',
                                        name)
            procedure.set_mime_types('image/x-sony-arw,image/x-sony-srf,image/x-sony-sr2')
            procedure.set_extensions('arw,srf,sr2')
            procedure.set_handles_raw(True)
            # lowest priority wins; beat file-raw-placeholder / file-darktable (0)
            procedure.set_priority(-100)
            procedure.set_thumbnail_loader(THUMB_PROC)
        else:
            procedure = Gimp.ThumbnailProcedure.new(self, name, Gimp.PDBProcType.PLUGIN,
                                                    thumbnail_arw, None)
            procedure.set_documentation('Load the embedded preview of a Sony raw file',
                                        'Extracts the embedded JPEG preview via rawpy.',
                                        name)
        procedure.set_attribution('Kristaps Asnins', 'Kristaps Asnins', '2026')
        return procedure


Gimp.main(FileArwRawpy.__gtype__, sys.argv)
