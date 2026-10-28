"""Copy the exact saved Archer field maps for the trophy refinement."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent
out=ROOT/'candidate04';(out/'textures').mkdir(parents=True,exist_ok=True);(out/'mobile').mkdir(exist_ok=True)
for suffix in ['color','roughness']:
 name='field_'+suffix+'.png'
 shutil.copyfile(ROOT.parent/'emerald_archer_20261023/candidate02/textures'/name,out/'textures'/name)
print('Exact Archer field maps copied')
