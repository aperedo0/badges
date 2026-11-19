# Ruby Crown overnight state (owner asleep from about Nov 8, 2026 02:00)

Owner instruction: "use the skill to get the badge right so I can wake up to it done". Use skills/badge-fresh-review: build, capture in app, review_pack, fresh badge-reviewer agent; repeat until closeness >= 90 (stop and report if two or three rounds show no clear gain). Owner deviations: every arch reaches the top middle; blue stones are ruby.

## Files
* Mockup checklist: review/checklist.md. Review settings: review.json (update build_front, build_box, poses per version).
* Pack: `python3 ../skills/badge-fresh-review/scripts/review_pack.py review.json candidateNN/review`
* App test: `python3 tools/app_try.py candidateNN --cloth` (installs into Badge3DPreviewRubyCrown, builds, captures 5 poses).
* USDZ writer: tools/write_crown_usdz.py (run with Blender's python3.13). Round 2 geometry: tools/crown2.py.
* Silhouette check offline: tools/silhouette.py GEOM.npz (projects through the app camera, prints width table vs mockup).
* Preview app crown stone shader: BadgeCrestGemSurface.metal profiles 12 (ruby) and 13 (clear); Swift maps CrestGem_CrownFoilRuby / CrestGem_CrownFoilClear. Backups in runtime_backup/.

## Scores
* v6: 62 (first reviewer), 55 (new setup with checklist). Review: candidate06/review_v2/review.md.
* v8: 62. v9: 62. v10: 62 (three flat rounds). v11: 70 (gain, so continuing). v12: 66. STOPPED (no clear gain); v11 reinstalled in the preview app with v11 shader settings. See REPORT.md.

## Round 2 targets (from the v6 review)
Model units: bottom -2.455, fleur tip 2.85, everything within radius 3.35 (width 6.7 limit). Circlet R 2.87 (y to -1.72). Velvet max r 3.08, top 1.06 at center, about 24 pleats with crease darkening texture. Arches (6 jeweled + front/back straps): stand off velvet, outer surface max 3.35 at y about -0.1, turn over at y 1.25, run level into the bell; thick and thin rails, satin channel, framed rubies, round diamonds, crest knob balls. Big ruby frames front and back only (kite 1.74 x 2.23, ruby 1.07 x 1.59 tall kite with crest, darker red). Leaves: big acanthus cluster at each jeweled arch foot, gem side leaves and C scrolls at frames, low tendrils with spiral and ball, bright yellow gold, no flat cutouts. Circlet: dark matte frieze, thick raised scrolls, 12 framed rubies, center ones larger touching the frame point. Bell taller (y 1.06 to 1.42), stacked neck rings, bigger fleur (thick petals spanning 1.47 wide).

## Log
* Round 2 started. Built crown2.py (v7 test only, never reviewed).
* v8: reviewed 62. Big issues: flat crossbar top, strap hidden in a velvet crease, bell buried by arch tops, crumpled foil leaves, pale gold, pyramid on frame top, small dark ruby.
* v9: dome lowered for the camera (back arches show above front ones), strap rides on flattened velvet, bell visible, smooth leaves with spiral ends, new circlet2 with narrow ledge, crest fan ruby 1.04 x 1.52, gold (1.0, 0.47, 0.09). Review running. Known: frieze still reads pale (try metallic (0.10, 0.065, 0.035) r 0.75); ~200k triangles (reduce later).

* v10 review top fixes: pointed acanthus fans, taller slimmer ruby without white facets, darker matte velvet with tighter folds, dark frieze with continuous sprays and bigger band rubies, inner arches moved in (now at 40 degrees), rounded staggered bends, smooth bell.
* v11 built with those; Blender checkpoint candidate11/source/ruby_crown_v11.blend. After its review: stop, write REPORT.md, leave v11 in the preview app.
* v12: frame bends back along the velvet (fixes edge-on plates in side views), ruby 0.80 x 1.40 with exposure 1.3, open leaf fans with hooked tips, taller bell (0.86 to 1.56), lower domed arch ring, frieze dielectric with zero specular.
