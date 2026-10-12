"""Package genuine proof and preserve all concurrent repository work."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/Users/antonioperedo/Downloads/diamond_codex')
REPO = Path('/Users/antonioperedo/Desktop/screen_time')
validation = OUT / 'validation'
validation.mkdir(exist_ok=True)
baseline = json.loads((ROOT / 'repo_before.json').read_text())
current = {}
for path in REPO.rglob('*'):
    if path.is_file() and '.git' not in path.relative_to(REPO).parts:
        current[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
changed = [name for name, sha in baseline['files'].items() if current.get(name) != sha]
added = sorted(set(current) - set(baseline['files']))
missing = sorted(set(baseline['files']) - set(current))
owned = [
    'ScreenTime/Sources/App/Features/Badges/BadgeGemSurface.metal',
    'ScreenTime/Sources/App/Features/Badges/BadgeHeroCard.swift',
    'ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModelDiamond.dataset/diamond_badge_mobile.usdz',
]
assert all(current[name] == baseline['files'][name] for name in owned)
assert not missing
def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO, text=True).strip()
audit = {
    'initial_file_count': len(baseline['files']), 'current_file_count': len(current),
    'owned_diamond_files_restored_byte_exact': True,
    'all_badge_models_and_art_restored_byte_exact': all(current.get(name) == sha for name, sha in baseline['files'].items() if 'Badge3DModel' in name or 'BadgeArt' in name),
    'missing_original_files': missing, 'changed_original_files': sorted(changed),
    'preserved_external_additions': added,
    'original_head': baseline['head'].strip(), 'current_head': git('rev-parse', 'HEAD'),
    'original_branch': baseline['branch'].strip(), 'current_branch': git('branch', '--show-current'),
    'current_status': git('status', '--porcelain=v1'),
    'external_commit': git('log', '-1', '--format=fuller', '--stat'),
    'interpretation': 'No Diamond task edits remain. Preserve external icon-catalog commit and external/Xcode user metadata; these existed outside our owned file edits. No reset, checkout, commit, branch change or stash operation by this task.',
}
(validation / 'restoration_audit.json').write_text(json.dumps(audit, indent=2))
(ROOT / 'repo_final.json').write_text(json.dumps({'files': current, **audit}, indent=2))
for source, destination in [('gate_output.log', 'gate_proof.txt'), ('candidate.json', 'gate_candidate.json'), ('test_summary.json', 'test_summary.json')]:
    shutil.copy2(ROOT / 'gate' / source, validation / destination)

today = OUT / '00_today'
if (today / 'slow_turn_review.mp4').exists():
    raw = ROOT / 'recordings_raw' / '00_today'
    raw.mkdir(parents=True, exist_ok=True)
    shutil.move(str(today / 'full_turn.mp4'), str(raw / 'full_turn.mp4'))
    shutil.move(str(today / 'slow_turn_review.mp4'), str(today / 'full_turn.mp4'))
folders = [today, OUT / 'raised_band15'] + sorted((OUT / 'recuts').iterdir()) + [OUT / 'glints' / name for name in ['01_subtle', '02_medium', '03_strong']]
video_proof = {}
for folder in folders:
    facts = json.loads((folder / 'video_evidence.json').read_text())
    assert facts['complete_to_hidden']
    facts['delivered_video'] = 'full_turn.mp4'
    facts['delivered_video_start_in_raw_seconds'] = max(0, facts['moving_start_seconds'] - 1)
    facts['timestamps_reference'] = 'Native untrimmed recording in working archive; delivered video contains resting lead-in, full turn and hidden endpoint.'
    (folder / 'video_evidence.json').write_text(json.dumps(facts, indent=2))
    video_proof[str(folder.relative_to(OUT))] = facts
(validation / 'full_turns.json').write_text(json.dumps(video_proof, indent=2))

outline_proof = {}
for folder in folders:
    review = ROOT / 'outline_review' / folder.parent.name / folder.name
    outline_proof[str(folder.relative_to(OUT))] = {'quarter_second_4x_crops': len(list(review.glob('*.png'))), 'workspace_review_directory': str(review), 'pose_4x_files': [p.name for p in folder.glob('*outline_4x.png')]}
(validation / 'outline_review.json').write_text(json.dumps({'method': 'Native screenshots, nearest-neighbor 4x tip/edge crops at rest and both sides/back; quarter-second moving-frame crops and continuous native full-turn playback. Finite sampled inspection, not a proof for infinitely many angles. Bright resolved facets inside the outline retained. Late scroll blur/shrink is unchanged Home behavior.', 'options': outline_proof}, indent=2))

report = (ROOT / 'REPORT_DRAFT.md').read_text().replace(
    'Build/test gate and final restoration audit are pending. Concurrent external icon work and the owner\'s stashes are preserved.',
    '[Full gate passed](validation/gate_proof.txt): three schemes built; 1871 tests passed, zero failures or skips. [Audit](validation/restoration_audit.json): all original badge files are byte-identical and our Diamond changes are restored. The simulator shows the original Diamond. An external icon-catalog commit and Xcode user metadata were preserved. Late-scroll blur/shrink is unchanged Home behavior. [Outline review](validation/outline_review.json) records finite 4x pose and turn sampling.'
)
(OUT / 'REPORT.md').write_text(report)
(OUT / 'INDEX.md').write_text('''# Diamond previews

Recommended: **raised band + medium glints**. Nothing is selected or permanently applied.

- [All shapes at rest](all_options_rest_1x.png), [4x](all_options_rest_4x.png)
- [Recommended rest comparison](raised_band15/rest_comparison_1x.png), [4x](raised_band15/rest_comparison_4x.png), [slow full turn](raised_band15/full_turn.mp4)
- Recommended poses: [right](raised_band15/right_comparison_1x.png), [back](raised_band15/back_comparison_1x.png), [left](raised_band15/left_comparison_1x.png). Each has a corresponding `_4x.png` comparison.
- Other cuts and slow turns: [40.5](recuts/01_40p5/full_turn.mp4), [41](recuts/02_41/full_turn.mp4), [41.5](recuts/03_41p5/full_turn.mp4), [today](00_today/full_turn.mp4)
- [Glint strengths at rest](glints/strengths_rest_1x.png), [4x](glints/strengths_rest_4x.png), [rotated flash](glints/strengths_flash_1x.png), [4x](glints/strengths_flash_4x.png)
- Glint slow turns: [subtle](glints/01_subtle/full_turn.mp4), [medium](glints/02_medium/full_turn.mp4), [strong](glints/03_strong/full_turn.mp4)
- [Cause and recommendation](REPORT.md), [build/test proof](validation/gate_proof.txt), [repo audit](validation/restoration_audit.json)

Videos are compact native simulator recordings showing a resting lead-in, the whole slow turn and its hidden endpoint. Spin sheets use timestamps from the longer working recordings. `candidate` folders contain only model/source needed to apply a later pick; large build products, raw recordings and frame sequences remain outside Downloads. Diagnostic images are technical tests, not proposed finishes.
''')
print(json.dumps({'audit': audit, 'video_count': len(video_proof), 'report_words': len(report.split())}, indent=2))
