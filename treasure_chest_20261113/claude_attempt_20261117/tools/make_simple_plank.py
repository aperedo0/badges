"""One simple plank. Usage: python make_simple_plank.py OUTDIR NAME L=.. H=.. seed=.. [vis0= vis1= top=1 lip=0 tone=1]"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from maps_common import lin2srgb, to8, to16, write_png  # noqa: E402
from simple_wood import DEPTH, plank_arrays  # noqa: E402

OUT, NAME = sys.argv[1], sys.argv[2]
kw = dict(a.split("=", 1) for a in sys.argv[3:])
H = float(kw["H"])
os.makedirs(OUT, exist_ok=True)
h, col, rough = plank_arrays(float(kw["L"]), H, int(kw.get("seed", 1)), float(kw.get("vis0", 0.0)), float(kw.get("vis1", H)),
                             kw.get("top", "1") == "1", kw.get("lip", "0") == "1", float(kw.get("tone", 1.0)))
write_png(os.path.join(OUT, f"{NAME}_height16.png"), to16(1 + h[::-1] / DEPTH))
write_png(os.path.join(OUT, f"{NAME}_albedo.png"), to8(lin2srgb(col[::-1])))
write_png(os.path.join(OUT, f"{NAME}_rough.png"), to8(rough[::-1]))
print("simple plank", NAME, h.shape)
