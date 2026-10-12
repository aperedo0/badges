import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/07';out.mkdir(exist_ok=True)
assert not (out/'usd').exists()
shutil.copytree(w/'candidates/06/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'))
mat=st.GetDefaultPrim().GetPath().AppendPath('Materials/PlatinumKnot_TexturedWalls_NoGlow')
s=UsdShade.Shader.Get(st,mat.AppendChild('Surface'));s.GetInput('roughness').Set(.88)
tex=UsdShade.Shader.Get(st,mat.AppendChild('diffuseColor'))
assert tex and tex.GetIdAttr().Get()=='UsdUVTexture'
# Candidate05's wall color was verified clean at the formerly failing angle.
# A multiplicative texture bounded by that exact RGB preserves the brushing
# without allowing any texel to exceed the proven plain-wall reflectance.
tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(.045,.05,.06,1))
tex.CreateInput('bias',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(0,0,0,0))
finish('platinum',w,out,st,[{'method':'Textured wall reflectance is bounded by the RGB and roughness of candidate05, which passed the oblique edge check. Color texture remains connected through BadgeUV; no wall emission. Thin bevel lips retain the same finish. Main front and rear texture and all geometry are unchanged from06.',
 'maximum_wall_color':[.045,.05,.06],'wall_roughness':.88}])
