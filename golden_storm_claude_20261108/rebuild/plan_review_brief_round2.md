Review the build plan for the Ornate Golden Storm (stacked pieces rebuild) badge before any modeling starts.

Open these first:
1. The plan: /Users/antonioperedo/Desktop/badges/golden_storm_claude_20261108/rebuild/PLAN.md
2. The owner's mockup (open the image and look closely, including zoomed areas): /Users/antonioperedo/Desktop/badges/golden_storm_claude_20261108/reference/mockup.png
3. The app contract and the owner's taste: /Users/antonioperedo/Desktop/badges/AGENTS.md (sections 1 to 4)
4. The failure catalog: /Users/antonioperedo/Desktop/badges/skills/badge-plan/references/failure-catalog.md
5. The quality rules: /Users/antonioperedo/Desktop/badges/skills/badge-quality/SKILL.md
6. The plan's prior art: every build script and folder the plan names. Open them; do not trust the plan's description of them.

This is review round 2. The plan's Review log lists round 1's findings and how each was fixed; the fixes are prime suspects, so check each against the scripts and pictures it names, then reread the whole plan. Plan check pictures: /Users/antonioperedo/Desktop/badges/golden_storm_claude_20261108/rebuild/review/ (top_*.png, clean_strokes_over_mockup.png) and planchk/material_map.png.

Your job: decide whether this plan will produce a badge that looks like the mockup on the owner's iPhone, at rest and through a full turn, and find everything that would go wrong. Be adversarial: try to refute each claim, re-derive every number, and assume anything not written down will be guessed wrong by the builder. "Approved" is a valid and expected verdict when the plan is solid. The owner does not need an exact copy: a real 3D object will differ in highlights, reflections, depth and colors the app cannot show, and that is fine. Turn a plan down for what would look wrong or broken, never for natural 3D differences.

Check, in this order:
1. **Looks like the mockup**: does every part, line and color of the mockup have a construction step? Inventory the image yourself and compare. Are proportions, depths and layers measured, not guessed?
2. **Built like the real object**: is the badge planned as stacked pieces with real thickness and bevels at least about 0.04 units wide, the way the mockup is layered? A flat plate with painted areas and small bumps for lines is a BLOCKER: it reads as fuzz at phone size. Do not push heights down to avoid other risks; solve those with bevels and the side wall technique.
3. **Clean in the app**: walk each build step in the app's environment (fixed studio light, AgX color finish, glow over 1.5 linear, floor reflection, about 416 pixels tall at rest, about 40 points on the Badges screen). Where would fuzz, wobbly lines, speckle, white dots, halos, dark fringes, washed out color or z fighting appear?
4. **Every angle**: early turn, both sides, back at half size. Gaps, banding, flashing edges, unfinished back, mottled side walls, gems losing color.
5. **Failure catalog**: are the badge's features listed correctly, so the right sections open? Is every layer 1 item and every item of an opened section handled? Are the plan's own risks specific to this badge?
6. **Your own risks**: look at the mockup and the plan with fresh eyes and find what neither the plan nor the catalog names. Use the catalog's layer 3 method: pre mortem, each part at each pose, each material facing the light and at a grazing angle, each join, what is new compared with approved badges.
7. **Method**: is there a proven method in an approved badge that is simpler or safer than the plan's? Name it, with its path.
8. **Facts**: every file, script, setting and number the plan cites exists and says what the plan claims.
9. **Checks that can fail**: for every check the plan names, the broken build it would catch. A check a broken build also passes is a BLOCKER.
10. **Handoff**: could a builder with only this plan, the mockup and AGENTS.md build it without asking a question?

Reply in exactly this format, one short line per finding:

VERDICT: APPROVED or TURNED DOWN

BLOCKERS: problems that would make the badge look wrong or broken in the app, or force the builder to guess. Each: what, the evidence (file and line, or what the mockup shows), and the exact edit to the plan.

RISKS: things likely to need care during the build, each with the checkpoint that should own it.

NITS: small wording or clarity fixes.

NEW RISKS: risks neither the plan nor the catalog names, each with a prevention and a check, or "none found".

STRONGEST CONCERN: the one thing most likely to make the owner unhappy with the result, even if the plan is approved.
