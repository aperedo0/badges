"""meshio.py export <in.usdz> <work> : unzip into <work>/pkg, write <work>/mesh.npz with, per mesh i: name, points, counts, indices,
normals (+interp), uv (+interp, primvar name), subsets (name, material, indices).
meshio.py import <work> <out.usdz> : apply <work>/edit.npz (keys '<i>:points', '<i>:normals', '<i>:uv') and <work>/edit.json
({"bind": {"<mesh>/<subset>": "<material name>"}, "materials": {...matedit-like...}}), pack and check."""
import sys, os, json, shutil, subprocess, zipfile
import numpy as np
def compact_usdc(path):
    """Re-save with Apple's usdcat: its crate writer packs float arrays (Blender's does not; 2.8 MB vs 5.4 MB)."""
    if not path.endswith('.usdc'): return
    tmp = path[:-5] + '_compact.usdc'; subprocess.run(['/usr/bin/usdcat', path, '-o', tmp], check=True); os.replace(tmp, path)
from pxr import Usd, UsdGeom, UsdShade, Sdf, Vt, Gf
mode = sys.argv[1]
if mode == 'export':
    src, work = sys.argv[2], sys.argv[3]; pkg = os.path.join(work, 'pkg'); shutil.rmtree(pkg, ignore_errors=True); os.makedirs(pkg)
    names = zipfile.ZipFile(src).namelist(); zipfile.ZipFile(src).extractall(pkg); json.dump(names, open(os.path.join(work, 'names.json'), 'w'))
    st = Usd.Stage.Open(os.path.join(pkg, names[0])); out = {}; meta = []
    for i, p in enumerate([p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]):
        m = UsdGeom.Mesh(p); out[f'{i}:points'] = np.array(m.GetPointsAttr().Get(), float)
        out[f'{i}:counts'] = np.array(m.GetFaceVertexCountsAttr().Get()); out[f'{i}:indices'] = np.array(m.GetFaceVertexIndicesAttr().Get())
        n = m.GetNormalsAttr(); out[f'{i}:normals'] = np.array(n.Get(), float) if n.HasAuthoredValue() else np.zeros((0, 3))
        uvs = [pv for pv in UsdGeom.PrimvarsAPI(p).GetPrimvars() if pv.GetTypeName() in (Sdf.ValueTypeNames.TexCoord2fArray, Sdf.ValueTypeNames.Float2Array)]
        uvname = uvinterp = None
        if uvs:
            pv = uvs[0]; uvname = pv.GetPrimvarName(); uvinterp = pv.GetInterpolation(); v = np.array(pv.Get(), float)
            if pv.GetIndices(): v = v[np.array(pv.GetIndices())]
            out[f'{i}:uv'] = v
        subs = []
        for s in UsdGeom.Subset.GetAllGeomSubsets(m):
            mt = UsdShade.MaterialBindingAPI(s.GetPrim()).ComputeBoundMaterial()[0]
            subs.append({'name': s.GetPrim().GetName(), 'material': mt.GetPrim().GetName() if mt else None}); out[f'{i}:subset:{s.GetPrim().GetName()}'] = np.array(s.GetIndicesAttr().Get())
        base = UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial()[0]
        meta.append({'i': i, 'path': str(p.GetPath()), 'name': p.GetName(), 'normals_interp': m.GetNormalsInterpolation(), 'uv': uvname, 'uv_interp': uvinterp, 'subsets': subs, 'material': base.GetPrim().GetName() if base else None})
    np.savez(os.path.join(work, 'mesh.npz'), **out); json.dump(meta, open(os.path.join(work, 'meta.json'), 'w'), indent=1)
    for m_ in meta: print(m_['name'], len(out[f"{m_['i']}:counts"]), 'faces', m_['normals_interp'], m_['uv'], m_['uv_interp'], [(s['name'], s['material'], len(out[f"{m_['i']}:subset:{s['name']}"])) for s in m_['subsets']])
else:
    work, dst = sys.argv[2], sys.argv[3]; pkg = os.path.join(work, 'pkg'); names = json.load(open(os.path.join(work, 'names.json')))
    tmp = os.path.join(work, 'pkg_out'); shutil.rmtree(tmp, ignore_errors=True); shutil.copytree(pkg, tmp)
    st = Usd.Stage.Open(os.path.join(tmp, names[0])); meshes = [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]
    ed = dict(np.load(os.path.join(work, 'edit.npz'))) if os.path.exists(os.path.join(work, 'edit.npz')) else {}
    cfg = json.load(open(os.path.join(work, 'edit.json'))) if os.path.exists(os.path.join(work, 'edit.json')) else {}
    mats = {p.GetName(): UsdShade.Material(p) for p in st.Traverse() if p.IsA(UsdShade.Material)}
    for i, p in enumerate(meshes):
        m = UsdGeom.Mesh(p)
        if f'{i}:points' in ed: m.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(ed[f'{i}:points'].astype(np.float32)))
        if f'{i}:normals' in ed:
            n_ = ed[f'{i}:normals']; n_ = n_ / np.maximum(np.linalg.norm(n_, axis=1, keepdims=True), 1e-9)
            m.GetNormalsAttr().Set(Vt.Vec3fArray.FromNumpy((np.round(n_ * 2048) / 2048).astype(np.float32)))   # few distinct values: crate packs it
        if f'{i}:uv' in ed:
            pv = [pv for pv in UsdGeom.PrimvarsAPI(p).GetPrimvars() if pv.GetTypeName() in (Sdf.ValueTypeNames.TexCoord2fArray, Sdf.ValueTypeNames.Float2Array)][0]
            if pv.GetIndices(): pv.BlockIndices()
            pv.Set(Vt.Vec2fArray.FromNumpy((np.round(ed[f'{i}:uv'] * 16384) / 16384).astype(np.float32)))
        for s_ in UsdGeom.Subset.GetAllGeomSubsets(m):
            k_ = f'{i}:subset:' + s_.GetPrim().GetName()
            if k_ in ed:
                if len(ed[k_]) == 0: st.RemovePrim(s_.GetPrim().GetPath())
                else: s_.GetIndicesAttr().Set(Vt.IntArray.FromNumpy(ed[k_].astype(np.int32)))
        for k_ in [k for k in ed if k.startswith(f'{i}:newsubset:')]:
            UsdGeom.Subset.CreateGeomSubset(m, k_.split(':')[-1], UsdGeom.Tokens.face, Vt.IntArray.FromNumpy(ed[k_].astype(np.int32)), UsdShade.Tokens.materialBind, UsdGeom.Tokens.partition)
        if f'{i}:extent' in ed: m.GetExtentAttr().Set(Vt.Vec3fArray.FromNumpy(ed[f'{i}:extent'].astype(np.float32)))
    for newname, (srcname, matpath) in cfg.get('new_materials', {}).items():   # copy a material prim under a new name
        src_ = mats[srcname].GetPrim(); dstp = src_.GetPath().GetParentPath().AppendChild(newname)
        Sdf.CopySpec(st.GetRootLayer(), src_.GetPath(), st.GetRootLayer(), dstp); mats[newname] = UsdShade.Material(st.GetPrimAtPath(dstp))
    for key, matname in cfg.get('bind', {}).items():
        mesh, sub = key.split('/'); p = [q for q in meshes if q.GetName() == mesh][0]
        UsdShade.MaterialBindingAPI.Apply(p.GetChild(sub)).Bind(mats[matname])
    st.GetRootLayer().Save()
    compact_usdc(st.GetRootLayer().realPath)
    for f in cfg.get('replace_files', {}): shutil.copy(cfg['replace_files'][f], os.path.join(tmp, f))
    os.path.exists(dst) and os.remove(dst)
    subprocess.run(['usdzip', dst] + names, cwd=tmp, check=True, stdout=subprocess.DEVNULL)
    r = subprocess.run(['usdchecker', '--arkit', dst], capture_output=True, text=True)
    print(os.path.basename(dst), os.path.getsize(dst), 'arkit', 'OK' if 'Success' in r.stdout + r.stderr else (r.stdout + r.stderr)[-600:])
