"""Palette-quantize PNGs (RGBA kept) and report sizes. Usage: quant.py OUTDIR file.png..."""
import os
import sys
from PIL import Image

outdir = sys.argv[1]
os.makedirs(outdir, exist_ok=True)
tot_in = tot_out = 0
for p in sys.argv[2:]:
    im = Image.open(p).convert("RGBA")
    q = im.quantize(colors=256, method=Image.Quantize.LIBIMAGEQUANT, dither=Image.Dither.FLOYDSTEINBERG)
    dst = os.path.join(outdir, os.path.basename(p))
    q.save(dst, optimize=True)
    a, b = os.path.getsize(p), os.path.getsize(dst)
    tot_in += a; tot_out += b
    print(f"{os.path.basename(p)} {a} -> {b}")
print("total", tot_in, "->", tot_out)
