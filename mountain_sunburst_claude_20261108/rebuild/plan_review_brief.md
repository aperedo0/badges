Review the build plan for the Radiant Mountain Sunburst badge before any modeling starts.

Open these first:
1. The plan: /Users/antonioperedo/Desktop/badges/mountain_sunburst_claude_20261108/rebuild/PLAN.md
2. The owner's mockup (open the image and look closely, including zoomed areas): /Users/antonioperedo/Desktop/badges/mountain_sunburst_claude_20261108/reference/mockup.png
3. The mockup checklist: /Users/antonioperedo/Desktop/badges/mountain_sunburst_claude_20261108/review/checklist.md
4. The app contract and the owner's taste: /Users/antonioperedo/Desktop/badges/AGENTS.md (sections 1 to 4)
5. The failure catalog: /Users/antonioperedo/Desktop/badges/skills/badge-plan/references/failure-catalog.md
6. The quality rules: /Users/antonioperedo/Desktop/badges/skills/badge-quality/SKILL.md
7. The plan's prior art: every build script and folder the plan names. Open them; do not trust the plan's description of them.

Your job: decide whether this plan will produce a badge that looks like the mockup on the owner's iPhone, at rest and through a full turn, and find everything that would go wrong. Be adversarial: try to refute each claim, re-derive every number, and assume anything not written down will be guessed wrong by the builder. "Approved" is a valid and expected verdict when the plan is solid.

Check, in this order:
1. **Looks like the mockup**: does every part, line and color of the mockup have a construction step? Compare the plan's part list against the image yourself. Are proportions, depths and layers measured, not guessed?
2. **Clean in the app**: walk each build step in the app's environment (fixed studio light, AgX color finish, glow over 1.5 linear, floor reflection, about 416 pixels tall at rest, about 40 points on the Badges screen). Where would fuzz, wobbly lines, speckle, white dots, halos, dark fringes, washed out color or z fighting appear?
3. **Every angle**: early turn, both sides, back at half size. Gaps, banding, flashing edges, unfinished back, mottled side walls, gems losing color.
4. **Failure catalog**: are the badge's features listed correctly, so the right sections open? Is every layer 1 item and every item of an opened section handled? Are the plan's own risks specific to this badge?
5. **Your own risks**: look at the mockup and the plan with fresh eyes and find what neither the plan nor the catalog names. Use the catalog's layer 3 method: pre mortem, each part at each pose, each material facing the light and at a grazing angle, each join, what is new compared with approved badges.
6. **Method**: is there a proven method in an approved badge that is simpler or safer than the plan's? Name it, with its path.
7. **Facts**: every file, script, setting and number the plan cites exists and says what the plan claims.
8. **Checks that can fail**: for every check the plan names, the broken build it would catch. A check a broken build also passes is a BLOCKER.
9. **Handoff**: could a builder with only this plan, the mockup and AGENTS.md build it without asking a question?

Reply in exactly this format, one short line per finding:

VERDICT: APPROVED or TURNED DOWN

BLOCKERS: problems that would make the badge look wrong or broken in the app, or force the builder to guess. Each: what, the evidence (file and line, or what the mockup shows), and the exact edit to the plan.

RISKS: things likely to need care during the build, each with the checkpoint that should own it.

NITS: small wording or clarity fixes.

NEW RISKS: risks neither the plan nor the catalog names, each with a prevention and a check, or "none found".

STRONGEST CONCERN: the one thing most likely to make the owner unhappy with the result, even if the plan is approved.
