# Ruby Crown overnight (Claude), November 8, 2026

Goal: closeness 90 from a fresh reviewer (skills/badge-fresh-review). Reached 70, then stopped by the skill's rule: no clear gain over several rounds.

## Scores (fresh badge-reviewer, far views, close ups and the mockup checklist)

| version | closeness | main change |
|---|---|---|
| 6 | 55 | starting point (the version the owner saw) |
| 8 | 62 | rebuilt: wide low crown, standing arches, pleated velvet, front and back ruby frames, sculpted leaves |
| 9 | 62 | rounder dome for the app camera, strap on the velvet, smooth leaves with spirals, new band |
| 10 | 62 | barrel outline, wider jeweled arches, bigger bell |
| 11 | 70 | pointed acanthus fans, taller crested ruby, darker velvet and frieze, staggered arches |
| 12 | 66 | overcorrected: ruby too dark, bell became a cone |

Version 11 is installed in Badge Studio Preview (Ruby Crown). Pictures: `candidate11/review/far_same_height.png` (same height as the mockup), `candidate11/review/turns.png`, outline at 4x `candidate11/outline4x.png` (clean). Model `candidate11/model.usdz` (210,000 triangles, 3.4 MB), Blender `candidate11/source/ruby_crown_v11.blend`, builder `tools/crown2.py`.

## What matches now
* Proportions: the outline is within a few points of the mockup at every height (width 1.27 times the height, widest at mid height).
* Eight arches all meeting at the top under the bell, ruby fleur de lis (owner's changes).
* Deep crimson pleated velvet, jeweled arches with rubies and white stones, big ruby setting front and back with a white stone border, band with 12 framed rubies, acanthus leafwork, clean outline from every side.

## What still blocks 90 (the same items in every review)
1. **Leafwork:** the mockup's carved acanthus (curled, veined lobes, open lace with dark gaps) is the biggest gap. Procedural leaves from scripts read as blobs, cardboard or spikes. Getting this right likely needs hand sculpting one leaf and one scroll in Blender and repeating them.
2. **Light and color:** under the app's fixed bright studio, polished gold facing the camera turns pale cream and the frieze reads light; the mockup's dark backdrop gives deep brown shadows. Material changes swing between "too orange" and "too pale" in different reviews.
3. **Camera from above:** the app camera looks down slightly, so the band reads as a curve and the back arches show above the front ones. Reviewers count both against it; they cannot be fixed in the model alone.
4. **Velvet pile and gem sparkle:** smooth velvet reads as plastic; a nap texture would break the owner's no grain rule.
5. **Reviewer variance:** different reviewers score a few points apart and sometimes ask for opposite changes (bell taller, then shorter; folds wider, then narrower).

## App state
* Preview app (`emerald_trophy_20261025/preview`, not committed by git): crown stone shader profiles 12, 13 and 14 in `BadgeCrestGemSurface.metal` (big rubies, clear stones, small rubies), names mapped in `Badge3DLiveBadge.swift`. Originals before the crown in `runtime_backup/` with checksums. Codex's crown model backed up at `runtime_backup/preview_crown_before_claude.usdz`.
* Production app untouched. Nothing committed.
* Triangles: 210,000, about five times the guideline; reduce once the design is approved.
