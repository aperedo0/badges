"""Run one operation only after its pacing guard succeeds."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parent
seconds,action,*command=sys.argv[1:]
if command and command[0]=='--':command=command[1:]
if not command:raise SystemExit('Need an exact command argument list')
result=subprocess.run([sys.executable,str(R/'work_guard.py'),seconds,action])
if result.returncode:raise SystemExit(result.returncode)
raise SystemExit(subprocess.run(command).returncode)
