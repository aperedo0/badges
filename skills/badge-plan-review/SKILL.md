---
name: badge-plan-review
description: Have fresh agents with no context approve or turn down a badge build plan before any modeling starts, judging whether it will produce a badge that looks like the owner's mockup in the iPhone app from every angle and what will go wrong. Loops until a reviewer approves with no blockers. Use right after badge-plan writes or changes a badge's PLAN.md, when the owner asks to review, check or approve a badge plan, or when a build returns to its plan after a failed checkpoint. Never modifies the badge model.
---

# Badge plan review

The stage between planning and building: plan → **review until approved** → build in the open Blender. A plan approved here is what makes the build easy; a weak plan caught here costs minutes, a weak plan caught in the app costs days.

## 1. Put the plan on disk

The reviewer cannot see the conversation. The plan must be the badge folder's `PLAN.md`, complete, with the mockup path in it.

## 2. One fresh reviewer per round

Spawn the `badge-plan-reviewer` agent (defined in the badges repository's `.claude/agents`; in another tool, a fresh agent given that file's instructions). Fill [the brief](references/reviewer-brief.md) with the name, round number and paths and save it beside the plan as `plan_review_brief.md`. The prompt is only: "Your brief is in this file: <path>. Open it first, then follow it exactly."

* The agent definition pins the strong model. A missed problem costs a whole build.
* A new reviewer every round, never a continued one.
* Add nothing about your doubts or preferences; that anchors it.

## 3. Adjudicate

The reviewer answers APPROVED or TURNED DOWN, with every finding marked BLOCKER, RISK or NIT and an exact plan edit.

* Check each claim against the files and the mockup before accepting it.
* Apply accepted edits to `PLAN.md`. Record rejected findings with a one line reason.
* A real risk the catalog does not name goes into the catalog too (its "Growing the catalog" rule), so the next badge is checked for it.
* Any change to what the owner will see (look, size, colors, scope) goes to the owner before the next round.

## 4. Loop

* **Round 1 is mandatory.** Approved with no blockers: done.
* **Turned down, or blockers found**: fix, then a fresh reviewer checks the fixes (fixes are prime suspects) and looks for new blockers. From round 2, fill the brief's round line with the round number: the reviewer then verifies the fixes recorded in the plan's Review log and looks only for new blockers. Use the brief template unchanged otherwise; never write a shorter brief of your own or add which risks you think are now addressed (that anchors it). Each round cost 210,000 to 340,000 tokens on the Mountain Sunburst.
* Risks and nits fold in without another round; only blockers extend the loop.
* **After round 2, numbers go to the build checks, but only to checks that exist** (owner's choice, November 9, 2026). A numeric blocker skips round 3 only when a named script prints and fails on that number today: `validate.py` (bounds, triangle budget, stacking gap of 0.006, outlines running together), `material_map.py` (local material misses), `light_centers.py` (dark specks on enamel). Write in the plan which script owns each such number. Anything else (slopes, step heights, crest minus floor) has no check yet: run round 3, or add the printout to the script first.
* **Cap: 3 rounds.** Blockers still open after round 3 go to the owner with the reviewer's words and your recommendation.

## 5. Log and hand off

Append `## Review log` to `PLAN.md`: per round, the verdict, blockers, risks and nits, accepted and rejected with reasons; the final line `APPROVED (round N)` or `CAPPED: owner decides`. Set the status line in section 1.

Tell the owner in their words: what they will see, the build order in one sentence, the verdict, the risks the build checkpoints must own, and any open decision as a yes or no question with your recommendation. Building starts only from an approved plan with no open decisions.

## During the build

When a checkpoint fails because of the method, stop: revise the plan's affected part and run one review round on the change before building on. Small fixes that stay within the plan need no review. **At most one return to the plan per badge without the owner**: a second method failure goes to the owner with pictures, what failed and a proposed different approach (AGENTS.md section 6).
