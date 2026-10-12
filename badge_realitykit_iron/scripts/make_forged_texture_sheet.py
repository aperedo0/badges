"""Inspect the actual delivered maps without changing the app-tested asset."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
tiles = [
    ("Brushed iron color", "USDZ_Casing_base_color.png"),
    ("Brushed iron roughness", "USDZ_Casing_roughness.png"),
    ("Crystal main color", "USDZ_Emblem_base_color.png"),
    ("Crystal roughness", "USDZ_Emblem_roughness.png"),
    ("Crystal shaded color", "USDZ_Emblem_shaded_base_color.png"),
    ("Charcoal inset color", "USDZ_Inset_base_color.png"),
]
sheet = Image.new("RGB", (1048, 1692), (20, 20, 20))
draw = ImageDraw.Draw(sheet)
for index, (label, name) in enumerate(tiles):
    x = 8 + (index % 2) * 524
    y = 8 + (index // 2) * 556
    draw.text((x, y), label + " | 512 x 512", fill=(240, 240, 240))
    with Image.open(root / "mobile/textures" / name) as tile:
        sheet.paste(tile.convert("RGB"), (x, y + 28))
draw.text((8, 1680), "Forged Iron: actual delivered color / roughness maps", fill=(240, 240, 240))
sheet.save(root / "proof/forged_texture_sheet.png")
