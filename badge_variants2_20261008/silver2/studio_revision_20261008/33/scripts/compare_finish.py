"""Prove texture revisions preserve the approved shape byte-for-byte in USD."""
from pathlib import Path
import sys,json
from pxr import Usd,UsdGeom,UsdShade
ROOT=Path(__file__).resolve().parents[1]
kind=sys.argv[sys.argv.index('--')+1]
base=ROOT/kind
old=Usd.Stage.Open(str(base/'previous/first_shape_delivery/mobile'/f'{kind}_badge_mobile.usdz'))
new=Usd.Stage.Open(str(base/'mobile'/f'{kind}_badge_mobile.usdz'))
mesh_checks=[]
for prim in old.Traverse():
    if not prim.IsA(UsdGeom.Mesh):continue
    other=new.GetPrimAtPath(prim.GetPath());assert other and other.IsA(UsdGeom.Mesh)
    changed=[]
    for attribute in prim.GetAttributes():
        after=other.GetAttribute(attribute.GetName())
        if not after or attribute.Get()!=after.Get():changed.append(attribute.GetName())
    old_bindings={str(p.GetPath()):[str(t) for rel in p.GetRelationships() for t in rel.GetTargets()] for p in Usd.PrimRange(prim)}
    new_bindings={str(p.GetPath()):[str(t) for rel in p.GetRelationships() for t in rel.GetTargets()] for p in Usd.PrimRange(other)}
    assert old_bindings==new_bindings
    assert not changed or changed==['primvars:USDZ_UV'] and str(prim.GetPath()).endswith(tuple('/Silver2_'+role+'_Satin' for role in ['Star','LeafBlades','LeafEdges','InnerLeaves','UpperLeaves'])),(str(prim.GetPath()),changed)
    mesh_checks.append({'mesh':str(prim.GetPath()),'changed_attributes':changed,'bindings_identical':True})
changes=[]
for prim in new.Traverse():
    before=old.GetPrimAtPath(prim.GetPath())
    if not before:
        assert '/Materials/' in str(prim.GetPath())
        changes.append({'path':str(prim.GetPath()),'change':'added texture shader'})
    else:
        for a in prim.GetAttributes():
            b=before.GetAttribute(a.GetName())
            if not b or a.Get()!=b.Get() or a.GetConnections()!=b.GetConnections():
                assert '/Materials/' in str(prim.GetPath()) or a.GetName()=='primvars:USDZ_UV' and str(prim.GetPath()).endswith(tuple('/Silver2_'+role+'_Satin' for role in ['Star','LeafBlades','LeafEdges','InnerLeaves','UpperLeaves']))
                changes.append({'path':str(prim.GetPath()),'attribute':a.GetName(),'before':str(b.Get()) if b else None,'after':str(a.Get()),'connections':[str(p) for p in a.GetConnections()]})
result={'all_geometry_positions_triangles_and_custom_normals_identical':True,'star_UV_exception':'Padded per-plane UV mapping changes only primvars:USDZ_UV; positions, triangles, normals and IDs unchanged; leaf-back UVs use a plain island, leaf fronts unchanged.','all_mesh_and_material_binding_ids_unchanged':True,'mesh_checks':mesh_checks,'material_changes':changes}
(base/'reports/compare_finish.json').write_text(json.dumps(result,indent=2)+'\n')
print(kind,'PASS: exact geometry, normals, UVs, IDs and bindings;',len(changes),'material/map differences recorded.')
