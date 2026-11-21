"""Diagnosis: paint chosen objects in flat colours and take the air away, to see which object is which in a
picture. Run before tools/v12_render.py in the same background Blender (nothing is saved)."""
import bpy
COL = {"Temple Nave Arch": (1, 0, 0), "Temple Nave Arch Trim": (1, 1, 0), "Temple Aisle Walls": (0, 0, 1), "Temple Arcade Arches": (0, 1, 0),
       "Temple Walls": (1, 0, 1), "Temple Pillar Front L": (0, 1, 1), "Temple Pillar Front R": (0, 1, 1), "Temple Apse Arch": (1, 0.4, 0),
       "Temple Vault": (1, 1, 1), "Temple Vault Ribs": (0.4, 0.4, 0.4), "Temple Apse Arch Trim": (0.6, 0.6, 0), "Temple Pillar Arcade L": (0, 0.5, 0.5),
       "Temple Pillar Apse L": (0.3, 0.3, 1), "Temple Corridor Ribs": (0.5, 0, 0), "Temple Corridor Vault": (0.2, 0, 0.2), "Temple Apse Wall": (0, 0.3, 0)}
for name, c in COL.items():
    o = bpy.data.objects.get(name)
    if o is None:
        continue
    m = bpy.data.materials.new("ID " + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*c, 1)
    e.inputs["Strength"].default_value = 0.6
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    o.data.materials.clear()
    o.data.materials.append(m)
for o in bpy.data.objects:
    if o.type == "MESH" and any(mt and ("Air" in mt.name or "Fog" in mt.name or "Mist" in mt.name or "Dust" in mt.name) for mt in o.data.materials):
        o.hide_render = True
