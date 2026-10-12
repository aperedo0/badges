import sys
from pxr import Usd, UsdShade
for path in sys.argv[1:]:
    st = Usd.Stage.Open(path); seen = []
    for prim in st.Traverse():
        if prim.IsA(UsdShade.Shader) and UsdShade.Shader(prim).GetIdAttr().Get() == 'UsdUVTexture':
            sh = UsdShade.Shader(prim); vals = {}
            for n in ['file', 'sourceColorSpace', 'scale', 'bias']:
                i = sh.GetInput(n)
                if i and i.Get() is not None: vals[n] = str(i.Get()).replace('@', '')
            seen.append((prim.GetPath().pathString.split('/')[-2] + '/' + prim.GetName(), vals))
    print('==', path.split('/')[-2]); [print('  ', a, b) for a, b in seen if 'color' in b.get('file', '').lower() or 'emissive' in b.get('file', '').lower()]
