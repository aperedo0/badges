import subprocess, sys, json
from pathlib import Path
r = Path(__file__).resolve().parents[1]
blender = '/Applications/Blender.app/Contents/MacOS/Blender'
def run(cmd, log):
    with (r / log).open('w') as f: p = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    assert p.returncode == 0 and 'Traceback' not in (r / log).read_text(), log
    print('PASS', log, flush=True)
run([sys.executable, str(r / 'scripts/run_renders.py'), 'master', 'iron'], 'logs/final_extra_renders.txt')
for key, pose, extra in [('45', '45', ['--samples', '256']),
                         ('0_no_denoise', '0', ['--samples', '512', '--no-denoise']),
                         ('0_realtime', '0', ['--realtime', '--samples', '192'])]:
    out = r / f'proof/renders/iron_harsh_{key}.png'
    if out.exists():
        print('EXISTING', out.name, flush=True)
        continue
    run([blender, '--background', '--factory-startup', str(r / 'scenes/iron_medallion_master.blend'),
         '--python', str(r / 'scripts/render_proof.py'), '--', '--variant', str(r / 'mobile/iron_badge_mobile.usdz'),
         '--rig', 'harsh', '--pose', pose, '--out', str(out)] + extra, f'logs/render_iron_harsh_{key}.log')
    assert out.is_file()
run([sys.executable, str(r / 'scripts/analyze_proofs.py')], 'proof/proof_analysis.txt')
for key in ['no_denoise', 'realtime']:
    run([sys.executable, str(r / 'scripts/measure_smoothness.py'), '--emblem', str(r / 'proof/emblem_iron.json'),
         '--pose', '0', '--out', str(r / f'proof/smoothness_{key}.json'),
         f'iron_{key}={r}/proof/renders/iron_harsh_0_{key}.png'], f'proof/smoothness_{key}.txt')
lines = ['# Smoothness measurements', '',
         'Original render pixels, eroded facet masks. Display luma levels. These measurements quantify intentional forged surface detail. The former uniform-surface thresholds are retained as historical diagnostics and are superseded by the latest reference-texture request.', '',
         '| Render | Facet residual mean | Edge excess mean |', '|---|---:|---:|']
for p in sorted((r / 'proof').glob('smoothness_*.json')):
    data = json.loads(p.read_text())
    if 'table' not in data: continue
    for key, row in data['table'].items():
        edge = row.get('edges', {}).get('excess_mean')
        edge_string = f'{edge:.6f}' if edge is not None else 'N/A'
        lines.append(f"| {key}, pose {data.get('pose', 0):g} | {row['facet_rough_mean']:.6f} | {edge_string} |")
lines += ['', 'Historical smooth-finish limits: stage 0.92 / 61.5; app point lights 1.00 / 64.6. Forged texture intentionally exceeds the facet-residual limits. '
          'Raw undenoised Cycles retains Monte Carlo sampling noise; Eevee is a separate realtime diagnostic. '
          'Per-plane brightness and adjacency use the separate emitted plane-ID mask in blender_metrics.json; no mask is inferred from the beauty image.']
(r / 'proof/NUMBERS.md').write_text('\n'.join(lines) + '\n')
print('Finished proof renders, smoothness crops, sheets and render comparisons.', flush=True)
