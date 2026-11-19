import sys,os
from pathlib import Path
D=Path(__file__).resolve().parent;S=D.parent/'surface_definition';code=(S/'render.py').read_text()
code=code.replace("D=Path(__file__).resolve().parent;",'D=Path('+repr(str(S))+');',1)
code=code.replace("if view in ['clay','mask']:","""body=sc.objects['Master Chest Body Envelope'];mat=next(m for m in body.data.materials if m and m.name.startswith('Wood Lab '));mat.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=0
if view in ['clay','mask']:""")
code=code.replace("('_final' if os.environ.get('WOOD_FINAL')=='1' else '')","'_nospec'")
exec(compile(code,'reused_diagnostic_renderer','exec'))
