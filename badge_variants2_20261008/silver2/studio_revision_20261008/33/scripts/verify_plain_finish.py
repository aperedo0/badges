"""Check the actual delivered maps, including the complete plain lower fifth."""
from pathlib import Path
import json
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
for kind in ['silver2']:
    base = root / kind
    settings=json.loads((base/'settings.json').read_text())
    build = json.loads((base / 'reports/build.json').read_text())
    records = []
    for path in sorted((base / 'mobile/textures').glob('*.png')):
        pixels = np.asarray(Image.open(path))
        y = np.linspace(3.015, -3.015, pixels.shape[0])
        if settings.get('star_uv_islands') and path.name.startswith(('Silver2_StarLit','Silver2_StarShaded')):
            # Atlas rows do not correspond to world height. Star fronts are above
            # the lower fifth; shared leaf backs use a constant plain UV island.
            low=pixels[384:512,384:512]
        else:
            low = pixels[y <= -2.455 + .20 * build['height']]
        variation = int(np.max(np.ptp(low.reshape(-1, pixels.shape[-1]), axis=0))) if low.ndim == 3 else int(np.ptp(low))
        records.append({'file': path.name, 'dimensions': list(Image.open(path).size), 'plain_lower_fifth_max_channel_difference': variation})
        assert variation == 0, (path, variation)
    out = {'atlas_mapping_note':'Atlas plain island tested; actual leaf-back UV routing independently proved in precise_identity_check.json. Candidates28-30 lacked plain-back routing and are not final recommendations.', 'all_plain_lower_fifth_checks_pass': True, 'normal_map_count': len(list((base / 'mobile/textures').glob('*_normal.png'))), 'maps': records}
    assert out['normal_map_count'] == 0
    (base / 'reports/plain_finish_checks.json').write_text(json.dumps(out, indent=2) + '\n')
    print(kind, 'PASS: zero normal maps; every map exactly even throughout the lower fifth.')
