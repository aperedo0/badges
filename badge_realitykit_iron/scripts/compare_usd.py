"""Compare two USD/USDZ badge exports prim by prim and attribute by attribute.

Run with any Python that has pxr and numpy, for example Blender's:
  Blender --background --factory-startup --python compare_usd.py -- OLD.usdz NEW.usdz [report.json]

Prints every difference (missing prims, changed attribute values with the
largest numeric change, changed relationships) plus per-mesh bounds, so an
export can be checked as a drop-in replacement for the shipped file.
"""
import json
import sys

import numpy as np
from pxr import Gf, Usd, UsdGeom

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
old_path, new_path = argv[0], argv[1]
report_path = argv[2] if len(argv) > 2 else None


def attr_value(attr):
    value = attr.Get()
    if value is None:
        return None
    try:
        array = np.asarray(value)
        if array.dtype != object and array.size > 0 and not isinstance(value, str):
            return array
    except Exception:
        pass
    return value


def describe(stage):
    prims = {}
    for prim in stage.TraverseAll():
        attrs = {}
        for attr in prim.GetAttributes():
            if not attr.HasAuthoredValue() and not attr.HasAuthoredConnections():
                continue
            attrs[attr.GetName()] = (attr_value(attr), [str(c) for c in attr.GetConnections()],
                                      attr.GetMetadata('interpolation'))
        rels = {r.GetName(): [str(t) for t in r.GetTargets()] for r in prim.GetRelationships()}
        prims[str(prim.GetPath())] = dict(type=str(prim.GetTypeName()), attrs=attrs, rels=rels,
                                          children=[c.GetName() for c in prim.GetAllChildren()],
                                          display=prim.GetMetadata('displayName'),
                                          custom=dict(prim.GetCustomData()))
    return prims


def mesh_bounds(stage):
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_, UsdGeom.Tokens.render])
    out = {}
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Mesh) or prim.GetPath() == stage.GetDefaultPrim().GetPath():
            box = cache.ComputeWorldBound(prim).ComputeAlignedRange()
            out[str(prim.GetPath())] = [list(box.GetMin()), list(box.GetMax())]
        if prim.IsA(UsdGeom.Xformable):
            matrix = UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default())
            if matrix != Gf.Matrix4d(1):
                out[str(prim.GetPath()) + ' (non-identity world transform)'] = [list(r) for r in matrix]
    return out


old_stage, new_stage = Usd.Stage.Open(old_path), Usd.Stage.Open(new_path)
meta = {}
for name, stage in (('old', old_stage), ('new', new_stage)):
    meta[name] = dict(upAxis=UsdGeom.GetStageUpAxis(stage), metersPerUnit=UsdGeom.GetStageMetersPerUnit(stage),
                      defaultPrim=str(stage.GetDefaultPrim().GetPath()))
old, new = describe(old_stage), describe(new_stage)
diffs = []
for path in sorted(set(old) | set(new)):
    if path not in new:
        diffs.append(dict(prim=path, change='removed', type=old[path]['type']))
        continue
    if path not in old:
        diffs.append(dict(prim=path, change='added', type=new[path]['type']))
        continue
    a, b = old[path], new[path]
    for key in ('type', 'display', 'custom'):
        if a[key] != b[key]:
            diffs.append(dict(prim=path, change=key, old=str(a[key]), new=str(b[key])))
    common = [c for c in a['children'] if c in b['children']]
    if common != [c for c in b['children'] if c in a['children']]:
        diffs.append(dict(prim=path, change='child order', old=a['children'], new=b['children']))
    for name in sorted(set(a['attrs']) | set(b['attrs'])):
        if name not in b['attrs']:
            diffs.append(dict(prim=path, attr=name, change='attribute removed'))
            continue
        if name not in a['attrs']:
            diffs.append(dict(prim=path, attr=name, change='attribute added', new=str(b['attrs'][name][0])[:200]))
            continue
        (va, ca, ia), (vb, cb, ib) = a['attrs'][name], b['attrs'][name]
        if ca != cb or ia != ib:
            diffs.append(dict(prim=path, attr=name, change='connection/interpolation', old=[ca, ia], new=[cb, ib]))
        if isinstance(va, np.ndarray) or isinstance(vb, np.ndarray):
            va_, vb_ = np.asarray(va), np.asarray(vb)
            if va_.shape != vb_.shape:
                diffs.append(dict(prim=path, attr=name, change='array shape', old=list(va_.shape), new=list(vb_.shape)))
            elif va_.dtype.kind in 'fiu':
                delta = np.abs(va_.astype(np.float64) - vb_.astype(np.float64))
                if delta.max() > 0:
                    changed = int(np.any(delta.reshape(len(delta), -1) > 0, axis=1).sum()) if delta.ndim else 1
                    diffs.append(dict(prim=path, attr=name, change='values', max_abs_delta=float(delta.max()),
                                      elements_changed=changed, elements=int(len(va_)) if va_.ndim else 1))
            elif not np.array_equal(va_, vb_):
                diffs.append(dict(prim=path, attr=name, change='values'))
        elif str(va) != str(vb):
            diffs.append(dict(prim=path, attr=name, change='value', old=str(va)[:200], new=str(vb)[:200]))
    for name in sorted(set(a['rels']) | set(b['rels'])):
        if a['rels'].get(name) != b['rels'].get(name):
            diffs.append(dict(prim=path, rel=name, change='targets', old=a['rels'].get(name), new=b['rels'].get(name)))

result = dict(old=old_path, new=new_path, stage=meta, differences=diffs,
              bounds_old=mesh_bounds(old_stage), bounds_new=mesh_bounds(new_stage))
bounds_match = result['bounds_old'] == result['bounds_new']
print('stage', json.dumps(meta))
print('differences', len(diffs))
for d in diffs:
    print('  ', json.dumps(d))
print('bounds identical:', bounds_match)
if not bounds_match:
    for k in sorted(set(result['bounds_old']) | set(result['bounds_new'])):
        print('  ', k, result['bounds_old'].get(k), '->', result['bounds_new'].get(k))
if report_path:
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2)
