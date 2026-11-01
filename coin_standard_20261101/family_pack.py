"""Package live Blender inspected geometry while preserving USD material graphs."""
from pathlib import Path
import sys, json, zipfile, subprocess, hashlib, shutil, tempfile
import numpy as np
from pxr import Usd, UsdGeom, Vt, Gf
R=Path(__file__).resolve().parent;F=R/'family'
sys.path.insert(0,str(R))
from geometry import points_after,normals_after,INNER,NEW_OUTER
manifest=json.loads((F/'manifest.json').read_text());reports=[]
for item in manifest:
    name=item['name'];C=F/name/'candidate01';source=F/name/'original.usdz'
    target=C/'mobile/coin.usdz';inspected=np.load(C/'inspected_points.npz')
    with tempfile.TemporaryDirectory(prefix='coin_family_',dir='/tmp') as tmp:
        pkg=Path(tmp)
        with zipfile.ZipFile(source) as archive:
            names=archive.namelist();archive.extractall(pkg)
        usd=next(n for n in names if n.endswith(('.usd','.usda','.usdc')))
        stage=Usd.Stage.Open(str(pkg/usd))
        def unaffected():
            return {str(a.GetPath()):str(a.Get()) for p in stage.Traverse() for a in p.GetAttributes()
                    if a.GetName() not in ['points','normals','extent']}
        before=unaffected();allbefore=[];allafter=[];meshes=0
        for prim in stage.Traverse():
            if not prim.IsA(UsdGeom.Mesh):continue
            mesh=UsdGeom.Mesh(prim);p=np.array(mesh.GetPointsAttr().Get(),float);q=points_after(p)
            indices=np.array(mesh.GetFaceVertexIndicesAttr().Get(),int);counts=np.array(mesh.GetFaceVertexCountsAttr().Get(),int)
            assert np.max(abs(q-inspected[prim.GetName()]))<2e-6,(name,str(prim.GetPath()))
            if mesh.GetNormalsAttr().HasValue():
                n=np.array(mesh.GetNormalsAttr().Get(),float);kind=mesh.GetNormalsInterpolation()
                if kind=='faceVarying':at=p[indices]
                elif kind in ['vertex','varying']:at=p
                elif kind=='uniform':at=np.array([x.mean(0) for x in np.split(p[indices],np.cumsum(counts)[:-1])])
                elif kind=='constant':at=p.mean(0)[None]
                else:raise RuntimeError(kind)
                mesh.GetNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(normals_after(at,n).astype(np.float32)))
            mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(q.astype(np.float32)))
            mesh.GetExtentAttr().Set([Gf.Vec3f(*q.min(0)),Gf.Vec3f(*q.max(0))])
            allbefore.append(p);allafter.append(q);meshes+=1
            if 'Casing___' in prim.GetName():
                shell=q;tri=indices.reshape(-1,3)
                _,welded=np.unique(np.round(q,6),axis=0,return_inverse=True);f=welded[tri]
                edges=np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]])
                _,edgecounts=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True)
                assert (edgecounts==2).all(),(name,'Open rim')
        assert before==unaffected(),(name,'Unexpected attribute edit')
        p=np.vstack(allbefore);q=np.vstack(allafter)
        assert abs(np.ptp(q[:,2])/np.ptp(p[:,2])-.7)<1e-8
        radius=np.linalg.norm(shell[:,:2],axis=1)
        assert abs(radius.max()-NEW_OUTER)<2e-6 and abs(radius.min()-INNER)<2e-6
        assert abs(np.ptp(shell[:,2])-.651)<2e-6
        stage.GetRootLayer().Save()
        compact=pkg/'compact.usdc';stage.GetRootLayer().Export(str(compact));compact.replace(pkg/usd)
        out=pkg/'output.usdz'
        subprocess.run(['/usr/bin/usdzip',str(out)]+names,cwd=pkg,check=True,capture_output=True)
        check=subprocess.run(['/usr/bin/usdchecker','--arkit',str(out)],capture_output=True,text=True)
        (C/'usdchecker.txt').write_text(check.stdout+check.stderr)
        assert check.returncode==0,(name,check.stdout+check.stderr)
        with zipfile.ZipFile(source) as a,zipfile.ZipFile(out) as b:
            assert all(a.read(n)==b.read(n) for n in names if n!=usd)
        if name=='EmeraldSprout':
            approved=R/'candidate03/mobile/emerald_sprout_badge_mobile.usdz'
            approved_stage=Usd.Stage.Open(str(approved))
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    other=UsdGeom.Mesh(approved_stage.GetPrimAtPath(prim.GetPath()))
                    assert np.array_equal(np.asarray(UsdGeom.Mesh(prim).GetPointsAttr().Get()),np.asarray(other.GetPointsAttr().Get()))
            shutil.copyfile(approved,target)
        else:shutil.copyfile(out,target)
        report=dict(name=name,mesh_count=meshes,rim_width_factor=.8,whole_coin_depth_factor=.7,
                    inner_radius=float(radius.min()),outer_radius=float(radius.max()),shell_depth=float(np.ptp(shell[:,2])),
                    closed_shell=True,matches_live_blender=True,preserved_materials_textures_uv_topology=True,
                    arkit_validation_passed=True,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                    before_bounds=[p.min(0).tolist(),p.max(0).tolist()],after_bounds=[q.min(0).tolist(),q.max(0).tolist()])
        (C/'validation.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(report)
        print(name,'validated',flush=True)
(F/'validation.json').write_text(json.dumps(reports,indent=2)+'\n')
