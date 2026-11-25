"""Package the four verified solids; run with Blender's bundled Python (OpenUSD)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json, sys
import numpy as np
from girdle import polished_border
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdUtils

root = Path(__file__).resolve().parents[1]
candidate = root / (sys.argv[1] if len(sys.argv)>1 else json.loads((root/'design.json').read_text())['candidate'])
data = json.loads((candidate/'geometry.json').read_text())

def material(stage, name, color, metallic, roughness, ior):
    mat = UsdShade.Material.Define(stage, '/Badge/Materials/' + name)
    surf = UsdShade.Shader.Define(stage, mat.GetPath().AppendChild('Surface'))
    surf.CreateIdAttr('UsdPreviewSurface')
    surf.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    for key, value in [('metallic', metallic), ('roughness', roughness), ('ior', ior)]:
        surf.CreateInput(key, Sdf.ValueTypeNames.Float).Set(value)
    mat.CreateSurfaceOutput().ConnectToSource(surf.ConnectableAPI(), 'surface')
    return mat, surf

with TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    layer = tmp/'RubyHourglass.usdc'
    stage = Usd.Stage.CreateNew(str(layer))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, 1.)
    base = UsdGeom.Xform.Define(stage,'/Badge')
    stage.SetDefaultPrim(base.GetPrim())
    ruby, _ = material(stage,'CrestGem_Ruby',(.35,.008,.015),0.,.06,1.77)
    if (candidate/'facing.json').exists():
        settings=json.loads((candidate/'facing.json').read_text())
        facing, fs=material(stage,'Polished_Ruby_Facing',tuple(settings['color']),settings['metallic'],settings['roughness'],1.77)
        if settings.get('polished_border'):
            girdle,_=material(stage,'Ruby_Polished_Girdle',tuple(settings['color']),settings['metallic'],settings['roughness'],1.77)
        fs.CreateInput('opacity',Sdf.ValueTypeNames.Float).Set(settings['opacity'])
    bronze_color=tuple(settings.get('bronze',[.19,.115,.077])) if (candidate/'facing.json').exists() else (.19,.115,.077)
    bronze, surface = material(stage,'Brushed_Bronze',bronze_color,.88,.34,1.5)
    (tmp/'BronzeBrush.png').write_bytes((candidate/'BronzeBrush.png').read_bytes())
    uv = UsdShade.Shader.Define(stage, bronze.GetPath().AppendChild('UV'))
    uv.CreateIdAttr('UsdPrimvarReader_float2')
    uv.CreateInput('varname', Sdf.ValueTypeNames.Token).Set('st')
    tex = UsdShade.Shader.Define(stage, bronze.GetPath().AppendChild('BrushRoughness'))
    tex.CreateIdAttr('UsdUVTexture')
    tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('BronzeBrush.png'))
    tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(uv.ConnectableAPI(),'result')
    tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('raw')
    surface.GetInput('roughness').ConnectToSource(tex.ConnectableAPI(),'r')
    for name, obj in data.items():
        mesh = UsdGeom.Mesh.Define(stage,'/Badge/'+name)
        points = np.asarray(obj['points'],dtype=np.float32)
        triangles = np.asarray(obj['triangles'])
        normals=np.asarray(obj['normals'],dtype=np.float32)
        if 'uv' not in obj:
            # RealityKit imports vertex normals reliably. Split hard edges so a
            # polished facet can never interpolate the normal of its neighbor.
            corners=points[triangles].reshape(-1,3)
            shading_normals=np.repeat(normals,3,axis=0)
            pairs,indices=np.unique(np.column_stack((corners,shading_normals)),axis=0,return_inverse=True)
            points=pairs[:,:3].copy()
            normals=pairs[:,3:].copy()
            triangles=indices.reshape(-1,3)
        mesh.CreatePointsAttr(points)
        mesh.CreateFaceVertexCountsAttr([3]*len(triangles))
        mesh.CreateFaceVertexIndicesAttr(triangles.ravel())
        mesh.CreateExtentAttr([Gf.Vec3f(*map(float,points.min(axis=0))),Gf.Vec3f(*map(float,points.max(axis=0)))])
        mesh.CreateSubdivisionSchemeAttr('none')
        mesh.CreateNormalsAttr(normals)
        mesh.SetNormalsInterpolation('vertex')
        if 'uv' in obj:
            UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('st',Sdf.ValueTypeNames.TexCoord2fArray,'vertex').Set(np.asarray(obj['uv'],dtype=np.float32))
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(bronze if 'uv' in obj else (facing if name.endswith('Facing') else ruby))
        if name.endswith('Facing') and settings.get('polished_border'):
            border=polished_border(name,obj)
            inner=sorted(set(range(len(triangles)))-set(border))
            api=UsdShade.MaterialBindingAPI(mesh)
            for subset_name,selection,mat in [('Girdle',border,girdle),('Crown',inner,facing)]:
                subset=api.CreateMaterialBindSubset(subset_name,selection)
                UsdShade.MaterialBindingAPI.Apply(subset.GetPrim()).Bind(mat)
            api.SetMaterialBindSubsetsFamilyType(UsdGeom.Tokens.partition)
    stage.GetRootLayer().Save()
    dest = candidate/'model.usdz'
    assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(layer)),str(dest))
    reread = Usd.Stage.Open(str(dest))
    assert reread and len([p for p in reread.Traverse() if p.IsA(UsdGeom.Mesh)])==len(data)
    print(dest, dest.stat().st_size)
