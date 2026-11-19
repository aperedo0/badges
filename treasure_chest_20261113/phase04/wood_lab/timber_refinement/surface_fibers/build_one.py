import bpy,sys
from pathlib import Path
D=Path(__file__).resolve().parent
KEY=sys.argv[sys.argv.index('--')+1]
exec(compile((D.parent/'grain_hierarchy/apply_layers.py').read_text(),'reused_plank_builder','exec'))
