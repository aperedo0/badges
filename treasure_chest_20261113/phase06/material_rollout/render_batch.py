from pathlib import Path
import subprocess,os,sys
D=Path(__file__).resolve().parent;B='/Applications/Blender.app/Contents/MacOS/Blender'
for view in sys.argv[1:]:
 log=D/((('final_' if os.environ.get('CHEST_FINAL')=='1' else 'draft_')+view)+'.log')
 with log.open('w') as f:r=subprocess.run([B,'-b','-t','6','-P',str(D/'render.py'),'--',view],stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(),str(log)
 print('COMPLETE',view,flush=True)
