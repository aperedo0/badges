from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;key=sys.argv[1];C=D/key;P=D.parents[1];v=json.loads((C/'validation.json').read_text());assert v['wood_geometry_uv_material_maps_exact'];assert (C/'live_validation.json').exists()
(P/'PROJECT_STATE.md').write_text(f'''# Bottom forged iron review

Current saved and live editable checkpoint: phase05/iron_fidelity/{key}/master.blend. Scene Test plank master preserves the owner's original reference editor, framing, camera, source lights, world and approved wood. The lower rim and its two small front knobs use the new iron. All other components are preserved. Bottom iron reflection review is a separate scene holding the selected studio reflection environment. Existing secondary image window shows the selected rendered iron closeup. Owner review pending.

BC_final_polish remains the approved permanent wood benchmark. Validation proves identical wood geometry, UVs, material graphs and packed maps, and exact preservation of every other original scene object and material. The owner explicitly authorized the same finish on the two small knobs above the textured bottom strip; their geometry is unchanged. The original complete chest and rigs are preserved. Feet, cuffs, uprights and all other hardware retain their previous materials. Do not transfer the iron or expand the wood rollout before owner approval.

Git checkpoint 546d617 contains the complete starting art and required dependencies. phase05/iron_fidelity/baseline.blend is the packed starting snapshot; checkpoint_validation.json proves fresh restore. The previous iron 09_pitted_iron remains recoverable. Root treasure_chest.blend is older. This round's final refinement is saved but uncommitted; prepare_commit.sh stages only this round and its state files when the owner runs it.

Current iron: independently mixed exposed conductor, blackened conductor and opaque dielectric forge scale. Published clean iron sRGB C4C6C6 is correctly converted to linear for exposed metal and diagnostic controls. Intermittent geometry informed edge wear remains neutral in color. No golden paint or emission. Existing hammer depressions receive localized planar floor fitting and actual medium vertex displacement on {v['vertices']} vertices. Complementary fine pitting, shallow scale and limited open forge laps use separately adjustable bump. Coarse bump is disabled to avoid duplicating physical relief. Original primary damage, outer dimensions and rivet contacts are protected. All required textures and the review HDRI are packed.

Read phase05/iron_fidelity/REPORT.md and README.md. reference_comparison.jpg, baseline_comparison.jpg, close_views.jpg and chest_comparison.jpg contain the review. Baseline and candidate are shown both under original lighting and matching studio reflections. Context PNGs use temporary surrounding finishes only. validation.json verifies original scenes and mesh integrity; live_validation.json verifies the loaded save.

Diagnostic findings: original material and reflection setup concealed useful relief; the broad source fill mainly caused the continuous white top reflection. Clean iron controls revealed structure. Reduced warm lights plus studio reflections improve visibility in an isolated scene. Existing source lighting remains available unchanged. Rejected: cloudy professional height replacement, low density displacement, unrestricted patchy coating, final lower coverage trial and indiscriminate warm wash. A lower HDRI level hid useful detail. Do not repeat these trials or global strength sweeps.

Remaining reference gap: more angular broken plate formations, sharper selective scars, bolder damaged bevels and brighter warm edge accents in the reference. Some selected forms remain rounder, with scratch like fine detail. Full parity is not claimed. Further meaningful form work should be deliberate local sculpting guided by owner review, not more global noise.

Resources are free and cached with licenses in resources/SOURCES.json. No install, paid resource, app work, simulator work, subagent or AI reviewer. Do not rerun the guarded initial promotion on the already changed live rim. The owner alone approves the next step.
''')
(P/'README.md').write_text(f'''# Treasure chest material development

Current saved Blender checkpoint: phase05/iron_fidelity/{key}/master.blend. The bottom iron reinforcement and its two small front knobs use the new finish. Approved wood, the reference setup and original lighting are preserved. Bottom iron reflection review saves the separate alternative lighting. Owner approval is pending before any transfer.

PROJECT_STATE.md is the concise continuation record. phase05/iron_fidelity/REPORT.md contains evidence, comparisons, changes and remaining gaps. Git 546d617 preserves the complete starting scene. The selected master packs required art resources. Root treasure_chest.blend is older.
''')
(P/'NEXT_WORK.md').write_text(f'''# Owner iron review pending

Review phase05/iron_fidelity/reference_comparison.jpg, baseline_comparison.jpg, close_views.jpg and chest_comparison.jpg. The saved and live checkpoint is phase05/iron_fidelity/{key}/master.blend. The original Test plank master scene preserves its lighting; Bottom iron reflection review provides the isolated reflection environment. The existing lower rim and its two small front knobs use the new finish.

Wait for owner direction before more development or transfer. Remaining gaps are angular forged plate formations, sharper broken scars, damaged bevel definition and brighter warm reflections. Do not automatically change other iron, brass or wood. Preserve BC as the wood benchmark and reuse current project records, authoring fields, cached resources and scripts.
''')
state=dict(status='Saved candidate awaiting owner artistic review',selected=key,master=str(C/'master.blend'),original_git_checkpoint='546d617',scope='Lower rim and two small front knobs only',approved_wood_preserved=True,reviewer='Owner only',validation='validation.json',live='live_validation.json',remaining='More angular broken formations, selective scars, damaged bevel definition and warm edge accents')
(D/'STATE.json').write_text(json.dumps(state,indent=2));print('Updated concise project records')
