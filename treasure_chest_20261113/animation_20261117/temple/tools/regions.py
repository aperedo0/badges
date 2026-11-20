"""Median colour (sRGB 0-255) of named regions, mockup vs render (normalized coordinates): python3 regions.py RENDER.png"""
import sys
import numpy as np
from PIL import Image
REF = "/Users/antonioperedo/Downloads/Ancient stone temple with emerald badge.png"
R = {  # x0, y0, x1, y1 in 0..1
    "pillarL lit": (0.06, 0.12, 0.12, 0.30), "pillarL dark edge": (0.035, 0.12, 0.05, 0.30),
    "pillarR lit": (0.87, 0.12, 0.93, 0.30), "capitalL": (0.04, 0.035, 0.16, 0.06),
    "plinthL": (0.02, 0.37, 0.15, 0.43), "arch band top": (0.42, 0.034, 0.58, 0.05),
    "apse inside top": (0.35, 0.07, 0.45, 0.13), "apse inside side": (0.27, 0.2, 0.30, 0.3),
    "aisle gap L": (0.155, 0.05, 0.175, 0.3), "floor far L": (0.02, 0.47, 0.2, 0.52),
    "floor mid L": (0.0, 0.55, 0.15, 0.65), "floor near bottom": (0.2, 0.95, 0.8, 1.0),
    "dais top front": (0.35, 0.86, 0.65, 0.885), "dais top left": (0.04, 0.80, 0.14, 0.84),
    "dais side front": (0.3, 0.9, 0.7, 0.93), "floor right": (0.88, 0.6, 1.0, 0.7)}
def stats(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    h, w = a.shape[:2]
    out = {}
    for k, (x0, y0, x1, y1) in R.items():
        c = a[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)].reshape(-1, 3)
        out[k] = np.median(c, 0)
    return out
A, B = stats(REF), stats(sys.argv[1])
print(f"{'region':20s} {'mockup':>16s} {'render':>16s}  ratio(lum)")
for k in R:
    la, lb = A[k].mean(), B[k].mean()
    print(f"{k:20s} {str(A[k].astype(int)):>16s} {str(B[k].astype(int)):>16s}  {lb / max(la, 1):.2f}")
