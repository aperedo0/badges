"""Convert cached free scans (already downloaded for the chest, CC0) to grayscale .npy for the map generators.
Run: blender -b --python tools/scan_to_npy.py -- OUTDIR name=path ...
"""
import bpy, sys, os, numpy as np
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
for a in args[1:]:
    name, path = a.split("=", 1)
    im = bpy.data.images.load(path); im.colorspace_settings.name = "Non-Color"
    w, h = im.size
    px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)[::-1, :, :3]
    g = px @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    np.save(os.path.join(out, name + ".npy"), g.astype(np.float32))
    gx = np.abs(np.diff(g, axis=1)).mean(); gy = np.abs(np.diff(g, axis=0)).mean()
    print("SCAN", name, w, h, "mean", float(g.mean()), "std", float(g.std()), "grad x", float(gx), "grad y", float(gy))
