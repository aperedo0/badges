"""Mockup and render side by side at the same height: python3 side_by_side.py RENDER.png OUT.png [HEIGHT]"""
import sys
from PIL import Image, ImageDraw
REF = "/Users/antonioperedo/Downloads/Ancient stone temple with emerald badge.png"
r = Image.open(sys.argv[1]).convert("RGB")
H = int(sys.argv[3]) if len(sys.argv) > 3 else r.size[1]
a = Image.open(REF).convert("RGB")
a = a.resize((round(a.size[0] * H / a.size[1]), H), Image.LANCZOS)
b = r.resize((round(r.size[0] * H / r.size[1]), H), Image.LANCZOS)
out = Image.new("RGB", (a.size[0] + b.size[0] + 12, H + 30), (20, 20, 20))
out.paste(a, (0, 30)); out.paste(b, (a.size[0] + 12, 30))
d = ImageDraw.Draw(out)
d.text((8, 8), "mockup", fill=(230, 230, 230)); d.text((a.size[0] + 20, 8), "Blender render", fill=(230, 230, 230))
out.save(sys.argv[2])
