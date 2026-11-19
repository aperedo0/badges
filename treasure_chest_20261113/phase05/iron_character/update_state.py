from pathlib import Path
import json
D=Path(__file__).resolve().parent;P=D.parents[1];choice=json.loads((D/'selection.json').read_text());C=D/choice['candidate'];v=json.loads((C/'validation.json').read_text());live=json.loads((C/'live_validation.json').read_text());assert v['wood_geometry_uv_material_maps_exact'] and (live.get('material_applied') or live['review_image_shown'])
(P/'PROJECT_STATE.md').write_text(f'''# Targeted bottom iron review

Current saved and live checkpoint: phase05/iron_character/{choice['candidate']}/master.blend. Owner review pending. Only the existing lower rim and its two already treated small front knobs use the new iron. All other materials and geometry are preserved. Test plank master retains the original lighting, camera, exposure, framing and reference setup. Bottom iron reflection review contains the selected isolated warm environment. The secondary review window is currently closed; the current layout and original reference editor are preserved. Updated renders are saved locally.

BC_final_polish is the approved wood benchmark. Validation proves exact wood geometry, UVs, material graphs and packed maps; other original objects, materials, transforms, rig and complete chest are preserved. Original bounds, rivet contacts and closed rim integrity remain valid. The rim still has {v['vertices']} vertices. Original UVs and topology are retained. Broad surface vertices outside localized edge edits are exact. No iron rollout or brass development is approved.

Git fe8e703 restores the starting P_iron_knobs artwork. phase05/iron_character/baseline.blend is the complete packed live checkpoint for this round. Earlier Git 546d617 and the previous phase05/iron_fidelity scenes remain available. The new selected complete master packs all required maps and its HDRI. New work is saved but uncommitted. prepare_commit.sh stages only this round and updated project records when the owner runs it.

The existing three conductor and opaque scale branches remain. Independent weathering, pigmentation, roughness, shallow fractured scale markings and edge wear were added. Cached ambientCG Metal025 and Metal003 provide separate scalar channels without rust pigmentation. Interior reference shapes guide the shallow marking mask; reference RGB is not copied. The markings are an appearance driven scale interpretation, not proof that every line is a crack. Only some markings affect conductor coverage.

Existing broad hammering was not increased or regenerated. New marking bump distance is 0.00055 in current scene units. Legacy broad lap normal strength is 0.25 and its exposed lip mask is scaled to 0.20. Existing chip locations have localized extra deterioration and small upper bevel facets; a mesh attribute controls worn facet reflectance. Lower facets that made notches too prominent were reverted. No gold edge paint or emission.

The resumed round retains shallow recessed scale boundaries without changing their density or bump distance. Selected review lighting uses studio HDRI tint (1,0.88,0.72), strength 0.35, established warm key and elevated fill, and two narrow warm bevel reflection sources linked only to the authorized iron. These new sources exist only in the isolated review scene. Original source lighting is exact. The resumed owner sheet compares the previous saved look with new lighting and the scale correction; mark_direction_comparison.jpg separately isolates the marking change under identical light. Final Cycles views use 128 samples. Actual rendered closeups, neutral diagnostics and contextual views were opened for artistic evaluation. No AI reviewer.

Earlier Shader AOV checks verified seventeen actual signals and the legitimate constant metallic values one and zero. They revealed an unexpectedly flat pigment mask caused by clipping a 16 bit source through an 8 bit conversion. Native precision loading restores brown and charcoal variation. Fourteen other AOVs are unchanged. Diagnostic nodes and passes exist only in temporary copies, and are absent from production. Detailed before and after data is in aov/. A further six signal check in aov/edge_cut found no material or normal break at a sharp lower highlight termination. The long lower reflection emitter was tilted through the floor and chest height range. Making its long axis horizontal removes the bright wedge. The final render mode is edge_floor, and exact reflection source settings are stored in design.json.

Read phase05/iron_character/README.md and REPORT.md. resume_reference.jpg, resume_close_views.jpg and resume_context.jpg are the latest owner review. Earlier comparisons remain available. Context finishes are temporary only. validation.json proves preservation and live_validation.json verifies the saved open result. Source hashes and existing free licenses are recorded in SOURCES.json.

Rejected: negligible damaged facet exposure remap, broad strong reflection sources that wash out the face, incomplete reflection coverage across the bays, raised cratered marking relief, broad lower bevel cuts and overly prominent legacy exposed strokes. Prior failed cloudy professional height replacement, low density displacement, closed stamps and global noise systems remain rejected. Do not restart them or repeat undirected strength sweeps.

Remaining reference gap: sharper broken edge highlights, more irregular overlapping surface scale and some softer existing pits. Wait for owner direction before another material pass or transfer. Do not rerun initial guarded promotion on this now changed scene.
''')
(P/'README.md').write_text(f'''# Treasure chest material development

Current saved and live Blender checkpoint: phase05/iron_character/{choice['candidate']}/master.blend. Only the bottom reinforcement and its two already treated knobs use the refined iron. Approved wood and other components are preserved. Original Test plank master lighting is unchanged; Bottom iron reflection review saves alternative warm lighting. Owner approval is pending.

PROJECT_STATE.md is the continuation record. phase05/iron_character/REPORT.md contains the comparisons, evidence and limits. Git fe8e703 and the new packed baseline preserve the starting artwork. The selected master packs required resources. Root treasure_chest.blend is older.
''')
(P/'NEXT_WORK.md').write_text('''# Owner iron review pending

Review phase05/iron_character/resume_reference.jpg, resume_close_views.jpg and resume_context.jpg. The selected saved scene is recorded in PROJECT_STATE.md and selection.json. The final Cycles closeup is packed in Blender. The owner closed the extra review window; preserve the current layout and original reference editor. Only the lower reinforcement and its two already treated knobs are involved.

Remaining differences are stronger broken edge highlights, more irregular overlapping scale and some softer existing pits. Wait for owner direction before further refinement or transfer. Preserve the approved BC wood, other hardware and original scene lighting. Reuse cached data, existing material branches, rendering adapters and validation. Do not add more hammering or generic cracks.
''')
(D/'STATE.json').write_text(json.dumps(dict(status='Saved candidate awaiting owner review',selection=choice,scope=live['scope'],wood_preserved=True,validation=str(C/'validation.json'),live=str(C/'live_validation.json'),baseline_git='fe8e703'),indent=2));print('Updated concise continuation records')
