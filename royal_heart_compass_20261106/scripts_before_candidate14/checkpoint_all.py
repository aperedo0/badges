from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parent
for row in json.loads((R/'gallery.json').read_text()):
 slug=row['slug'];c=R/slug/'candidate11'
 with (c/'checkpoint_log.txt').open('w') as f:
  r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--factory-startup','--python',str(R/'save_compact_blend.py'),'--',slug],stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(slug,'checkpoint failure')
 print(slug,'compact editable checkpoint saved',flush=True)
