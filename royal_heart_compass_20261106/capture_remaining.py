"""Resume missing measured views without repeating saved successful captures."""
from pathlib import Path
import sys,json,subprocess,os
R=Path(__file__).resolve().parent;slug,mode=sys.argv[1:3];V=R/slug/mode/('review_baseline' if os.environ.get('BADGE_BASELINE')=='1' else 'review')
for pose in ['front','early_turn','side_left','back','side_right','full_turn']:
 file=V/'pose_alignment.json';done=json.loads(file.read_text()) if file.exists() else {}
 if pose in done and (V/(pose+'.png')).is_file():continue
 subprocess.run([sys.executable,str(R/'capture_pose.py'),slug,mode,pose],check=True)
