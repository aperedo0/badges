"""Preserve the installed contact revision and prepare an optically balanced crystal."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np

root = Path(__file__).resolve().parents[1]
prior = root / 'forged_revision/08'
archive = root / 'previous/forged08'
assert not archive.exists(), 'Never overwrite a preserved version'
archive.mkdir()
for name in ['mobile', 'scenes', 'proof']:
    shutil.copytree(root / name, archive / name)
for name in ['REPORT.md', 'parameters.json']:
    shutil.copy2(root / name, archive / name)
files = {
    str(path.relative_to(archive)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in archive.rglob('*') if path.is_file()
}
(root / 'reports/forged08_archive.json').write_text(json.dumps({
    'root': str(archive.relative_to(root)), 'files': files
}, indent=2))

revision = root / 'centering_revision/01'
assert not revision.exists()
for name in ['scenes', 'work', 'logs', 'reports', 'proof/renders', 'mobile/textures']:
    (revision / name).mkdir(parents=True)
shutil.copytree(root / 'scripts', revision / 'scripts')
shutil.copytree(root / 'source', revision / 'source')
for name in ['v3', 'final08']:
    shutil.copytree(root / 'previous' / name / 'mobile', revision / 'previous' / name / 'mobile')
for name in ['smoothness_silver_pose00.json', 'smoothness_silver_pose20.json', 'emblem_silver.json']:
    shutil.copy2(prior / 'proof' / name, revision / 'proof' / name)
for path in (prior / 'proof/renders').glob('silver_*.png'):
    shutil.copy2(path, revision / 'proof/renders' / path.name)

parameters = json.loads((prior / 'parameters.json').read_text())
parameters['reference_front_faces'] = parameters['front_faces']
points = np.array(parameters['outline'] + [[0, .52, .96], [0, -.62, .88]])
points[[0, 4], 0] = 0
points[1, 0] = .67
points[3, 0] = .62
points[5, 0] = -.60
points[6, 1] = .23
points[2, 1] = .16
points[4, 2] = .56
faces = [[0, 6, 7], [6, 5, 8, 7], [5, 4, 8],
         [0, 7, 2, 1], [2, 7, 8, 3], [3, 8, 4]]
# Solve each shoulder vertex on its broad plane, never triangulate a warped quad.
for face, index in [(faces[1], 5), (faces[3], 1), (faces[4], 3)]:
    fixed = points[[i for i in face if i != index]]
    normal = np.cross(fixed[1] - fixed[0], fixed[2] - fixed[0])
    points[index, 2] = fixed[0, 2] - normal[:2] @ (points[index, :2] - fixed[0, :2]) / normal[2]
assert points[:7, 2].min() > parameters['crystal_back_z']
outline = points[:7, :2]
next_outline = np.roll(outline, -1, axis=0)
cross = outline[:, 0] * next_outline[:, 1] - next_outline[:, 0] * outline[:, 1]
centroid = ((outline + next_outline) * cross[:, None]).sum(0) / (3 * cross.sum())
# Area centering plus a tiny rightward optical offset balances the lit left side.
offset = -centroid + np.array([.025, 0])
points[:, :2] += offset
parameters.update(outline=points[:7].tolist(), interior=points[7:].tolist(),
                  front_faces=faces, main_front_planes=[0, 1, 2],
                  shaded_front_planes=[3, 4, 5], ridge_vertex_indices=[0, 7, 8, 4],
                  plane_color_gains={'0': .60, '3': .95},
                  centering_offset_xy=offset.tolist(),
                  centering_revision='01', front_planes=6)
(revision / 'parameters.json').write_text(json.dumps(parameters, indent=2))
(revision / 'NOTES.md').write_text(
    'Straight continuous center ridge with three large planes on each side. '
    'Balance lower shoulders while retaining the angled upper-right cut, irregular outline, '
    'original height/width and forged detail. Center by silhouette area, then shift right '
    '0.025 units to balance left lighting. Attenuate only the upper-left plane color; '
    'raise the previously dark upper-right plane. Preserve rim/casing texture pixels.\n')
print('Prepared', revision, 'offset', offset.tolist(), 'archived', len(files), 'files')
