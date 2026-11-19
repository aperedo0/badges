"""Owner render: full resolution front from the app, an all angles sheet, and a turning video.

Usage: make_render.py CANDIDATE_DIR OUT_PREFIX   (writes OUT_PREFIX front.png, angles.png, turn.mp4)
"""
import sys, subprocess, time, signal
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/skills/badge-fresh-review/scripts')
import review_pack as RP
UDID = 'C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
AXE = '/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
cand = Path(sys.argv[1]); out = sys.argv[2]
app = cand / 'app'
front = Image.open(app / 'front.png').convert('RGB')
a = np.asarray(front).astype(int)
m = ((a.max(2) - a.min(2)) > 25) | (a.max(2) > 140)
m[:150] = False; m[1450:] = False; m[:, :150] = False; m[:, -150:] = False
rows = np.nonzero(m.sum(1) > 3)[0]; gaps = np.nonzero(np.diff(rows) > 15)[0]
y0 = rows[0]; y1 = rows[gaps[0]] if len(gaps) else rows[-1]
cols = np.nonzero(m[y0:y1].sum(0) > 2)[0]
cx, cy = (cols[0] + cols[-1]) / 2, (y0 + y1) / 2; h = (y1 - y0) * 1.18
w = h * 0.8
front.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).save(out + ' front.png')
names = [('front', 'front'), ('early_turn', 'turning'), ('side_left', 'side'), ('back', 'back'), ('side_right', 'other side')]
tiles = []
for f, label in names:
    t = RP.crop_badge_auto(str(app / (f + '.png'))).resize((520, 520), Image.LANCZOS)
    d = ImageDraw.Draw(t); d.text((10, 10), label, fill=(255, 255, 255)); tiles.append(t)
sheet = Image.new('RGB', (520 * len(tiles), 520))
for i, t in enumerate(tiles): sheet.paste(t, (i * 520, 0))
sheet.save(out + ' angles.png')
# turning video: record while scrolling slowly through the full turn, then crop around the badge
raw = str(cand / 'app' / 'turn_raw.mp4')
if '--video-only' not in sys.argv: pass
subprocess.run([AXE, 'swipe', '--start-x', '200', '--start-y', '250', '--end-x', '200', '--end-y', '750', '--duration', '1', '--delta', '2', '--udid', UDID], capture_output=True, timeout=40)
time.sleep(2)
rec = subprocess.Popen(['xcrun', 'simctl', 'io', UDID, 'recordVideo', '--codec=h264', '--force', raw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
subprocess.run([AXE, 'swipe', '--start-x', '200', '--start-y', '640', '--end-x', '200', '--end-y', '442', '--duration', '7', '--delta', '1', '--udid', UDID], capture_output=True, timeout=60)
time.sleep(2)
subprocess.run([AXE, 'swipe', '--start-x', '200', '--start-y', '442', '--end-x', '200', '--end-y', '640', '--duration', '7', '--delta', '1', '--udid', UDID], capture_output=True, timeout=60)
time.sleep(1.5)
rec.send_signal(signal.SIGINT); rec.wait(timeout=30)
H = front.height; Wd = front.width
crop = f"crop={int(Wd * 0.80)}:{int(H * 0.36)}:{int(Wd * 0.10)}:{int(H * 0.035)}"
subprocess.run(['/opt/homebrew/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-vf', crop + ',scale=720:-2', '-pix_fmt', 'yuv420p', out + ' turning.mp4'], check=True)
print('wrote', out + ' front.png', out + ' angles.png', out + ' turning.mp4')
