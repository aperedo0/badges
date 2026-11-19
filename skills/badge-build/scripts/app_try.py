"""Install a badge candidate in Badge Studio Preview, build, launch and capture poses. Python 3.11.

Usage: app_try.py CANDIDATE_DIR DATASET KEY [--no-build] [--poses front,early_turn,side_left,back,side_right]
  DATASET  the preview data set, Badge3DPreview<Key>, e.g. Badge3DPreviewSapphireTeardrop
  KEY      the preview key, e.g. sapphireTeardrop (DATASET must be "Badge3DPreview" + KEY with a capital first letter)
The candidate dir holds model.usdz; captures go to CANDIDATE_DIR/app (front.png, side_left.png, back.png, ...).
--no-build relaunches the app built last time: it shows whichever model that build packed, so use it only to
recapture the same candidate. The data set's previous model is backed up once to
CANDIDATE_DIR/../runtime_backup/preview_none.usdz.

A new badge needs three things in the preview first (the script checks them and stops if one is missing):
  1. the data set folder Assets.xcassets/<DATASET>.dataset with a Contents.json (copy a neighbour's) and coin.usdz;
  2. the key in PrivateBadgePreview.items in Badge3DLiveBadge.swift;
  3. for a floating shape, the data set in a `.neutral` line of look(forDatasetName:) in the same file (otherwise
     it gets the coin placement, size 0.96 and lift 0.56, and sits too high).
The script stops when the app did not load this candidate, rather than capturing another badge.
"""
import sys, subprocess, time, shutil, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(sys.argv[1]).resolve().parent
PREVIEW = Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025/preview')
DATASET = PREVIEW / f'ScreenTime/SupportingFiles/Assets.xcassets/{sys.argv[2]}.dataset/coin.usdz'
UDID = 'C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
BUNDLE = 'com.antonioperedo.badgestudio.preview'
DERIVED = Path.home() / 'Library/Developer/Xcode/DerivedData/badge_preview_skill'   # kept between runs: incremental builds
APP = DERIVED / 'Build/Products/Debug-iphonesimulator/ScreenTimeUI.app'
AXE = '/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
POSES = dict(front=0, early_turn=68, turn45=75.1, side_left=94.2528, turn135=113.4, back=132.5056, turn225=151.6, side_right=170.7583, turn315=189.9)

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
    key, dataset = sys.argv[3], sys.argv[2]
    swift = (PREVIEW / 'ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift').read_text()
    problems = []
    if dataset != 'Badge3DPreview' + key[:1].upper() + key[1:]:
        problems.append(f'DATASET {dataset} does not match KEY {key} (expected Badge3DPreview{key[:1].upper() + key[1:]})')
    if not DATASET.parent.is_dir():
        problems.append(f'no data set folder {DATASET.parent} (copy a neighbour\'s Contents.json and coin.usdz)')
    if f'"{key}":' not in swift:
        problems.append(f'key "{key}" is not in PrivateBadgePreview.items (the app would show Silver)')
    if f'"{dataset}"' not in swift:
        print(f'note: {dataset} is on no placement line: it gets the coin placement (size 0.96, lift 0.56). '
              'A floating shape needs a .neutral line.', flush=True)
    if problems:
        raise SystemExit('preview not set up for this badge:\n  ' + '\n  '.join(problems))
    backup = ROOT / 'runtime_backup/preview_none.usdz'
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists() and DATASET.exists():
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
                                 '-hasCompletedOnboarding', 'YES', '-CoinBadgePreview', sys.argv[3],
                                 '-BadgePreviewBaseline', 'NO', '-BadgePreviewClothFinish', ('YES' if '--cloth' in sys.argv else 'NO')],
                                stdin=subprocess.DEVNULL, stdout=h, stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(12)
    container = Path(subprocess.check_output(['xcrun', 'simctl', 'get_app_container', UDID, BUNDLE, 'data'], text=True).strip())
    cached = container / 'tmp' / (sys.argv[2] + '.usdz')
    for _ in range(20):
        if cached.exists() and cached.read_bytes() == model.read_bytes():
            break
        time.sleep(1)
    same = cached.exists() and cached.read_bytes() == model.read_bytes()
    print('app loaded this candidate:', same, flush=True)
    if not same:
        raise SystemExit('the app did not load this candidate: no captures taken (check the key, the data set and '
                         'that the build packed this model; --no-build reuses the previous build)')
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
    print('\n'.join(l for l in log.splitlines() if any(w in l.lower() for w in ('error', 'fail', 'gem', 'stone prepared', 'cloth', 'usdz')))[-2000:])

if __name__ == '__main__':
    main()
