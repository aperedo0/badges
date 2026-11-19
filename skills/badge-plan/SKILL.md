---
name: badge-plan
description: Write the build plan for a 3D badge before any modeling. It covers how every part of the owner's mockup will be built in Blender, how it will look in the iPhone app at rest and through a full turn, everything that can go wrong and the check that catches it. Use when the owner gives a new badge mockup, asks to plan, rebuild or redo a badge, or a badge build keeps failing and needs a new approach. The plan then goes to badge-plan-review; no building starts until it is approved.
---

# Badge plan

A great plan makes the build easy. Badges failed when building started from a guess and the method was tuned round after round (November 8, 2026: three enamel badges traced from pixels reached the owner with fuzz and wobbly lines). Plan first, get it approved, then build exactly the plan.

**Close, not exact** (owner rule, November 8, 2026): the badge does not have to match the mockup exactly. A real 3D object under the app's light will differ in highlights, reflections, depth and colors the app cannot show, and that is fine. Match the design: shapes, proportions, parts, line work and colors as close as the app allows. Never spend rounds chasing exact pixels or a painted look.

## Build it like the real object: stacked pieces

A badge is made of several pieces, and that is the right way to build it. Each visible element is its own solid with real thickness and beveled edges, and pieces sit on top of each other the way the mockup shows: a back plate, the rays on it, the sun on the rays, the mountains in front of the sun, the clouds and border in front of them, a gem in its frame on top. Pieces may overlap and stack; nothing needs cutting.

* Never build the badge as one flat plate with painted color areas and small bumps for lines. On November 8, 2026 the Mountain Sunburst's rays and wedges were built that way: its gold lines rose about 2 phone pixels, light smeared across them, and the owner saw fuzz at once and asked why a 3D badge was flat.
* Make every edge big enough to see: steps between pieces about 0.03 to 0.08 units, bevels at least about 0.04 units wide (3 screen pixels at rest) at about 45 degrees. Smaller relief does not read as an edge; it reads as blur.
* Each piece carries its own gold rim when the mockup outlines it, so lines come from real bevels, not from paint.
* Use the house side wall technique for the visible sides of each piece (AGENTS.md section 4).

## Read before planning

1. The workspace `AGENTS.md`: the app contract, the owner's taste and the techniques that worked or failed. It overrides this skill.
2. The mockup itself, at full size and zoomed in. Inventory its pieces yourself from the image, back to front. Never plan from a written description of it: one misread solid gold spikes and flat enamel and the build followed it. Where a part's material is unclear, sample its pixels across the part (a profile of colors) and decide from the numbers.
3. Prior art, per element: list the badge's hard or new elements (spirals and scrolls, thin gold line work, a bright yellow, clouds, gems, glass, edges over a base) and search the approved badges for each one, in one search agent across their folders (Codex's dated folders: READMEs, REPORTs, build scripts). Also find the approved badge closest overall. Reuse a proven method over inventing one; say which and why, with paths. (November 9, 2026: the Golden Storm plan rebuilt spirals and edges from scratch for many rounds before anyone looked at how approved badges did them.)
4. Any earlier attempts at this badge and the owner's comments on them.
5. [The failure catalog](references/failure-catalog.md): every way a badge has gone wrong in this app and how to prevent it.

## Write the plan

Use [the plan template](references/plan-template.md). Save it as `PLAN.md` in the badge's working folder. The essentials:

* **Every piece has a construction method**: where its outline comes from, how it becomes a solid in Blender, its thickness and bevels, which pieces it sits on, its back and its side wall. Edges follow the design's lines; never a grid over a picture; never one flat plate with painted areas.
* **Every piece says how you can tell it is right**: one "looks right when" line per piece, naming what a picture would show if it were wrong and the view that shows it (why, November 14, 2026: in a documented outside run a round shaft stayed square through 19 versions while every general check passed).
* **Every part has a material**: color source, metal, roughness, glow only where needed, and what the app's color finish will do to it.
* **Walk the app**: what the owner sees at rest, at the early turn, from both sides, from the back at half size, on the Badges screen at about 40 points, and in the floor reflection.
* **Risks in three layers** (see the catalog): every item of layer 1 (every badge); every item of the feature sections this badge opens, skipping the rest in one line; and at least five risks of this badge's own, found fresh.
* **Every check can fail**: name the broken build it would catch. A check that a broken build also passes is decoration.
* **Checkpoints in the open Blender**: the order of building, where to stop and look, and the rule that a checkpoint failing because of the method sends the build back to the plan, not into another round of tuning.
* **Open decisions**: choices only the owner can make (a color the app cannot show, a depth, a back design), each with a recommendation.

## Validate, then hand off

* Every mockup part maps to a build step and a check, and every piece has its "looks right when" line.
* **Plan check for stacked badges**: draft `PIECES.json` and run badge-build's `badge3d.py` and `validate.py` on it (engine output only, not a candidate). They find shared walls, stacking and budget problems while the plan can still change. Put the failures, or "validate: no failures", in the plan for the reviewer.
* Every layer 1 item and every item of an opened section has a prevention and a check; the badge's own risks are specific, not restated catalog items.
* Handoff test: another agent with only this plan, the mockup and `AGENTS.md` could build the badge without asking a question. If not, the plan is not done.

Then run badge-plan-review. Once approved, build with badge-build (its tools make stacked pieces, prove them and capture them in the app). Show the owner the plan's first section (what they will see, the build order in one sentence, the open decisions as yes or no questions with your recommendation) together with the review verdict. Never start modeling from a plan that is not approved.
