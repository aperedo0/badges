import bpy
import hashlib
import json
import shutil
from pathlib import Path

R = Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113')
C = R / 'phase03/wood_sample44/candidate03'
sc = bpy.context.scene
assert bpy.data.filepath == str(C / 'chest.blend') and sc.frame_current == 0
exec(compile((R / 'phase01/tools/frame36_geometry.py').read_text(), 'g36', 'exec'))
baseline = json.loads((C / 'before_geometry_manifest.json').read_text())
models = [o for o in sc.objects if o.type == 'MESH' and o.get('full_form')]
assert len(models) == 155
for obj in models:
    current = capture36(obj)
    previous = baseline[obj.name]
    for key in ('vertex_hash', 'triangle_hash', 'normal_hash'):
        assert current[key] == previous[key], (obj.name, key)
    if obj.name != 'Chest Body Envelope':
        assert current['materials'] == previous['materials'], obj.name
body = sc.objects['Chest Body Envelope']
material = bpy.data.materials['Chest Wood Sample44 v3']
slot = list(body.data.materials).index(material)
assert [f.index for f in body.data.polygons if f.material_index == slot] == json.loads((C / 'isolation_proof.json').read_text())['faces']
assert material.node_tree.nodes['Single plank physical tangent normal'].inputs['Strength'].default_value == 1
assert all(material.node_tree.nodes['Single plank ' + role].image.packed_file for role in ('albedo', 'roughness', 'normal'))
for relative, digest in json.loads((C / 'baseline43_hashes.json').read_text()).items():
    assert hashlib.sha256((R / 'phase01/candidate43' / relative).read_bytes()).hexdigest() == digest

# Save the current scene without loading, dropping or replacing any window changes.
prior = bpy.context.preferences.filepaths.save_version
try:
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, compress=True)
finally:
    bpy.context.preferences.filepaths.save_version = prior
assert not bpy.data.is_dirty
shutil.copy2(C / 'chest.blend', R / 'treasure_chest.blend')
digest = hashlib.sha256((C / 'chest.blend').read_bytes()).hexdigest()
assert hashlib.sha256((R / 'treasure_chest.blend').read_bytes()).hexdigest() == digest
(C / 'save_proof.json').write_text(json.dumps(dict(current_blend=bpy.data.filepath, canonical_copy=str(R / 'treasure_chest.blend'), sha256=digest, source43_preserved=True, mesh_count=155, selected_polygons=28, all_images_packed=True), indent=2))
print('Saved current one plank sample and identical canonical copy. Source43 remains preserved.')
