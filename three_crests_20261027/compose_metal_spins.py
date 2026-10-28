"""Put the three actual simulator recordings beside one another for review."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parent
keys=['crescent_ocean','mountain_crest','winged_sword'];args=['/opt/homebrew/bin/ffmpeg','-y','-loglevel','error'];filters=[]
for index,key in enumerate(keys):
 R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();video=C/'full_turn.mp4'
 stream=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(video)]))['streams'][0]
 width,height=stream['width'],stream['height'];ch=int(height*.42)//2*2;cw=int(ch*360/510)//2*2;left=(width-cw)//2;top=int(height*.04)//2*2
 # New refinement recordings turn near the beginning; older recordings
 # include a longer initial pause before the gesture.
 args+=(['-ss','2'] if (C/'refinement.json').exists() else ['-sseof','-12'])+['-i',str(video)]
 filters.append(f'[{index}:v]fps=15,trim=duration=12,setpts=PTS-STARTPTS,crop={cw}:{ch}:{left}:{top},scale=360:510,tpad=stop_mode=clone:stop_duration=12[v{index}]')
filters.append('[v0][v1][v2]hstack=inputs=3[out]')
args+=['-filter_complex',';'.join(filters),'-map','[out]','-an','-t','12','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'metal_glints.mp4')]
subprocess.run(args,check=True);print(ROOT/'metal_glints.mp4')
