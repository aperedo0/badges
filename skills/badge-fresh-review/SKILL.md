---
name: badge-fresh-review
description: Independent review of a badge version against the owner's mockup by a brand new agent with no context. First a clean finish gate (no fuzz, jagged edges, specks or dots at the phone's real pixels, at rest and turning), then a closeness score out of 100 with everything that is off. Loop until shippable and 90. Use after a version is captured in the app, before showing it to the owner or calling it close, and when the owner asks for a fresh look, a second opinion or a closeness rating.
---

# Badge fresh review

Never judge your own badge as close. After each version, a brand new agent that has seen nothing of your work compares it with the owner's mockup, lists everything that is off, and gives a closeness score. Below 90, fix all of it and run a new reviewer on the next version.

Two separate questions, always in this order: **is it shippable** (a clean finish at the phone's real pixels) and **how close is it** to the mockup. A close design with a surface defect is not shippable, and no closeness score may hide that.

Why (owner rule, November 8, 2026): a Ruby Crown its builder called close scored 62. At the same height it was 15% too narrow, with thin arches and sparse leaves, and the builder's own crops had hidden all of it.

## How it stays cheap and thorough

* **One lean reviewer, one step.** Pictures cost little (at most about 1,600 tokens each); an agent's setup, repeated on every step, costs most. So one reviewer opens every picture at once and answers right away.
* **Far and close.** Far views show silhouette, proportions and color mass; close ups show details too small to see from afar.
* **The mockup itself, never a written description of it.** Reviewers compare pictures with pictures.
* **Numbers measured by script**, so the reviewer spends no steps measuring.
* **Keep the strong model** (the agent definitions pin it).

## 0. Clean finish gate: before every reviewer and before the owner sees anything

Why (owner rule, November 8, 2026): three enamel badges reached the owner with fuzz and glitter along every gold line, called atrocious. Reviewers had written "crumpled foil", "sawtooth" and "speckle" for two rounds; the builder read that as a shape problem and never zoomed in. The cause was the surface itself: a grid of triangles under a traced picture.

1. **Blender first** (owner rule, November 9, 2026). Before any simulator run, sweep the version inside the open Blender: zoomed renders of every part, front, both sides and back, plus the whole badge at phone size enlarged 4x (`golden_storm_fable_20261109/blender_zoom.py` is the working example: about half a minute). Run `badge-build/scripts/light_centers.py` on the candidate: it must print 0 centers (dark specks where a light reflects into the camera). Fix and sweep again until clean. Develop and judge working versions there (owner rule, November 12, 2026); go to the simulator only when Blender shows the version clean and you would let the owner judge it.
2. **Then the app capture.** Open the pack's finish pictures yourself (step 2 makes them): `finish_full_size.png` (real pixels), `finish_2x_*.png` (the **whole** badge at 2x in tiles), `finish_4x.png` (busiest lines), `finish_outline_4x.png` (the outline's tips and brightest spots) and `finish_turn_*.png` (each turned pose at real pixels). Look for fuzz, haze, smeared or soft edges, wobbly lines, stair steps, speckle, dark specks, white dots on the outline, mottling and banding.
   * **Judge against clean, never against the previous version.** On November 8, 2026 a rebuild was called "free of fuzz" because the old glitter was gone; the owner saw new fuzz at once.
   * **Motion**: look at the turn pictures in a row; edges that crawl or sparkle while turning are defects even when each picture looks fine.
3. **Then a fresh agent checks the finish alone**: spawn `badge-reviewer` with the prompt "Open <review folder>/finish_brief.md first, then follow it exactly." The pack writes that brief with fixed wording, so every round asks the same question. The full closeness review (step 3) runs only after it answers SHIPPABLE: yes.
4. **Any defect means not shippable.** No closeness review, and never shown to the owner as a candidate.
5. **Understand why before changing anything.** Find the cause with one direct test and write it in one line in the version notes:
   * draw the mesh triangles over a 4x crop: lines crossing a grid at random angles mean zigzag geometry;
   * swap the color map for one flat color: if the defect stays, it is geometry or normals; if it goes, it is the texture;
   * raise the roughness: glints from tiny bumps fade, real shape stays;
   * a single dark pixel in a smooth bright area: run `light_centers.py`;
   * compare with the previous version at the same zoom.
6. Fix the cause, capture again, and repeat the gate. If the cause is the way the surface is built, change the method; tuning the same method again is not a fix. **The same defect failing the gate three times: stop and show the owner** the pictures, the cause and a different method.

## 1. Once per badge: settings

Write `review.json` in the badge's working folder (format at the top of `scripts/review_pack.py`):
* the mockup and the badge's center column and top and bottom rows in it;
* the regions to show up close, in badge heights around the center (about six);
* the owner's intended differences, one line each. **List every color the app cannot reach here, as what it shows instead** ("bright lemon shows as pale lemon"); the reviewer counts any other color difference as off.

## 2. Each version: pictures

1. Capture the build in the app (`badge-build/scripts/app_try.py`): the resting front and the turned poses.
2. Put the front capture, its badge box and the pose captures in `review.json`. The box is the badge's center column, its highest row, and its lowest row at the floor contact, never inside the reflection. The pack scales each picture by its own top and bottom so both badges stand the same height; it never scales width separately, so width errors show.
3. Run `review_pack.py review.json <version folder>/review` (Python 3.11: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`). It writes:
   * far views: the same height side by side, both at phone size, and both outlines over the mockup;
   * matching close ups of each region, the mockup on the left;
   * the turn strip (smooth, for shape) and each turned pose at real pixels (for finish);
   * the finish pictures (step 0);
   * a table of silhouette widths;
   * for you only: the outline overlap score (1.00 = the same outline) in `overlap.json` and on the console, and `outline_mismatch.png` (red = the mockup has it and the build does not, blue = the build adds it). It is kept out of the brief: a reviewer anchors on a number;
   * `finish_brief.md` and `brief.md`, each ending in a brief version (a fingerprint of the reviewer instructions).
4. Look at the pictures before sending them: the outlines must hug both badges, and each close up pair must show the same area. Fix the settings if not.
5. **Outline overlap below 0.85: fix the outline first.** Open `outline_mismatch.png`; a wrong shape is cheaper to fix now than after a review round. The score only catches failures: a high score says nothing about closeness (Ruby Crown version 12 scored 0.91 and its review gave closeness 66). Red or blue from an intended difference, or from a mockup's drop shadow, does not count.

## 3. Each version: the reviewer

1. In Claude Code, spawn the `badge-reviewer` agent (`.claude/agents/badge-reviewer.md`). Its whole prompt is "Open <path>/brief.md first, then follow it exactly." A new reviewer every round, never a continued one. If the agent type is not loaded (it loads when a session starts), or in another tool, give a fresh general agent the instructions in `.claude/agents/badge-reviewer.md` followed by the brief path.
2. Add nothing about your process, your doubts or what you changed; that anchors it.
3. Never predict or report its result before it arrives.

## 4. Use the report

1. Save it as `review.md` next to the pictures, the shippable verdict and score first, with the brief version.
2. **SHIPPABLE: no comes before everything else.** Run step 0's cause test on each defect it lists and fix those first. Words like crumpled, foil, sawtooth, stair steps, speckle, fuzz or glitter anywhere in a review mean a surface defect, even when filed under shape.
3. Check each claim against the model before acting. A reviewer can miss parts that are only small. Turn such a claim into the real fix ("make it bigger") rather than dismissing it.
4. **Go back when a version gets worse** (owner rule, November 14, 2026). If the new version is not shippable where the previous one was, scores at least 3 points lower, or its outline overlap drops by 0.03 or more, do not build on it. Reload the previous version's saved Blender checkpoint, note what the failed change was and why it made things worse, and try a different fix from there. Reviewers differ by a few points, so a drop of 1 or 2 alone is noise. **Compare scores only under the same brief version**; after the instructions change, repack and review the previous version once to get a comparable score.
5. Fix everything it found in one round, worst first: surface defects, then proportions, silhouette and ornament mass, then small details.
6. When relaying it to the owner, rewrite each point in their words (clarity skill), keep the score and the measurements, and say where you think it is wrong.
7. Never relay a build that is not shippable as a score alone. Say first, plainly, that it is not shippable, what the defect looks like and what causes it.

## 5. When to stop

* **90 or higher and shippable**: run badge-quality's final piece reduction pass (`badge-quality/references/finish-optimization.md`), capture the reduced version in the app, check it is unchanged, then deliver with the far side by side and the last review. A score of 90 with a surface defect is not done.
* **Below 90**: fix and run a new reviewer on the next version.
* **No clear gain after two or three reviewed versions** (flat score, the same top items), **or five reviewed versions in all**: stop and show the owner the pictures and review, with what you think blocks you (AGENTS.md section 6). If the repeating items are surface defects, the way the surface is built is wrong: say so and propose a different method. Continue only when the owner says so.
* **The owner asks to see a review**: show it and pause until they answer.

The open Blender rules (one saved file per badge, never delete objects, never overwrite unsaved changes, reopening it) are in badge-quality's "Build it in the owner's open Blender".

## Pitfalls

* Different reviewers score a few points apart. Trust the trend and the listed items over one number.
* The outline finder uses color against a neutral background. For a grey or silver badge, lower its threshold or check the outlines by eye.
* The overlap score counts a mockup's drop shadow as badge (a red strip along one side, as on Golden Storm), and a dark open gap inside a dark badge can count as badge in one picture and not the other (Emerald Stag). Judge the red and blue shapes, not the number.
* Before November 14, 2026 the pack filled the area outside a narrow mockup with black, so the mockup's whole frame counted as badge: width tables in reviews of mockups narrower than the crop (Golden Storm, Campfire Night) were wrong on the mockup side. Fixed.
* Never put your own verdict ("it is close now") in a brief.
