#!/usr/bin/env python3
#
# copyfigs.py
#
# Copyright The Persistent-1 Contributors.
#
# Persistent-1 Documentation
#
# This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
# International License. To view a copy of this license,
# visit http://creativecommons.org/licenses/by-sa/4.0/.
#

"""Copy the figures referenced by the converted chapters into the repository.

Usage: copyfigs.py SRC_ROOT DST_ROOT MANIFEST

MANIFEST is the figures.json written by tex2rst.py. PDF figures are rendered to
PNG (200 dpi), applying the LaTeX \\includegraphics trim={l b r t} crop if any.
"""
import json, os, shutil, sys
import pymupdf as fitz
src, dst, manifest = sys.argv[1], sys.argv[2], sys.argv[3]
seen = set()
for f in json.load(open(manifest)):
    s = os.path.join(src, f['src']); o = os.path.join(dst, f['out'])
    if o in seen: continue
    seen.add(o)
    os.makedirs(os.path.dirname(o), exist_ok=True)
    if not os.path.exists(s):
        print('MISSING', s); continue
    if f['src'].lower().endswith('.pdf'):
        doc = fitz.open(s); page = doc[0]; r = page.rect
        clip = None
        if f['trim']:
            l, b, rt, t = f['trim']
            clip = fitz.Rect(r.x0 + l, r.y0 + t, r.x1 - rt, r.y1 - b)
        pix = page.get_pixmap(dpi=200, clip=clip, alpha=False)
        pix.save(o)
        print('PDF->PNG', o, pix.width, pix.height)
    else:
        shutil.copy(s, o)
