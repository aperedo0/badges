"""Run the existing live builder, inspection, and exporter sequentially."""
from pathlib import Path
import sys,subprocess,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'water_match_20261014'))
from blender_live import command
PYUSD='/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13'
for key in sys.argv[1:]:
 (ROOT/'active_badge.txt').write_text(key)
 print(command('execute_code',{'code':(ROOT/'build_live.py').read_text()}),flush=True)
 subprocess.run([sys.executable,str(ROOT/'inspect_live.py'),key],check=True)
 for script in ['pack.py','validate.py']:subprocess.run([PYUSD,'-I',str(ROOT/script),key],check=True)
 subprocess.run([sys.executable,str(ROOT/'install_preview_asset.py'),key],check=True)
