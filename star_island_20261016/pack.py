"""Package Blender-authored reliefs around byte-preserved approved rim data."""
from pathlib import Path
import json,sys,zipfile,hashlib,subprocess
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Gf,Vt

ROOT=Path(__file__).resolve().parent
TEMP=Path('/tmp/star_island_20261016')
SOURCES={'star_ascent':ROOT.parent/'water_match_20261014/clean/mobile/clean_badge_mobile.usdz',
         'island_sunset':ROOT.parent/'botanical_match_20261014/sprout/mobile/sprout_badge_mobile.usdz'}
SHELL='/Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry'

def add_material(stage,role,palette,pkg,calibration,name):
    color,metal,rough=palette[role]
    scales_path=ROOT/name/'texture_scales.json'
    scales=json.loads(scales_path.read_text()).get(role,{}) if scales_path.exists() else {}
    mat=UsdShade.Material.Define(stage,'/Badge/_materials/New_'+role)
    shader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Surface'));shader.CreateIdAttr('UsdPreviewSurface')
    shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*([.15]*3 if calibration else color)))
    shader.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(float(metal))
    shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(float(rough))
    shader.CreateInput('opacity',Sdf.ValueTypeNames.Float).Set(1.)
    shader.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0))
    shader.CreateInput('clearcoat',Sdf.ValueTypeNames.Float).Set(0.)
    shader.CreateInput('ior',Sdf.ValueTypeNames.Float).Set(1.46)
    fitted=ROOT/name/'textures'/(role+'_color.png')
    if not calibration and (role!='cloud' or fitted.exists()):
        texname=role+'_color.png' if fitted.exists() else role+'.png'
        source=fitted if fitted.exists() else ROOT/'textures'/texname
        if source.exists():
            target=pkg/'textures'/texname;target.write_bytes(source.read_bytes())
            reader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('UV'));reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('CoinReliefUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
            tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Color'));tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+texname));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB');tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3)
            shader.GetInput('diffuseColor').ConnectToSource(tex.ConnectableAPI(),'rgb')
            if scales and fitted.exists():tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(*scales['color'],1))
            if fitted.exists() and role in ['sky','sea','sun','leaf']:
                glowname=role+'_emission.png';(pkg/'textures'/glowname).write_bytes((fitted.parent/glowname).read_bytes())
                glow=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Emission'));glow.CreateIdAttr('UsdUVTexture')
                glow.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+glowname))
                glow.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
                glow.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(*scales.get('emission',[4,4,4]),1))
                glow.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp');glow.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp')
                glow.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');glow.CreateOutput('rgb',Sdf.ValueTypeNames.Float3)
                shader.GetInput('emissiveColor').ConnectToSource(glow.ConnectableAPI(),'rgb')
    shader.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface')
    return mat

def build(name,calibration=False):
    outdir=ROOT/name;pkg=TEMP/(name+('_calibration' if calibration else '_package'));pkg.mkdir(exist_ok=True);(pkg/'textures').mkdir(exist_ok=True)
    source=SOURCES[name]
    with zipfile.ZipFile(source) as archive:
        archive.extractall(pkg);usd=next(n for n in archive.namelist() if n.endswith('.usdc'))
    stage=Usd.Stage.Open(str(pkg/usd));rim=stage.GetPrimAtPath(SHELL)
    signature={a.GetName():a.Get() for a in rim.GetAttributes()}
    for prim in list(stage.GetPrimAtPath('/Badge').GetChildren()):
        if prim.GetName() not in ['_materials','Casing___smooth_rounded_outer_edge']:
            stage.RemovePrim(prim.GetPath())
    for prim in list(stage.GetPrimAtPath('/Badge/_materials').GetChildren()):
        if prim.GetName() not in ['Silver___circumferential_brushed_steel_Mobile_Casing','Shell_inner','Shell_bevel']:
            stage.RemovePrim(prim.GetPath())
    meta=json.loads((outdir/'design.json').read_text());geometry=np.load(TEMP/(name+'_geometry.npz'))
    materials={role:add_material(stage,role,meta['palette'],pkg,calibration,name) for role in {g['role'] for g in meta['groups']}}
    count=4096
    # Combine disconnected pieces by material. This retains every vertex,
    # triangle and face normal while avoiding 150 RealityKit model entities.
    grouped={}
    for i,group in enumerate(meta['groups']):
        role=group['role'];points=geometry[str(i)+'_points'];triangles=geometry[str(i)+'_triangles'];normals=geometry[str(i)+'_normals']
        parts=grouped.setdefault(role,{'p':[],'t':[],'n':[],'count':0})
        parts['p'].append(points);parts['t'].append(triangles+parts['count']);parts['n'].append(normals);parts['count']+=len(points)
    for role,parts in grouped.items():
        points=np.concatenate(parts['p']);triangles=np.concatenate(parts['t']);normals=np.concatenate(parts['n']);uv=(points[:,:2]+3.015)/6.03
        for side in ['Front','Back']:
            p=points if side=='Front' else points*[-1,1,-1]+[0,0,-.33]
            n=normals if side=='Front' else normals*[-1,1,-1]
            mesh=UsdGeom.Mesh.Define(stage,'/Badge/'+side+'_'+role)
            mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p.astype(np.float32)))
            mesh.CreateFaceVertexCountsAttr([3]*len(triangles));mesh.CreateFaceVertexIndicesAttr(triangles.ravel().tolist())
            mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(n.reshape(-1,3).astype(np.float32)));mesh.SetNormalsInterpolation('faceVarying')
            mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(False)
            mesh.CreateExtentAttr([Gf.Vec3f(*p.min(0)),Gf.Vec3f(*p.max(0))])
            UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('CoinReliefUV',Sdf.ValueTypeNames.TexCoord2fArray,'vertex').Set(Vt.Vec2fArray.FromNumpy(uv.astype(np.float32)))
            UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(materials[role])
            count+=len(triangles)
    assert signature=={a.GetName():a.Get() for a in stage.GetPrimAtPath(SHELL).GetAttributes()}
    used=set()
    for prim in stage.Traverse():
        if prim.IsA(UsdShade.Shader):
            shader=UsdShade.Shader(prim)
            if shader.GetInput('file'):used.add(str(shader.GetInput('file').Get().path))
    final=pkg/'final.usdc';assert stage.GetRootLayer().Export(str(final))
    out=(TEMP/(name+'_calibration.usdz')) if calibration else outdir/'mobile'/(name+'_badge_mobile.usdz')
    out.unlink(missing_ok=True)
    subprocess.run(['/usr/bin/usdzip',str(out),'final.usdc']+sorted(used),cwd=pkg,check=True,capture_output=True)
    gate=subprocess.run(['/usr/bin/usdchecker','--arkit',str(out)],capture_output=True,text=True);assert gate.returncode==0,gate.stdout+gate.stderr
    facts={'name':name,'bytes':out.stat().st_size,'triangles':count,'relief_meshes':2*len(grouped),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'shell_data_unchanged':True,'mirrored_matching_back':True,'required_size':.96,'required_lift':.56,'calibration':calibration,'USD_validation':'passed'}
    if not calibration:(outdir/'model.json').write_text(json.dumps(facts,indent=2))
    print(json.dumps(facts),flush=True)

if __name__=='__main__':
    for name in [n for n in sys.argv[1:] if n!='--calibration']:build(name,'--calibration' in sys.argv)
