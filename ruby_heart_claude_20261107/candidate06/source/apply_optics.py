"""Copy fitted foil optics into the preview app's shader and Swift exposure."""
import sys, json, re
B = '/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/'
prm = json.load(open(sys.argv[1]))['prm']
def f(x): return f'{float(x):.6f}'
m = open(B + 'BadgeCrestGemSurface.metal').read()
glow = [prm['glow'] * c for c in prm['glow_color']]
rep = {
    'cHeartAbsorption': f"float3({', '.join(f(a) for a in prm['absorption'])})",
    'cHeartFoil': f(prm['foil']),
    'cHeartBodyLevel': f(prm['body_level']),
    'cHeartBodyClamp': f(prm['body_clamp']),
    'cHeartSpecClamp': f(prm['spec_clamp']),
    'cHeartSpecGain': f(prm.get('spec_gain', 1.0)),
    'cHeartSpecFloor': f(prm.get('spec_floor', 0.0)),
    'cHeartPathBase': f(prm.get('path_base', 0.0)),
    'cHeartTentGain': f(prm['tent_gain']),
    'cHeartGlow': f"float3({', '.join(f(g) for g in glow)})",
}
for k, v in rep.items():
    m, n = re.subn(rf'(constant float3? {k} = )[^;]+;', rf'\g<1>{v};', m)
    assert n == 1, k
open(B + 'BadgeCrestGemSurface.metal', 'w').write(m)
s = open(B + 'Badge3DLiveBadge.swift').read()
s, n = re.subn(r'(nonisolated static let heartFoilExposure: Float = )[^\n]+', rf'\g<1>{f(prm["exposure"])}', s)
assert n == 1
open(B + 'Badge3DLiveBadge.swift', 'w').write(s)
print('applied', rep, 'exposure', prm['exposure'])
