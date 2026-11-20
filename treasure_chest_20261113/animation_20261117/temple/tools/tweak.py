"""Diagnostic only, never saved: set light or material numbers for one test render.
TWEAK is a list like "Temple Shaft L.volume_factor=40;Temple Shaft R.energy=0;mat:Temple Air.AIR=0.003"."""
import bpy, os
for item in [x for x in os.environ.get("TWEAK", "").split(";") if x]:
    key, val = item.split("=")
    name, prop = key.rsplit(".", 1)
    o = bpy.data.objects.get(name)
    if o is None:
        print("TWEAK missing", name); continue
    tgt = o.data if hasattr(o.data, prop) else o
    cur = getattr(tgt, prop)
    setattr(tgt, prop, type(cur)(float(val)) if isinstance(cur, (int, float)) else val)
    print("TWEAK", name, prop, getattr(tgt, prop))
