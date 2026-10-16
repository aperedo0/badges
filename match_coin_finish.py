"""Match another coin's rim finish to approved Teal Sands, retaining its hue.

Run with system Python (Pillow/numpy): NAME SOURCE.usdz OUTPUT.usdz.
Geometry, UVs, emblem textures and the inner glint shader are untouched.
This finish step runs after the older packers and coin_rim.apply().
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
from PIL import Image

from coin_rim import COLORS

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT / 'hourglass_match_20261014/hourglass_teal/mobile/hourglass_teal_badge_mobile.usdz'
USD_PYTHON = '/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13'
ROUGHNESS = 'textures/Rim_brushed_reference_roughness.png'
COLOR = 'textures/Rim_brushed_reference_color.png'


def linear_color(pixels):
    values = pixels / 255.0
    return np.where(values <= .04045, values / 12.92, ((values + .055) / 1.055) ** 2.4)


def srgb_pixels(values):
    encoded = np.where(values <= .0031308, 12.92 * values, 1.055 * np.maximum(values, 0) ** (1 / 2.4) - .055)
    return np.uint8(np.rint(np.clip(encoded, 0, 1) * 255))


def match_finish(name, source, output):
    assert name in {'clean', 'hourglass_gold', 'sunrise', 'sprout'}, name
    source, output = Path(source), Path(output)
    with tempfile.TemporaryDirectory(prefix='coin_finish_') as tmp:
        package = Path(tmp)
        with zipfile.ZipFile(source) as original, zipfile.ZipFile(REFERENCE) as reference:
            names = original.namelist()
            original.extractall(package)
            usd = next(n for n in names if n.endswith('.usdc'))
            source_rough = np.array(Image.open(original.open(ROUGHNESS)))
            source_color = np.array(Image.open(original.open(COLOR)))
            reference_rough = np.array(Image.open(reference.open(ROUGHNESS)))
            reference_color = np.array(Image.open(reference.open(COLOR)))
        assert source_rough.shape == reference_rough.shape == (1024, 1024)
        v = 1 - (np.arange(1024) + .5) / 1024
        changed_rows = ((v >= .006) & (v <= .494)) | ((v >= .526) & (v <= .744))
        rough = source_rough.copy()
        rough[changed_rows] = reference_rough[changed_rows]
        color = source_color.copy()
        # Divide out Teal Sands' steel hue, keeping its real neutral grain.
        neutral_grain = linear_color(reference_color[changed_rows]) / np.array([.50, .52, .55])
        color[changed_rows] = srgb_pixels(neutral_grain * np.array(COLORS[name]))
        Image.fromarray(rough).save(package / ROUGHNESS)
        Image.fromarray(color).save(package / COLOR)
        assert np.array_equal(rough[~changed_rows], source_rough[~changed_rows])
        assert np.array_equal(color[~changed_rows], source_color[~changed_rows])

        # The outer border uses the same softer reflection finish as the
        # approved Teal Sands border. Its hue and the inner border stay intact.
        edit = '''from pxr import Usd, UsdShade
import sys
source, reference, output = sys.argv[1:]
stage = Usd.Stage.Open(source)
approved = Usd.Stage.Open(reference)
path = '/Badge/_materials/Shell_bevel/RoughnessMap'
shader = UsdShade.Shader(stage.GetPrimAtPath(path))
target = UsdShade.Shader(approved.GetPrimAtPath(path))
assert shader and target
allowed = {path + '.inputs:scale', path + '.inputs:bias'}
before = {str(a.GetPath()): a.Get() for p in stage.Traverse() for a in p.GetAttributes()}
relationships = {str(r.GetPath()): r.GetTargets() for p in stage.Traverse() for r in p.GetRelationships()}
for name in ['scale', 'bias']:
    shader.GetInput(name).Set(target.GetInput(name).Get())
after = {str(a.GetPath()): a.Get() for p in stage.Traverse() for a in p.GetAttributes()}
assert before.keys() == after.keys()
assert all(before[k] == after[k] for k in before.keys() - allowed)
assert relationships == {str(r.GetPath()): r.GetTargets() for p in stage.Traverse() for r in p.GetRelationships()}
assert stage.GetRootLayer().Export(output)
'''
        edited = package / 'edited.usdc'
        subprocess.run([USD_PYTHON, '-I', '-c', edit, str(package / usd), str(REFERENCE), str(edited)], check=True, capture_output=True)
        edited.replace(package / usd)
        # Stable file dates make repeated packs reproducible.
        for path in names:
            os.utime(package / path, (946684800, 946684800))
        candidate = package / 'finished.usdz'
        subprocess.run(['/usr/bin/usdzip', str(candidate)] + names, cwd=package, check=True, capture_output=True)
        gate = subprocess.run(['/usr/bin/usdchecker', '--arkit', str(candidate)], capture_output=True, text=True)
        assert gate.returncode == 0, gate.stdout + gate.stderr
        with zipfile.ZipFile(source) as original, zipfile.ZipFile(candidate) as finished:
            assert set(original.namelist()) == set(finished.namelist())
            assert all(original.read(n) == finished.read(n) for n in names if n not in {usd, ROUGHNESS, COLOR})
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(candidate.read_bytes())
    return {'name': name, 'file': str(output), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'geometry_normals_UVs_emblem_inner_glints': 'unchanged', 'USD_validation': 'passed'}


if __name__ == '__main__':
    name, source, output = sys.argv[1:]
    print(json.dumps(match_finish(name, source, output)))
