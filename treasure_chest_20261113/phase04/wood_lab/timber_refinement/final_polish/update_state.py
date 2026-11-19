from pathlib import Path
import json
D=Path(__file__).resolve().parent;W=D.parent;R=D.parents[3];C=W/'BC_final_polish';live=json.loads((C/'live_validation.json').read_text());assert live['material'].startswith('Wood Lab BC_final_polish') and not live['dirty']
text='''# Current test plank

Live Blender and strongest checkpoint: phase04/wood_lab/timber_refinement/BC_final_polish/master.blend, scene Test plank master. The original reference editor, owner comparison camera and main viewport framing remain. The separate render window displays the completed isolated context. Owner review pending. No other plank, permanent surrounding material, app or AI reviewer.

Git 97cce9c preserves the complete starting AW scene and required maps and numerical height data. final_polish/checkpoint.json verifies exact committed bytes. final_polish/live_before_polish.blend is the immediate live snapshot before replacement. AW_depth_hierarchy/master.blend remains unchanged. Earlier AE and other owner checkpoints remain recoverable. Root treasure_chest.blend is older.

Final cleanup retains three isolated passes: AZ applies a bounded correction only at resolved broad grain transitions, about 0.0014 scene units at most; BB reduces the prominence of existing narrow right bay channels so broader formations read more coherently; AX shifts intrinsic pigment slightly toward chestnut and burnt amber while retaining texel luminance. Existing fine source detail remains, with normals recomputed against actual mesh frames. No new features or polygons. Knot relief and the existing vertical split are unchanged. Roughness, IOR, normal strength one, exposure and lighting remain at AW values. Maps are packed 4096 by 1536. Full float32 height and geometry height are beside the master.

A specular removed diagnostic showed that pale pink highlights are partly reflected light. Removing specular is not retained. A localized roughness floor and warmer key test gave too little extra benefit and were rejected. Earlier failed synthetic or traced core, polar rings and independent column profile methods should not be repeated. Do not add detail to compensate for broad form organization.

Evidence is in final_polish/REPORT.md. reference_final.jpg compares the original and final chest at equal projected width with temporary surrounding shaders. reference_close.jpg shows the corresponding knot region at equal whole chest scale. baseline_final.jpg compares this round's AW baseline with BC under the same light. close_views.jpg, right_before_after.jpg, whole_plank.jpg and knot_close.jpg preserve detail. Full resolution PNGs remain beside the master. Temporary iron, brass, quiet surrounding wood and floor contact are confined to the isolated render, never transferred into live components.

saved_validation.json and live_validation.json verify original complete scene and rig, other components, unchanged target topology and UVs, exact contact boundary, closed mesh, packed local material maps and the single shared reference. channel_controls.json confirms exact core relief and roughness. Git contains the complete initial checkpoint. The unused append library stub is removed before saving local data.

Remaining differences: some large formations still have smoother and rounder ledges than the reference; the knot's inner contour differs. Further isolated sharpening or recoloring offers diminishing returns and risks the current foundation. Whole chest tonal decisions should be revisited with finished surrounding materials, after owner approval. Do not claim an exact match or a completed chest.

All source data and tools were reused. No new download, installation, paid resource or subagent. One older loose normal map absent after unrelated cleanup was copied from Git into final_polish/required_AE_normal.png; cleanup paths were left untouched. Rebuildable geometry, frame and diagnostic intermediates stay cached locally. Use final_polish/README.md and deterministic scripts for continuation. Do not rerun the AW guarded promotion on this later mesh.
'''
(R/'PROJECT_STATE.md').write_text(text)
(R/'README.md').write_text('''# Treasure chest test plank

Open phase04/wood_lab/timber_refinement/BC_final_polish/master.blend, scene Test plank master. It is saved and loaded in Blender with the existing reference and owner camera retained. The separate review window shows the final isolated chest context. The owner reviews before any transfer to remaining parts.

PROJECT_STATE.md is the compact continuation record. final_polish/REPORT.md under phase04/wood_lab/timber_refinement contains evidence and limitations. Git checkpoint 97cce9c preserves the starting AW scene and dependencies. Earlier original chest, rig and reference remain recoverable. Root treasure_chest.blend is older.

Surrounding context materials appear only in isolated render images. Live surrounding components retain their original materials. No app or simulator work and no AI reviewer.
''')
(R/'NEXT_WORK.md').write_text('''# Owner review pending

BC_final_polish/master.blend is the saved live checkpoint in Test plank master. Review final_polish/reference_final.jpg, baseline_final.jpg and close_views.jpg alongside PROJECT_STATE.md. The original reference, owner camera and main viewport framing remain. The separate render window shows the final isolated chest context.

Wait for owner direction or approval before more refinement or transfer. Do not alter another plank, hardware or the app automatically. Do not repeat rejected synthetic core methods, column profiles, indiscriminate sharpening, roughness or warm light tuning. Do not rerun a prior baseline guarded helper on the current mesh.
''')
s=dict(selected='BC_final_polish',live_file=live['file'],live_confirmed=True,owner_review_pending=True,work_active=False,background_jobs_running=False,baseline_git='97cce9c',previous_best='AW_depth_hierarchy',scope='Only existing test plank',next='Owner review before further work or transfer');(W/'STATE.json').write_text(json.dumps(s,indent=2)+'\n');(D/'STATE.json').write_text(json.dumps(s,indent=2)+'\n')
p=W/'surface_definition/STATE.json';old=json.loads(p.read_text());old.update(working=False,background_jobs_running=False,superseded_by='BC_final_polish',next='Previous round preserved at 97cce9c. Read root PROJECT_STATE.md for final polish.');p.write_text(json.dumps(old,indent=2)+'\n')
p=W/'surface_definition/README.md';old=p.read_text();prefix='Previous round preserved at Git 97cce9c. Current final polish is BC_final_polish; read the root PROJECT_STATE.md and final_polish/REPORT.md.\n\n';p.write_text(prefix+old)
p=D/'README.md';p.write_text(p.read_text().replace('The selected candidate is BC_final_polish, subject to final resolved review and live promotion.','The selected complete checkpoint is BC_final_polish, saved and loaded in Blender after final resolved visual inspection. Owner approval is pending.'))
print('Updated compact project state after verified live promotion')
