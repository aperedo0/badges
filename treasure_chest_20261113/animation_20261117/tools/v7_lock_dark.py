"""Version 7: a dark lock inside (owner, 2026-11-18: the bright rectangle inside the keyhole; asked whether a
real lock works that way, then: darken the inside of the lock).

The rectangle is the lock's bolt (R Lab Chest Key Driven Slider) sliding right to left inside the lock
case as it unlocks, which is how a real chest lock moves. But a closed lock gets almost no light
inside, and EEVEE lit the bolt like the brass plate outside, so it read as a glowing block. The bolt
only shows through the keyhole, so it gets its own dark, slightly rough version of the aged bronze:
the keyhole reads as a shadowy hole with the bolt's edge just catching a little light as it slides.
Object level material, so the shared mesh and the brass outside are unchanged. Run inside Blender;
safe to run again."""
import bpy

src = bpy.data.materials["Simple aged bronze"]
dark = bpy.data.materials.get("Simple aged bronze lock inside")
if dark is None:
    dark = src.copy()
    dark.name = "Simple aged bronze lock inside"
nt = dark.node_tree
bsdf = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
# darken whatever feeds the base colour where the bolt is deep inside the lock
mul = nt.nodes.get("v7 lock inside darken")
if mul is None:
    mul = nt.nodes.new("ShaderNodeMix"); mul.name = "v7 lock inside darken"
    mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"
    bc = bsdf.inputs["Base Color"]
    if bc.is_linked:
        nt.links.new(bc.links[0].from_socket, mul.inputs["A"])
    else:
        mul.inputs["A"].default_value = bc.default_value
    nt.links.new(mul.outputs["Result"], bc)
# Dark only deep in the lock: the keyhole shows the bolt's lower part (local z about -0.6 to -0.7);
# its top end, the catch that holds the latch, shows in the notch on top of the lock plate once the
# latch swings up and must stay plain brass (dark there read as a black square, owner 2026-11-18).
tc = nt.nodes.get("v7 lock inside coords") or nt.nodes.new("ShaderNodeTexCoord")
tc.name = "v7 lock inside coords"
sz = nt.nodes.get("v7 lock inside z") or nt.nodes.new("ShaderNodeSeparateXYZ")
sz.name = "v7 lock inside z"
band = nt.nodes.get("v7 lock inside band") or nt.nodes.new("ShaderNodeMapRange")
band.name = "v7 lock inside band"
band.inputs["From Min"].default_value, band.inputs["From Max"].default_value = -0.42, -0.30
band.inputs["To Min"].default_value, band.inputs["To Max"].default_value = 1.0, 0.0
nt.links.new(tc.outputs["Object"], sz.inputs[0])
nt.links.new(sz.outputs["Z"], band.inputs["Value"])
nt.links.new(band.outputs["Result"], mul.inputs["Factor"])
mul.inputs["B"].default_value = (0.09, 0.08, 0.07, 1.0)
# same roughness as the brass outside (an earlier version roughened the whole bolt)
sb = next(n for n in src.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
if not bsdf.inputs["Roughness"].is_linked and not sb.inputs["Roughness"].is_linked:
    bsdf.inputs["Roughness"].default_value = sb.inputs["Roughness"].default_value

bolt = bpy.data.objects["R Lab Chest Key Driven Slider"]
for slot in bolt.material_slots:
    slot.link = "OBJECT"
    slot.material = dark
print("v7 lock dark", [s.material.name for s in bolt.material_slots])
