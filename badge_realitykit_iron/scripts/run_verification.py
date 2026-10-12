from pathlib import Path
import subprocess,sys,json
r=Path(__file__).resolve().parents[1];handoff=next(folder for folder in [r,*r.parents] if (folder/'forged_revision/08').is_dir());blender='/Applications/Blender.app/Contents/MacOS/Blender'
def run(name,script,*args):
    path=r/'proof'/name
    cmd=[blender,'--background','--factory-startup','--python',str(r/'scripts'/script)]
    if args:cmd+=['--']+list(map(str,args))
    with path.open('w') as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
    assert result.returncode==0 and 'Traceback' not in path.read_text(),name
    print('PASS',name,flush=True)
run('geometry_identity.txt','validate_geometry.py')
run('scene_and_normals_validation.txt','check_scenes.py')
run('crystal_design_validation.txt','verify_crystal.py')
run('usd_diff_silver_vs_iron.txt','compare_usd.py',r/'source/silver_v3/silver_badge_mobile.usdz',r/'mobile/iron_badge_mobile.usdz',r/'proof/usd_diff_silver_vs_iron.json')
run('usd_diff_previous_vs_iron.txt','compare_usd.py',r/'previous/v3/mobile/iron_badge_mobile.usdz',r/'mobile/iron_badge_mobile.usdz',r/'proof/usd_diff_previous_vs_iron.json')
for filename in ['usd_diff_silver_vs_iron.json','usd_diff_previous_vs_iron.json']:
    data=json.loads((r/'proof'/filename).read_text())
    assert all(x['prim'].startswith(('/Badge/Emblem','/Badge/_materials')) for x in data['differences'])
run('usd_diff_final08_vs_iron.txt','compare_usd.py',r/'previous/final08/mobile/iron_badge_mobile.usdz',r/'mobile/iron_badge_mobile.usdz',r/'proof/usd_diff_final08_vs_iron.json')
assert all(x['prim'].startswith(('/Badge/Emblem','/Badge/_materials')) for x in json.loads((r/'proof/usd_diff_final08_vs_iron.json').read_text())['differences'])

run('usd_diff_forged05_vs_iron.txt','compare_usd.py',handoff/'forged_revision/05/mobile/iron_badge_mobile.usdz',r/'mobile/iron_badge_mobile.usdz',r/'proof/usd_diff_forged05_vs_iron.json')
assert all(x['prim'].startswith(('/Badge/Emblem','/Badge/_materials')) for x in json.loads((r/'proof/usd_diff_forged05_vs_iron.json').read_text())['differences'])
run('reimport_check.txt','reimport_check.py',r/'mobile/iron_badge_mobile.usdz')
run('floor_cut_verification.txt','verify_floor_cut.py',r/'work/iron_uncut.usdz',r/'mobile/iron_badge_mobile.usdz','-2.895',r/'proof/floor_cut_verification.json')
for row in json.loads((r/'proof/floor_cut_verification.json').read_text())['meshes'].values():
    assert row['min_y_cut']>=-2.895-1e-7
    assert row.get('kept_missing',0)==row.get('kept_changed',0)==row.get('new_triangle_material_mismatches',0)==0
run('floor_cut_topology.txt','check_casing_topology.py',r/'source/silver_v3/silver_badge_mobile.usdz',r/'mobile/iron_badge_mobile.usdz')
run('proof_geometry.txt','extract_proof_geometry.py')
with (r/'proof/usdchecker.log').open('w') as log:result=subprocess.run(['/usr/bin/usdchecker','--arkit',str(r/'mobile/iron_badge_mobile.usdz')],stdout=log,stderr=subprocess.STDOUT)
assert result.returncode==0 and 'Success!' in (r/'proof/usdchecker.log').read_text()
print('PASS usdchecker --arkit',flush=True)
