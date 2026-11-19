from pathlib import Path
import json
D=Path(__file__).resolve().parent;R=D.parents[1];C=D/'09_pitted_iron';live=json.loads((C/'live_validation.json').read_text());assert live['only_target_data_swapped'] and not live['dirty']
(R/'PROJECT_STATE.md').write_text('''# Bottom iron test

Current live checkpoint: phase05/lower_iron/09_pitted_iron/master.blend, scene Test plank master. Only Lab Chest Lower Rim beneath the approved wooden plank changed. Owner iron review pending. The original reference editor, main viewport framing, camera, source lights and environment are preserved. Existing secondary review window shows the final iron closeup.

BC_final_polish remains the provisionally approved permanent wood benchmark. Its geometry, UVs, material graphs and packed maps are exact. Other wood, corner feet, uprights, cuffs, rivets, brass, original complete chest and rig remain unchanged. The owner's bottom only scope superseded the broad wood rollout directive for this round. Do not expand automatically.

Git 2ae680c stores the complete current live baseline, with fresh restoration verified in checkpoint_validation.json. phase05/lower_iron/baseline.blend and live_before_iron.blend are recoverable snapshots. The earlier wood checkpoints remain. Root treasure_chest.blend is older.

The selected iron has sparse real dents and edge chips on the existing adaptively tessellated rim, 98672 vertices and 98736 faces. Matching shared edge subdivisions retain a closed surface. Original anchors, outside dimensions and rivet seating regions are protected. Separate secondary hammering and pitting use coordinated independently editable albedo, roughness, metallic and 16 bit bump height. Fine surface data reuses official CC0 ambientCG Metal055A and Metal003. No gold edge paint or emission. Float authoring fields and rest/deformation arrays remain locally and in the selected production data.

Read phase05/lower_iron/REPORT.md and README.md. reference_comparison.jpg, baseline_comparison.jpg, close_views.jpg and chest_comparison.jpg contain the owner review. Surrounding materials are temporary render context only. Final PNGs remain beside the master. validation.json verifies all other scene objects, approved wood maps, materials, transforms, lights, bounds, contacts, closed mesh and packed target images. live_validation.json verifies the loaded result.

Rejected: modern brushed source, overly granular first texture, closed polygon stamps, crumpled erosion bands, overly quiet surface, and cloudy native hammered material. A low warm reflection light flattened and brightened the entire band; it was diagnostic only. Existing lighting remains unchanged. Detailed trial inputs remain on disk. Rejected scene caches are excluded from Git while the complete best master and required dependencies remain.

Remaining differences: sharper irregular forge scars and broken plate formations in the reference; selected dents remain rounder and exposed highlights cooler. This is an initial iron test for owner review. Further automatic strength tuning or reuse of rejected stamp patterns is not justified. Owner direction is required before more refinement or transfer. Brass and broader wood rollout remain future scoped tasks.

No new install, paid resource, image generation, app or simulator work, subagent or AI reviewer. Reuse scripts and cached official resources. Do not rerun the initial guarded live promotion on this now changed rim.
''')
(R/'README.md').write_text('''# Treasure chest material development

Current editable Blender scene: phase05/lower_iron/09_pitted_iron/master.blend, Test plank master. The bottom iron rim is the only new component developed. The approved BC wooden plank, original reference and owner framing are preserved. The owner reviews the initial iron before more work or transfer.

PROJECT_STATE.md is the compact continuation record. phase05/lower_iron/REPORT.md contains comparisons, technical changes and remaining gaps. Git checkpoint 2ae680c preserves the complete starting scene and required packed resources. Context materials appear only in isolated review renders. Root treasure_chest.blend is older.
''')
(R/'NEXT_WORK.md').write_text('''# Owner iron review pending

Review phase05/lower_iron/reference_comparison.jpg, close_views.jpg and chest_comparison.jpg. The selected 09_pitted_iron/master.blend is saved and loaded in Blender. The approved wood is unchanged. Only the existing bottom rim was developed.

Wait for owner direction before further refinement or transferring the iron to other parts. Main remaining gaps are sharper forge scars and warmer edge reflections. Do not automatically alter corner feet, brass, other iron or remaining wood. Preserve BC as the wood benchmark and reuse PROJECT_STATE.md, the cached resources and selected master.
''')
p=R/'AGENTS.md';s=p.read_text();s=s.replace('Work only on the existing lower front test plank until owner approval. Additional wood, iron and brass can appear only as temporary context in an isolated scene.','The owner provisionally approved BC_final_polish as the wood benchmark. Current authorized scope is one representative bottom iron rim below that wood. Preserve the wood and all other parts. Additional surrounding wood, iron and brass can appear only as temporary context in an isolated scene. Do not transfer the new iron before owner approval.')
s=s.replace('The current owner directive explicitly authorizes multiple internal refinement and visual validation passes on the test plank before presenting the strongest result.','The current owner directive authorizes internal refinement and visual validation of the bottom iron test while preserving the approved wood.');p.write_text(s)
state=dict(selected='09_pitted_iron',live_file=live['file'],scope='Only existing bottom iron rim beneath the approved plank',owner_review_pending=True,wood_benchmark='BC_final_polish, provisionally approved',baseline_git='2ae680c',work_active=False,background_jobs_running=False,next='Owner review before further iron refinement or transfer');(D/'STATE.json').write_text(json.dumps(state,indent=2)+'\n');print('Updated compact current state')
