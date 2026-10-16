"""Strengthen the approved Teal Sands outside-wall finish by ten percent.

Only side-chart pixels change. Front band, glint borders, emblem, geometry
and UVs remain identical to the approved 100% preview. Use system Python
with Pillow/numpy. Optional first argument specifies an output USDZ.
"""
from pathlib import Path
from PIL import Image
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'previous/hourglass_teal_side_100.usdz'
OUTPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'mobile/hourglass_teal_badge_mobile.usdz'


def build(source=SOURCE, output=OUTPUT):
    rough_name = 'textures/Rim_brushed_reference_roughness.png'
    color_name = 'textures/Rim_brushed_reference_color.png'
    with tempfile.TemporaryDirectory(prefix='teal_side_finish_') as tmp:
        pkg = Path(tmp)
        with zipfile.ZipFile(source) as original:
            original.extractall(pkg)
            usd = next(n for n in original.namelist() if n.endswith('.usdc'))
        rough = np.asarray(Image.open(pkg / rough_name), dtype=float) / 255
        rgb = np.asarray(Image.open(pkg / color_name), dtype=float) / 255
        v = 1 - (np.arange(rough.shape[0]) + .5) / rough.shape[0]
        side = (v >= .526) & (v <= .744)
        result = rough.copy()
        result[side] *= .90
        Image.fromarray(np.uint8(np.rint(np.clip(result, 0, 1) * 255))).save(pkg / rough_name)
        linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
        base = np.array([.50, .52, .55])
        linear[side] = base + (linear[side] - base) * 1.10
        encoded = np.where(linear <= .0031308, 12.92 * linear, 1.055 * np.maximum(linear, 0) ** (1 / 2.4) - .055)
        Image.fromarray(np.uint8(np.rint(np.clip(encoded, 0, 1) * 255))).save(pkg / color_name)
        candidate = pkg / 'result.usdz'
        subprocess.run(['/usr/bin/usdzip', str(candidate), usd] + sorted(str(p.relative_to(pkg)) for p in (pkg / 'textures').glob('*.png')), cwd=pkg, check=True, capture_output=True)
        gate = subprocess.run(['/usr/bin/usdchecker', '--arkit', str(candidate)], capture_output=True, text=True)
        assert gate.returncode == 0, gate.stdout + gate.stderr
        with zipfile.ZipFile(source) as original, zipfile.ZipFile(candidate) as updated:
            assert set(original.namelist()) == set(updated.namelist())
            for name in original.namelist():
                if name not in [rough_name, color_name]:
                    assert original.read(name) == updated.read(name), name
            for name in [rough_name, color_name]:
                a = np.asarray(Image.open(original.open(name)))
                b = np.asarray(Image.open(updated.open(name)))
                assert np.array_equal(a[~side], b[~side]), name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(candidate.read_bytes())
    return {'file': str(output), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'bytes': output.stat().st_size, 'USD validation': 'passed', 'scope': 'side atlas only; front, borders and all other data identical'}


if __name__ == '__main__':
    print(json.dumps(build()))
