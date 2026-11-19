# Claude's attempt: full chest wood and iron (2026-11-17)

Separate from Codex's work. Nothing in `phase06/` or the open Blender scene was changed.

- `source_copy.blend`: copy of the chest exactly as it was open in Blender (Codex's state).
- `chest_claude.blend`: same chest with my wood and iron on every wood surface and every
  structural iron piece. Codex's original meshes stay inside as `Codex backup ...` datablocks.
  Same camera and lights as Codex's review scene.
- `compare/`: reference, Codex and mine (closeup and full), plus my front, back, top and closeup.

Rebuild, in this order (each step works on `chest_claude.blend`):
1. `./run.sh vNN`: bottom planks and bottom rim maps, fresh `chest_claude.blend` from `source_copy.blend`.
2. `python tools/make_wood_panels.py maps` (Blender's Python), then
   `blender -b chest_claude.blend --python tools/build_wood.py -- maps`: all other planks.
3. `blender -b chest_claude.blend --python tools/build_iron.py`: all other iron.

Method:
- Wood: carved planks (grain flowing around knots, grooves, cracks, rounded plank edges with dark
  gaps) generated as height, color and roughness maps, shown as real displacement on a dense panel
  per surface: front, back, both ends, lid arch, both lid caps. Faces inside the chest use the
  same wood, box projected, bump only (not checked in a render yet).
- Iron: the bottom rim is a rebuilt mesh with real chipped chamfers and authored maps. Every other
  iron piece keeps its shape; its existing bevel strips are marked as worn bare metal (face
  attribute `claude_wear`) and a procedural dark hammered surface matches the rim. Pieces with no
  modelled bevel (the boots) get worn rounded edges from the Cycles bevel node, so that part does
  not show in the Material Preview viewport.
- Not touched: lock, hasp, hasp mount, ring handles and their mounts, rear hinges, rivets.
- This Mac has 8 GB of memory: panel meshes are kept light on purpose (fine detail lives in the
  maps). A denser iron remesh with chips on every piece was tried and dropped (5 million points).

## Simple style (started 2026-11-17, owner's new reference `simple/reference_simple.png`)

Step by step, each step shown to the owner before the next. `./run_simple.sh` rebuilds
`chest_simple.blend` from `chest_claude.blend` (maps from `tools/make_simple_plank.py` and
`tools/make_simple_iron.py`, look settings at the top of each; scene by `tools/build_simple.py`).
Renders for this style use neutral white light (`neutral=1` in `tools/render.py`); the saved file
keeps the warm lights.

- Step 1 (shown): bottom front plank and bottom iron band.
- Step 2 (shown, waiting for the owner's verdict): whole front face. Three lapped planks
  (seams at z = -1.177 and -0.640), bottom rim with authored maps, and a matching procedural
  smoky iron on the front posts, front boots, upper body band, lock strap and lower cuff.
  Rivets and diamonds on that iron are plain steel (object level material, shared meshes untouched).
  Lock, hasp, handles, the lid and the other sides are still the earlier version.
- Step 3 (shown, waiting for the owner's verdict): finer texture. Real wood fibre detail (Poly Haven
  Wood Cabinet Worn Long) is blended into the plank maps and a real fine metal surface (ambientCG
  Metal055A) into all simple iron, both as grayscale detail only, from the caches Codex already
  downloaded. Strength settings: `SCAN`, `SCAN_BUMP` in `tools/make_simple_plank.py` and
  `SCAN_ROUGH`, `SCAN_TONE`, `SCAN_BUMP` in `tools/build_simple.py`. Sources: `simple/SOURCES.json`.
- Step 4 (shown, waiting for the owner's verdict): the whole chest. Simple planks on the back, both
  ends, the lid (9 planks, mirrored over the top) and both lid caps (`tools/make_simple_panels.py`,
  same panel meshes as before, new maps). Procedural smoky iron on every iron piece, the handle
  mounts and the rear hinges; plain steel on every rivet, diamond and crown fastener; aged bronze
  on the lock, hasp and hasp mount; brass on the two side rings. Metals for arbitrary shapes come
  from `piece_metal()` in `tools/build_simple.py` (base colours `IRON_BASE`, `BRONZE_BASE`,
  `RING_BASE` at the top). Hardware materials are set on the object, so shared meshes are untouched.
  Renders: `simple/step4_*.png`.
- Step 5 (shown, waiting for the owner's verdict): grey iron a touch smoother (`IRON_SCAN = 0.70`,
  lower cloud bump) and a different brass texture: smooth satin with faint short curvy engraved
  marks and almost no scan grain (the `bronze = piece_metal(...)` line in `tools/build_simple.py`).
- Step 6: bronze a touch darker (BRONZE_BASE).
