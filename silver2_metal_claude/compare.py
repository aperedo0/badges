"""compare.py <name> [<name2> ...] : reference | c33 | candidates, star and wreath at Home size, written to compare_<last>.png"""
import sys
from PIL import Image, ImageDraw
W = '/Users/antonioperedo/Desktop/badges/silver2_metal_claude'
ref = Image.open(W + '/src/silver_reference.png').convert('RGB')
# reference badge width matched to the app: wreath spans app x 373..830 (457 px); reference wreath spans about 30..1224
r = ref.resize((round(1254 * 457 / 1194), round(1254 * 457 / 1194)), Image.LANCZOS)
ox = round(30 * 457 / 1194); refc = r.crop((ox - 30, 40, ox - 30 + 520, 40 + 470))
def app(n): return Image.open(f'{W}/{n}/app.png' if n != 'c33' else W + '/src/c33_app_rest.png').convert('RGB').crop((343, 370, 863, 840))
tiles = [('Reference', refc), ('Codex 33', app('c33'))] + [(n, app(n)) for n in sys.argv[1:]]
out = Image.new('RGB', (len(tiles) * 530, 500), (16, 16, 20)); d = ImageDraw.Draw(out)
for i, (t, im) in enumerate(tiles): out.paste(im, (i * 530, 28)); d.text((i * 530 + 8, 8), t, fill=(255, 255, 255))
out.save(f'{W}/compare_{sys.argv[-1]}.png')
