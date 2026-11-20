"""Diagnostic only, never saved: scale every fog card's strength by FOGX."""
import bpy, os
k = float(os.environ.get("FOGX", "1"))
for o in bpy.data.collections["Temple Fog"].objects:
    c = list(o.color); c[3] *= k; o.color = c
