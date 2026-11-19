"""Clip exact cutting planes to retain their shared, stable facet boundaries."""
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull

R = Path(__file__).resolve().parent
D = np.load(R.parent / 'ruby_heart/candidate20/geometry.npz')
raw = np.load(R / 'heart_plane_cut_0.65_1.7.npz')
result = {}

def unique(points, tolerance=1e-7):
    out = []
    for point in points:
        if not any(np.linalg.norm(point - p) < tolerance for p in out):
            out.append(point)
    return np.asarray(out)

for domain in range(2):
    old = D[f'{domain + 3}_points'].astype(float)
    front = ConvexHull(old).equations
    front = front[front[:, 2] > -1e-6]
    rear = ConvexHull(raw[f'{domain}_points']).equations
    rear = rear[rear[:, 2] < -.01].copy()
    rear[:, 3] -= rear[:, 2] * (old[48:96, 2].mean() + .03)
    planes = np.unique(np.round(np.vstack([front, rear]), 9), axis=0)
    box = np.array([[-8,-8,-8],[8,-8,-8],[8,8,-8],[-8,8,-8],[-8,-8,8],[8,-8,8],[8,8,8],[-8,8,8]], float)
    faces = [box[x] for x in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]]
    for eq in planes:
        if max(float(np.max(face @ eq[:3] + eq[3])) for face in faces) <= 2e-6:
            continue
        updated, cap = [], []
        for face in faces:
            clipped = []
            for a, b in zip(face, np.roll(face, -1, axis=0)):
                ga, gb = a @ eq[:3] + eq[3], b @ eq[:3] + eq[3]
                if abs(ga) < 2e-6: ga = 0.
                if abs(gb) < 2e-6: gb = 0.
                if ga <= 0:
                    clipped.append(a)
                    if ga == 0: cap.append(a)
                if (ga < 0 and gb > 0) or (ga > 0 and gb < 0):
                    point = a + ga / (ga - gb) * (b - a)
                    clipped.append(point)
                    cap.append(point)
            clipped = unique(clipped)
            if len(clipped) >= 3 and np.linalg.norm(np.cross(clipped[1:] - clipped[0], np.roll(clipped[1:], -1, axis=0) - clipped[0]).sum(0)) > 1e-8:
                updated.append(clipped)
        cap = unique(cap)
        if len(cap) >= 3:
            center = cap.mean(0)
            normal = eq[:3]
            ref = np.array([1.,0,0]) if abs(normal[0]) < .9 else np.array([0.,1,0])
            u = np.cross(normal, ref); u /= np.linalg.norm(u)
            v = np.cross(normal, u)
            cap = cap[np.argsort(np.arctan2((cap-center) @ v, (cap-center) @ u))]
            if np.linalg.norm(np.cross(cap[1:] - cap[0], np.roll(cap[1:], -1, axis=0) - cap[0]).sum(0)) > 1e-8:
                updated.append(cap)
        faces = updated
    points, triangles, lookup = [], [], {}
    def vertex(p):
        if points:
            distance = np.linalg.norm(np.asarray(points) - p, axis=1)
            near = int(np.argmin(distance))
            if distance[near] < 2e-6:
                return near
        key = tuple(np.round(p, 6))
        if key not in lookup:
            lookup[key] = len(points); points.append(p)
        return lookup[key]
    for face in faces:
        center = face.mean(0)
        center_id = vertex(center)
        ids = [vertex(p) for p in face]
        for a, b in zip(ids, np.roll(ids, -1)):
            if len({center_id, int(a), int(b)}) == 3:
                triangles.append([center_id, a, b])
    p, t = np.asarray(points, np.float32), np.asarray(triangles, np.int32)
    n = np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]])
    inward = ((p[t].mean(1) - p.mean(0)) * n).sum(1) < 0
    t[inward] = t[inward, ::-1]
    n[inward] *= -1
    area = np.linalg.norm(n,axis=1)
    assert area.min() > 1e-9, area.min()
    n /= area[:,None]
    violation = float((p @ n.T - (n*p[t[:,0]]).sum(1)).max())
    assert violation < 9e-6, violation
    edges = np.sort(np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1)
    _, counts = np.unique(edges,axis=0,return_counts=True)
    assert np.all(counts == 2), np.unique(counts,return_counts=True)
    result[f'{domain}_points'] = p
    result[f'{domain}_triangles'] = t
    print(domain,len(faces),len(p),len(t),violation,flush=True)
np.savez_compressed(R/'heart_reference_closed_cut.npz',**result)
