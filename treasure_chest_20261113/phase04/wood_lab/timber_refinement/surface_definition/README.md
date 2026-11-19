Previous round preserved at Git 97cce9c. Current final polish is BC_final_polish; read the root PROJECT_STATE.md and final_polish/REPORT.md.

# Surface organization round

Current selected checkpoint: ../AW_depth_hierarchy/master.blend, loaded in Test plank master with the owner reference and comparison camera retained. See ../../../../PROJECT_STATE.md for the compact current state and REPORT.md for detailed evidence. The owner reviews; no AI reviewer or transfer to other planks.

baseline.blend preserves the starting AE state. live_before_selection.blend preserves the immediate initial live state; live_before_AW.blend preserves the complete preceding AT state. Source fingerprints are in checkpoint.json. Source AE remains unchanged.

All processing reuses the previous infrastructure and cached official CC0 data. The selected folder contains packed material maps, complete editable master, numerical full height, geometry height, masks and validation. Intermediate geometry and normal frames remain cached locally. New candidate keys identify changed artwork. Rendering uses a single GPU lock with an in lock cache check for run_jobs.py to prevent duplicate work. Do not launch a second copy of a running queue.

The original baseline guarded show_selected_live.py must not be rerun on the current mesh. Later work should begin with a new checkpoint and recorded input geometry. Appended local data can leave an unused Blender library stub; the helper removes only that verified unused stub before saving. Do not alter real linked source data.

Compare at equal whole chest scale before diagnosing feature hierarchy. Earlier manually rectified close crops are approximate and cannot establish physical feature dimensions. Owner comparisons use projected chest width normalization without stretching either image.
