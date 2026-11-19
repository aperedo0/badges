"""Keep the measured front cut and replace the shallow rear with a real pavilion."""
from pathlib import Path
import json, shutil, hashlib
import numpy as np
from scipy.spatial import ConvexHull, cKDTree

R = Path(__file__).resolve().parent
B = R / 'ruby_heart/candidate20'
C = R / 'ruby_heart/candidate26'
assert not C.exists()
cut = np.load(R / 'optics_fit/heart_reference_crown_candidate20.npz')
parts = [cut[f'{j}_points'].copy() for j in range(2)]
shift = -float((min(p[:, 2].min() for p in parts) + max(p[:, 2].max() for p in parts)) / 2)
groups = json.loads((B / 'groups.json').read_text())
D = np.load(B / 'geometry.npz')
out, report, gem = {}, [], 0
for i, g in enumerate(groups):
    p, t = D[f'{i}_points'].copy(), D[f'{i}_triangles'].copy()
    if g['mat'] == 'CrestGem_Rose':
        exact = parts[gem]
        # Intersecting redundant cutting planes creates duplicate corner samples.
        # Collapse only corners less than two millionths of a scene unit apart.
        tree = cKDTree(exact)
        used = set()
        merged = []
        for index in range(len(exact)):
            if index in used:
                continue
            cluster = tree.query_ball_point(exact[index], 2e-6)
            used.update(cluster)
            merged.append(exact[cluster].mean(0))
        exact = np.asarray(merged)
        exact[:, 2] += shift
        hull = ConvexHull(exact)
        planes = np.unique(np.round(hull.equations, 8), axis=0)
        points, triangles = list(exact), []
        for eq in planes:
            normal = eq[:3]
            indices = np.flatnonzero(abs(exact @ normal + eq[3]) < 8e-8)
            assert len(indices) >= 3
            center = exact[indices].mean(0)
            ref = np.array([0., 1, 0]) if abs(normal[1]) < .9 else np.array([1., 0, 0])
            u = np.cross(normal, ref)
            u /= np.linalg.norm(u)
            v = np.cross(normal, u)
            rel = exact[indices] - center
            indices = indices[np.argsort(np.arctan2(rel @ v, rel @ u))]
            mid = len(points)
            points.append(center)
            for a, b in zip(indices, np.roll(indices, -1)):
                face = [mid, int(a), int(b)]
                if np.cross(exact[a] - center, exact[b] - center) @ normal < 0:
                    face = face[::-1]
                triangles.append(face)
        p, t = np.asarray(points, np.float32), np.asarray(triangles, np.int32)
        normal = np.cross(p[t[:, 1]] - p[t[:, 0]], p[t[:, 2]] - p[t[:, 0]])
        area = np.linalg.norm(normal, axis=1)
        assert area.min() > 1e-9
        normal /= area[:, None]
        offset = (normal * p[t[:, 0]]).sum(1)
        violation = float((p @ normal.T - offset).max())
        print('DIAGNOSTIC',gem,len(exact),len(planes),area.min(),violation, 'bad',np.sum((p @ normal.T - offset).max(0)>9e-6), 'worst', t[np.argmax((p @ normal.T - offset).max(0))], flush=True); assert violation < 9e-6, violation
        edges = np.sort(np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]]), axis=1)
        _, counts = np.unique(edges, axis=0, return_counts=True)
        assert np.all(counts == 2), np.unique(counts, return_counts=True)
        assert len(planes) <= 256
        report.append(dict(name=g['name'],facet_planes=len(planes),triangles=len(t),maximum_float32_support_violation=violation,closed_mesh=True))
        gem += 1
    else:
        p[:, 2] += shift
    out[f'{i}_points'], out[f'{i}_triangles'] = p.astype(np.float32), t
assert gem == 2
for name in ['source', 'mobile', 'textures', 'review']:
    (C / name).mkdir(parents=True)
np.savez_compressed(C / 'geometry.npz', **out)
for name in ['groups.json', 'materials.json']:
    shutil.copy2(B / name, C / name)
for p in (B / 'textures').glob('*.png'):
    shutil.copy2(p, C / 'textures' / p.name)
trial = json.loads((R / 'ruby_heart/candidate25/optical_color_trial.json').read_text())
trial.update(source_geometry='candidate26',model_and_texture_bytes_unchanged=False,native_review_pending=True,reference_front_cut_preserved=True,shared_pavilion_from_candidate24=True)
(C / 'optical_color_trial.json').write_text(json.dumps(trial, indent=2) + '\n')
(C / 'source/optical_runtime_parameters.json').write_text(json.dumps(trial, indent=2) + '\n')
(C / 'physical_cut_review.json').write_text(json.dumps(dict(reference_front='candidate20',coordinated_pavilion='candidate24',global_z_center_shift=shift,domains=report,clear_optics_unchanged_from_candidate25=True,not_accepted_before_native_review=True), indent=2) + '\n')
print(json.dumps(report, indent=2), flush=True)
