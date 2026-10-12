"""Check the actual delivered maps, including the complete plain lower fifth."""
from pathlib import Path
import json
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
for kind in ['silver2', 'iron2']:
    base = root / kind
    build = json.loads((base / 'reports/build.json').read_text())
    records = []
    for path in sorted((base / 'mobile/textures').glob('*.png')):
        pixels = np.asarray(Image.open(path))
        y = np.linspace(3.015, -3.015, pixels.shape[0])
        low = pixels[y <= -2.455 + .20 * build['height']]
        variation = int(np.max(np.ptp(low.reshape(-1, pixels.shape[-1]), axis=0))) if low.ndim == 3 else int(np.ptp(low))
        records.append({'file': path.name, 'dimensions': list(Image.open(path).size), 'plain_lower_fifth_max_channel_difference': variation})
        assert variation == 0, (path, variation)
    out = {'all_plain_lower_fifth_checks_pass': True, 'normal_map_count': len(list((base / 'mobile/textures').glob('*_normal.png'))), 'maps': records}
    assert out['normal_map_count'] == 0
    (base / 'reports/plain_finish_checks.json').write_text(json.dumps(out, indent=2) + '\n')
    print(kind, 'PASS: zero normal maps; every map exactly even throughout the lower fifth.')
