Ruby Heart: smooth upper gold rim

Replaced the abrupt shoulder bend in every swept rim profile with a curve matching position, tangent and curvature at its ends. The repair is mirrored across both lobes and the back. The center notch and bottom tip remain intentional points. Maximum local displacement is 0.0402 model units.

Only Frame points and normals differ in the delivered USDZ. The ruby mesh and its runtime optical material, gold shader graph, roughness texture bytes, UVs and topology remain unchanged. The frame stays closed. The badge remains 2 meshes and 26680 triangles. The source approved model is preserved. Final asset: mobile/ruby_heart.usdz.

Development used the live Blender connection and actual front, back and side renders. The saved complete scene is ruby_heart.blend, with its reference beside it. The development gem material was used only to inspect the surrounding rim: the untouched custom app optics were judged in the final simulator check.

The private Badge Studio Preview build succeeded. Native front, early turn, both sides, back and a bounded full rotation were checked. The loaded asset hash matches candidate01/validation.json. Every preview Swift and Metal source remained identical, and the approved Sapphire asset remained identical. Production code was not edited. Simulator left on Ruby Heart at rest.

Independent fresh visual review passed the requested curve revision at 95/100 for scoped smoothness, with no visible regressions. See candidate01/comparison.png and candidate01/review.md.

Rebuild: execute tools/load_live.py through the live Blender bridge, run tools/package.py with the Blender bundled Python, and render with tools/render_live.py. These tools reuse the preserved original Ruby Heart builder and source asset. Tools/capture.py performs native final captures only after the repaired model is installed and launched through XcodeBuildMCP.
