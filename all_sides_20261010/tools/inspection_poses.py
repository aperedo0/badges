import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
selection_path=Path(sys.argv[sys.argv.index('--selection')+1]) if '--selection' in sys.argv else ROOT/'selection.json'
selection=json.loads(selection_path.read_text())
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if '--selection' in args:
 i=args.index('--selection');args=args[:i]+args[i+2:]
tiers=[a for a in args if not a.startswith('--')] or list(selection)
for tier in tiers:
 w=Path(MANIFEST[tier]['work'])
 for version in ['current','updated']+(['tilted','darker'] if tier=='gold' and '--old-gold-tests' in sys.argv else []):
  number=selection[tier] if version=='updated' else {'tilted':'08','darker':'09'}.get(version)
  source=next((w/'source/installed').glob('*.usd*')) if version=='current' else next((w/'candidates'/number/'usd').glob('*.usd*'))
  if version!='current' and (source.parent/'compacted.usdc').exists():source=source.parent/'compacted.usdc'
  original=Usd.Stage.Open(str(source))
  for pose,degrees in ([('front',0),('back',180)] if version=='tilted' else [('front',0)] if version=='darker' else [('right',-90),('back',180),('left',90)]):
   out=ROOT/'inspection_models'/version/tier/pose;out.mkdir(parents=True,exist_ok=True)
   layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(original.GetRootLayer());st=Usd.Stage.Open(layer)
   # Resolve textures before moving the independent testing layer; never save source layers.
   for prim in st.Traverse():
    for a in prim.GetAttributes():
     if a.GetTypeName()==Sdf.ValueTypeNames.Asset:
      value=a.Get()
      if value and value.path:
       filename=Path(value.path).name;matches=list(source.parent.rglob(filename))
       assert len(matches)==1,(source,value.path,matches)
       texture=out/'textures'/filename;texture.parent.mkdir(exist_ok=True);shutil.copyfile(matches[0],texture)
       a.Set(Sdf.AssetPath('textures/'+filename))
   angle=np.deg2rad(degrees);rot=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
   for prim in [q for q in st.Traverse() if q.IsA(UsdGeom.Mesh)]:
    p,f,n,m,uv=read_mesh(prim);write_mesh(st,prim.GetPath(),p@rot.T,f,n@rot.T,m,uv)
   layer.Export(str(out/'badge.usdc'));loaded=Sdf.Layer.FindOrOpen(str(out/'badge.usdc'));loaded.Reload(True);st=Usd.Stage.Open(loaded)
   finish(tier,w,out,st,[{'inspection_only':True,'angle_degrees':degrees,'purpose':'Full-size in-app inspection under unchanged studio lighting. Final model remains upright/front facing; actual scrolling is captured separately.','source_version':version,'source_candidate':number or 'installed'}])
