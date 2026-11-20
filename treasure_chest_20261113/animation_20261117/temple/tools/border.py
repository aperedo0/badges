"""Diagnostic only, never saved: render just one part of the real picture (real camera, soft focus, grade), to
judge a region at its true pixels without paying for the whole frame.
BORDER="x0,y0,x1,y1" as shares of the picture, y measured from the bottom. The rest of the picture stays empty."""
import bpy, os
spec = os.environ.get("BORDER")
if spec:
    scn = bpy.data.scenes["Chest Reveal"]
    x0, y0, x1, y1 = [float(v) for v in spec.split(",")]
    r = scn.render
    r.use_border = True
    r.use_crop_to_border = False
    r.border_min_x, r.border_min_y, r.border_max_x, r.border_max_y = x0, y0, x1, y1
    print("BORDER", spec)
