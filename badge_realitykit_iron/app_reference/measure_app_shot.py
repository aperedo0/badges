"""Measures an iPhone 17 simulator screenshot of the app's Home badge (1206x2622 px, coin at rest).
Usage: /usr/local/bin/python3 measure_app_shot.py <screenshot.png> [more.png ...]
Prints, per screenshot:
  loaded_3d     True when the 3D coin is showing (rim band is lit, above 40); False means the flat fallback badge (rim band near 0)
  rim_top       mean luma of the rim's top band (silver 167, iron v2 and v3 147, iron v1 92)
  emblem_clip   pixels at pure white (max channel >= 254) in the emblem box (silver 796, iron v3 4934)
  emblem_mean   mean luma in the emblem box (silver 81, iron v3 84)
Boxes are in screenshot pixels: emblem x 500-720, y 440-780; rim top band x 560-646, y 364-388 (the rim's top, above the inset).
"""
import sys
import numpy as np
from PIL import Image
for path in sys.argv[1:]:
    rgb = np.asarray(Image.open(path).convert('RGB')).astype(float)
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722])
    rim = luma[364:388, 560:646].mean()
    em = rgb[440:780, 500:720].max(axis=2)
    print(f"{path}: loaded_3d={rim > 40} rim_top={rim:.1f} emblem_clip={int((em >= 254).sum())} emblem_mean={luma[440:780, 500:720].mean():.1f}")
