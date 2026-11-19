# Final polish continuation

Baseline is the complete AW checkpoint committed as 97cce9c. The selected complete checkpoint is BC_final_polish, saved and loaded in Blender after final resolved visual inspection. Owner approval is pending. Read the root PROJECT_STATE.md for current status. Only the owner approves; do not transfer to other planks.

setup.py prepares the isolated pigment variant and verifies source cache paths. prepare_finish.py tests localized roughness. prepare_edges.py makes a bounded correction to resolved existing grain transitions. prepare_right.py tests only existing right bay width hierarchy. assemble.py combines the visually retained passes. The existing geometry builder, complementary normal solver and packer remain authoritative. solve_normals.py uses required_AE_normal.png copied from Git because the older loose map was absent after separate cleanup.

structure_batch.py builds a new immutable candidate and renders both bays. For final renders use surface_definition/run_jobs.py with WOOD_FINAL=1; it takes the existing GPU mutex. Never launch duplicate queues. present.py creates comparisons against the current AW baseline, not the older AE round.

promote_live.py is guarded by the recorded AW geometry fingerprint and must not be rerun on a changed live mesh. It is intended once after final visual inspection and makes live_before_polish.blend first. Existing Blender screens, owner camera, rig, reference and other materials are preserved. No external or paid resource is required.

Complete packed masters, independent maps and full float32 numerical height fields are preserved in each candidate folder. Rebuildable geometry, frame arrays and diagnostic fields remain local. REPORT.md records retained and rejected changes and remaining differences.
