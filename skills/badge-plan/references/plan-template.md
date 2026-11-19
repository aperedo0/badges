# Badge plan template

Save as `PLAN.md` in the badge's working folder. Write in plain words. Omit a section only when it truly does not apply, and say so in one line.

## 1. What the owner will see

* At rest on Home, while it turns, on the Badges screen, in the floor reflection: a few plain sentences.
* The build order in one sentence.
* Open decisions as yes or no questions, each with a recommendation. An approved plan has none left open.
* Status line: `DRAFT`, `APPROVED (review round N)` or `TURNED DOWN`.

## 2. Reference read

* Mockup path. The piece inventory below is written from the image itself, never from a written description; sample pixels where a material is unclear and note the numbers.
* Size in app units: total height 5.45 from Y 2.995 down to Y minus 2.455 for floating badges (lower top only when the width reaches the 6.7 limit), width, and the badge box measured in the mockup. Coins use AGENTS.md section 2's shell and placement instead; badge-build builds floating shapes only.
* Pieces, back to front: each a solid with its thickness, bevel width and angle, gold rim if any, and the pieces it sits on. Steps between pieces about 0.03 to 0.08 units; bevels at least about 0.04 units wide.
* **Looks right when**, one line per piece: what that piece must look like in the app for it to be right, said as something a picture can prove false, and from which view (front, side, back, phone size). Examples: "the rim reads round from the side, never flat sided"; "the bolt's lower tip ends in a fine point, not a blunt end"; "each leaf is a separate raised piece, not paint on the plate". General checks (closed mesh, outline overlap) pass a wrong shape; these lines catch it.
* Crossings: every place two pieces overlap, and which is on top as the mockup shows it (the piece whose edges run unbroken through the crossing). The stack order follows this list.
* Colored faces: flat, as real enamel (a tilt of about 0.04 mirrors a bright part of the studio and washes the color pale); the mockup's facets are paint areas.
* Symmetry: which parts mirror exactly, which do not.
* Materials per part as the mockup shows them, and which of the mockup's light and dark is painted lighting that must not be copied into textures.
* The owner's intended differences from the mockup.

## 3. Prior art

The approved badge or badges whose method this plan reuses, with paths to their build scripts, and what changes for this badge. If nothing fits, say so and why the new method is safe.

## 4. Construction, part by part

For each part:
* **Outline source**: measured primitives (circles, straight lines, polygons with listed coordinates), a traced outline cleaned into curves (straight runs straight, tips sharp, widths even), or drawn by hand where tracing fails. Name where the coordinates live (`design.json` or similar).
* **Geometry in Blender**: curve, extrude, bevel or ring profile with numbers; how triangle edges follow the outline; flat facets where the design is faceted, smooth where it is rounded.
* **Relief**: heights in units, wall and bevel profile, how it meets neighboring parts with no gap, overlap or coplanar faces.
* **Back and side wall**: what the back shows and how it is made; side wall thickness, profile and material. With badge-build the back is the mirrored front (validate.py fails anything else); a different back needs its own build step.

## 5. Materials

For each material: name (never the coin names), base color and how it is chosen, metallic, roughness, texture size and UV set, glow. Gems: which shader path and the conditions it needs. The app's color limits (see the catalog) and the expected look for any color it cannot show.

## 6. The app walkthrough

Rest front, early turn, left side, back at half size, right side, the Badges screen still at about 40 points, the floor reflection. For each: what is visible, what could go wrong there, and how the plan handles it.

## 7. Risks

* **Features**: the badge's features that open catalog sections (traced from the picture, metal walls with enamel, bright saturated colors, layered parts, symmetry, gems, glass, fine marks, coin shell), and one line naming the sections that do not apply.
* **Every badge**: each layer 1 item with its prevention and check.
* **Feature sections**: each item of every section that applies, with its prevention and check.
* **This badge's own risks**: at least five, found with the catalog's layer 3 method (pre mortem, part by pose, material by light, joins, what is new), each with a prevention and a check.

## 8. Build steps and checkpoints

Ordered steps in the open Blender (one saved file per badge). Each step: what is built, the files and scripts, and the check that proves it, naming the broken result the check would catch. Mark the checkpoints where you stop and look. State the stop rule: a checkpoint failing because of the method returns to this plan and its review.

## 9. Budget

Triangles (about 35,000 to 45,000), file size (under about 5 MB), texture sizes (512 or 1024), the expected number of app builds, and any reason to exceed a guideline.

## 10. Final acceptance

Finish gate at real pixels and 4x, every pose at 4x, fresh review shippable and at least 90, contract validation, the model left visible in the simulator and the Blender file saved.

## Review log

Appended by badge-plan-review.
