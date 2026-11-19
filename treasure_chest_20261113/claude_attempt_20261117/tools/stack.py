# blender -b --python tools/stack.py -- out.png a.png b.png ...   (stacks images of equal width, top to bottom)
import bpy, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from maps_common import write_png
args = sys.argv[sys.argv.index("--") + 1:]
rows = []
for p in args[1:]:
    im = bpy.data.images.load(os.path.abspath(p))
    w, h = im.size
    a = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3]
    rows.append(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))
    rows.append(np.full((14, w, 3), 255, np.uint8))
write_png(args[0], np.concatenate(rows[:-1], axis=0))
