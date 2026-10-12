Approved Diamond: original envelope, widest band raised 5%, medium camera glints.
Model and source copies match the app. Generated Home and art copies were removed during owner-requested cleanup.
The authoritative art remains in the app: ScreenTime/SupportingFiles/Assets.xcassets/BadgeArtDiamond.imageset/BadgeArtDiamond.png.

Rebuild model with Blender Python (pxr and numpy):
  /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I tools/build_original_raised_band.py /tmp/diamond-rebuild
Regenerate medium-glint source:
  python3 tools/make_glints.py /tmp/diamond-glints 0.035
To recut the 600 x 600 art later, capture a fresh actual Diamond Home render at the established native simulator scale as /tmp/Home.png:
  python3 tools/still_cut.py still_geometry.npz /tmp/Home.png /tmp/BadgeArtDiamond.png

The final genuine build/test summary is gate_proof.txt. Raw temporary bundles were cleaned after approval.
Runtime facet kernel and environment remain in the app repo and were never removed.
