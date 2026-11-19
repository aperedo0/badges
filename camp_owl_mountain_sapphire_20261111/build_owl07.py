"""Build the measured owl as continuous backing pieces with raised ornament."""
from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parent;C=R/'amber_owl/candidate07';P='/Library/Frameworks/Python.framework/Versions/3.11/bin/python3'
steps=[('engine',[R/'tools/badge3d.py',C/'PIECES.json',C]),('edges',[R/'tools/clean_surface_edges.py',C]),('normals',[R/'tools/physical_metal_normals.py',C]),('colors',[R/'tools/enamel_fill.py',C,R/'amber_owl/reference.png',C/'enamel_config.json',C]),('validation',[R/'tools/validate.py',C])]
for name,args in steps:
 with (C/('validation.json' if name=='validation' else name+'.log')).open('w') as log:subprocess.run([P,*map(str,args)],stdout=log,check=True,cwd=R.parent)
 print(name,'complete',flush=True)
print('Measured complete owl candidate passes unchanged standard geometry checks',flush=True)
