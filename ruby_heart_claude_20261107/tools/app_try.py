"""Install a Ruby Heart candidate in Badge Studio Preview, build, launch and capture poses.

Usage: app_try.py CANDIDATE_DIR [--no-build] [--poses front,early_turn,side_left,back,side_right]
The candidate dir holds model.usdz. The preview data set's previous model is
backed up once to runtime_backup/preview_coin_before_claude.usdz.
"""
import sys, subprocess, time, shutil, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path('/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107')
PREVIEW = Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025/preview')
DATASET = PREVIEW / 'ScreenTime/SupportingFiles/Assets.xcassets/Badge3DPreviewRubyHeart.dataset/coin.usdz'
UDID = 'C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
BUNDLE = 'com.antonioperedo.badgestudio.preview'
DERIVED = Path('/tmp/forge_tide_derived_20261103')
APP = DERIVED / 'Build/Products/Debug-iphonesimulator/ScreenTimeUI.app'
AXE = '/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
POSES = dict(front=0, early_turn=68, side_left=94.2528, back=132.5056, side_right=170.7583)

def header_y(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    r, g, b = a[500:2100, 950:1150].transpose(2, 0, 1)
    counts = ((b - r > 40) & (b - g > 20) & (b > 120) & (r > 50) & (g > 80)).sum(1)
    ys = np.where(counts > 8)[0]
    if len(ys) <= 8:
        raise ValueError('picker not visible')
    return float(np.median(ys) + 500)

def shot(path):
    path = Path(path); path.unlink(missing_ok=True)
    subprocess.run(['xcrun', 'simctl', 'io', UDID, 'screenshot', str(path)], check=True, capture_output=True)
    return path

def stable_shot(path):
    time.sleep(1.0); prev = None; stable = 0
    for _ in range(20):
        shot(path)
        try:
            y = header_y(path)
        except ValueError:
            prev = None; stable = 0; time.sleep(.4); continue
        stable = stable + 1 if prev is not None and abs(y - prev) <= 1 else 0
        if stable >= 2:
            return path
        prev = y; time.sleep(.3)
    raise RuntimeError('screen did not settle')

def swipe(y0, y1, delta=2):
    args = [AXE, 'swipe', '--start-x', '200', '--start-y', str(y0), '--end-x', '200', '--end-y', str(y1),
                    '--duration', '1', '--delta', str(delta), '--udid', UDID]
    for attempt in range(3):
        try:
            subprocess.run(args, check=True, capture_output=True, timeout=30); return
        except subprocess.TimeoutExpired:
            subprocess.run(['pkill', '-f', 'axe swipe']); time.sleep(3)
    raise RuntimeError('swipe failed 3 times')

def main():
    cand = Path(sys.argv[1]).resolve()
    build = '--no-build' not in sys.argv
    poses = list(POSES)
    if '--poses' in sys.argv:
        poses = sys.argv[sys.argv.index('--poses') + 1].split(',')
    out = cand / 'app'; out.mkdir(exist_ok=True)
    model = cand / 'model.usdz'
    backup = ROOT / 'runtime_backup/preview_coin_before_claude.usdz'
    if not backup.exists():
        shutil.copy2(DATASET, backup)
    shutil.copy2(model, DATASET)
    if build:
        log = out / 'build.log'
        args = ['xcodebuild', '-project', str(PREVIEW / 'ScreenTime.xcodeproj'), '-scheme', 'ScreenTime-UIOnly',
                '-configuration', 'Debug', '-destination', 'id=' + UDID, '-derivedDataPath', str(DERIVED),
                '-disableAutomaticPackageResolution', 'build']
        with log.open('w') as f:
            r = subprocess.run(args, stdout=f, stderr=subprocess.STDOUT)
        if r.returncode:
            print(log.read_text()[-6000:]); raise SystemExit('build failed')
        subprocess.run(['xcrun', 'simctl', 'install', UDID, str(APP)], check=True)
        print('built and installed', flush=True)
    console = out / 'console.log'
    with console.open('w') as h:
        proc = subprocess.Popen(['xcrun', 'simctl', 'launch', '--console-pty', '--terminate-running-process', UDID, BUNDLE,
                                 '-hasCompletedOnboarding', 'YES', '-CoinBadgePreview', 'rubyHeart',
                                 '-BadgePreviewBaseline', 'NO', '-BadgePreviewClothFinish', 'NO'],
                                stdin=subprocess.DEVNULL, stdout=h, stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(12)
    container = Path(subprocess.check_output(['xcrun', 'simctl', 'get_app_container', UDID, BUNDLE, 'data'], text=True).strip())
    cached = container / 'tmp' / 'Badge3DPreviewRubyHeart.usdz'
    for _ in range(20):
        if cached.exists() and cached.read_bytes() == model.read_bytes():
            break
        time.sleep(1)
    same = cached.exists() and cached.read_bytes() == model.read_bytes()
    print('app loaded this candidate:', same, flush=True)
    swipe(250, 750)
    rest = stable_shot(out / 'front.png'); y_rest = header_y(rest)
    results = dict(model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(), loaded=same, front_header=y_rest)
    for pose in poses:
        if pose == 'front':
            continue
        swipe(250, 750); stable_shot(out / '_rest.png')
        target = y_rest - POSES[pose] * 3
        swipe(600, 600 - POSES[pose] - 10)
        p = stable_shot(out / f'{pose}.png')
        for _ in range(8):
            y = header_y(p)
            if abs(y - target) <= 1.5:
                break
            c = (y - target) / 3; c += 10 if c > 0 else -10
            swipe(600, 600 - c, 1); p = stable_shot(out / f'{pose}.png')
        results[pose] = header_y(p)
    swipe(250, 750); stable_shot(out / '_rest.png')
    (out / 'capture.json').write_text(json.dumps(results, indent=2))
    log = console.read_text(errors='ignore')
    print('\n'.join(l for l in log.splitlines() if 'heart foil' in l or 'gem' in l.lower())[-2000:])

if __name__ == '__main__':
    main()
