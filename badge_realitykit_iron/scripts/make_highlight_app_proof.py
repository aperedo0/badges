"""Unretouched app comparison and diagnostic luminance changes outside the emblem."""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import sobel, map_coordinates, binary_dilation
root = Path(__file__).resolve().parents[1]; r = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / 'scripts')); import measure_smoothness as ms
old_path = root / 'previous/v5/proof/app_iron_rest.png'
new_path = r / 'app_rest.png'
for name, box, scale in [('app_v5_vs_candidate.png', (330, 340, 875, 920), 1),
                          ('app_upper_left_4x.png', (498, 428, 710, 630), 4)]:
    w, h = (box[2]-box[0])*scale, (box[3]-box[1])*scale
    sheet = Image.new('RGB', (w*2+20, h+32), (20, 20, 20)); draw = ImageDraw.Draw(sheet)
    for i, (label, path) in enumerate([('Approved v5', old_path), (f'Candidate {r.name}', new_path)]):
        draw.text((i*(w+20)+8, 8), label, fill='white')
        crop = Image.open(path).convert('RGB').crop(box)
        if scale != 1: crop = crop.resize((w, h), Image.Resampling.NEAREST)
        sheet.paste(crop, (i*(w+20), 32))
    sheet.save(r / name)
old = np.asarray(Image.open(old_path).convert('RGB'), float)
new = np.asarray(Image.open(new_path).convert('RGB'), float)
weights = np.array([.2126, .7152, .0722]); luma = old @ weights
gradient = np.hypot(sobel(luma, axis=0), sobel(luma, axis=1))
baseline = json.loads((root / 'previous/v5/parameters.json').read_text())
candidate = json.loads((r / 'parameters.json').read_text())
source, _ = ms.project(np.array(baseline['outline']), 0)
source *= 47/60  # Documented 3x simulator scale: 3 * (47/180) points/master pixel.
samples = np.concatenate([source[i]*(1-t[:,None])+source[(i+1)%8]*t[:,None]
                          for i in range(8) for t in [np.linspace(.12, .88, 50)]])
best = (-1, None)
for dx in np.arange(178., 182.01, .5):
    for dy in np.arange(60., 85.01, .5):
        score = float(map_coordinates(gradient, [samples[:,1]+dy, samples[:,0]+dx], order=1).mean())
        if score > best[0]: best = (score, (float(dx), float(dy)))
offset = np.array(best[1]); union = np.zeros(luma.shape, bool)
for p in [baseline, candidate]:
    points, _ = ms.project(np.array(p['outline']), 0); points = points*(47/60)+offset
    mask = Image.new('1', (luma.shape[1], luma.shape[0])); ImageDraw.Draw(mask).polygon([tuple(x) for x in points], fill=1)
    union |= np.asarray(mask, bool)
annulus = binary_dilation(union, iterations=12) & ~binary_dilation(union, iterations=3)
roi = np.zeros(luma.shape, bool); roi[428:630, 490:650] = True; annulus &= roi
delta = (new-old) @ weights; values = delta[annulus]
report = {'method': 'diagnostic only, no invented halo pass cutoff; camera-projected outline registered to baseline outer-edge gradients; exclude 3 AA pixels, inspect next 9 pixels on upper left',
          'camera_projection_pixel_scale':47/60, 'fitted_screenshot_offset':offset.tolist(),
          'annulus_pixels':int(annulus.sum()), 'outside_outline_mean_luma_change':float(values.mean()),
          'outside_outline_95th_percentile_luma_increase':float(np.percentile(values,95)),
          'outside_outline_max_luma_increase':float(values.max()),
          'visual_halo_judgment_required':True}
(r / 'app_highlight_diagnostic.json').write_text(json.dumps(report, indent=2)); print(json.dumps(report, indent=2))
