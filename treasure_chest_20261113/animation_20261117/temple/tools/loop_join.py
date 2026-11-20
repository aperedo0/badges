"""Blend the extra frames into the start so the ending repeats without a jump, then write the loop's frames.
    python3 loop_join.py IN_FOLDER OUT_FOLDER LOOP FADE"""
import sys, os
from PIL import Image
src, dst, LOOP, FADE = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
os.makedirs(dst, exist_ok=True)
for i in range(LOOP):
    a = Image.open(os.path.join(src, f"{i:04d}.png")).convert("RGB")
    if i < FADE:
        b = Image.open(os.path.join(src, f"{LOOP + i:04d}.png")).convert("RGB")       # the take carrying on past the loop's end
        t = (i + 0.5) / FADE
        t = t * t * (3 - 2 * t)
        a = Image.blend(b, a, t)
    a.save(os.path.join(dst, f"{i:04d}.png"))
print("joined", LOOP)
