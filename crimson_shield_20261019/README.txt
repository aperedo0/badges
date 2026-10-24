CRIMSON SHIELD

A new floating shield built from the owner's October 19 reference.
The private badge picker calls it Crimson Shield.

Final model: mobile/crimson_shield_badge_mobile.usdz
Editable scene: crimson_shield.blend
Reference: reference.png
Geometry and material settings: design.json and palette.json
Rebuild source: prepare.py, build_live.py, pack.py
Contract check: validate.py

The shield uses its own outline, not the circular coin casing. Front faces
positive Z, Y is up, transforms are identity. Its lowest point is Y minus
2.455, the shared floating height. Use size 1 and lift 0 in the preview.
Both sides have the layered silver frame, directionally brushed dark field,
continuous recessed red mineral inlay, creased corner ornaments and faceted ruby settings.
The broad frame bevels catch the studio from their inward raised edge.
Diagonal scarf joints are real geometry on both sides of the frame.
The back is a proper half turn of the front; the edge is solid metal.

The center now uses directional brushing derived from the owner's metal photo,
with a less matte physical finish. The broad frame face is about 23% wider;
the outside silhouette and bevel angle remain the same. The inner recess
is deeper to separate the silver from the red trim.

The textures contain fine intrinsic reflectance and roughness grain.
They contain no studio light bands, painted highlights or emission.
The rubies use ordinary physical materials, not the Diamond gem shader.
No recognized coin casing or material names occur in the final model.

App dependency: app_material.patch restores live anisotropy on the exact
material CrimsonShield_BrushedField. It is already in the separate preview
app; production integration must carry the patch. Read app_material_README.txt.
The USDZ alone contains the color and roughness grain, but not this runtime
reflection direction. Both faces and the mirrored floor image use it.

Rebuild from the badges workspace:
1. Run python3 crimson_shield_20261019/prepare.py.
2. Keep previous/crimson_shield_before_brushing.usdz as the complete source
   imported into Blender for hidden working context. Create the temporary
   /tmp/crimson_shield_20261019 directory if it does not already exist.
3. Run the live Blender helper on this project's build_live.py.
4. Run pack.py with the Blender bundled Python, which includes USD.
5. Run validate.py with that Python and usdchecker with its ARKit option.

The live build exports intermediate mesh arrays to /tmp. They are scratch
and need not be kept. Rebuilding never changes the original Iron model.
The saved Blender scene is independently editable and contains its images.
