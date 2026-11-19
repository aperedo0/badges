---
name: fair-lighting-checks
description: Optional technique. Before changing a material in Blender, prove the problem is not the lighting, environment, camera, denoising or color management. Covers neutral and reference matched light, grazing light, gray clay, a clean metal control, lights off one by one, raw versus denoised renders, and aimed reflection lights. Use when a material looks soft, flat, too dark, orange or pink, metal reads black or washed out, a bright edge, streak or wedge appears, or a Blender render is compared with a reference. For a material's input values use shader-aov-diagnostics. For badges the app's fixed light stays the final judge.
---

# Fair lighting checks

An option, not a rule. The owner's word and the workspace `AGENTS.md` (Claude sees it as `CLAUDE.md`) always win.

## The idea

A difference between a render and a reference can come from light direction, size or color, the environment, camera, exposure, color management, denoising, texture filtering, pigment, roughness, normals or geometry. Change one at a time, hold the rest fixed, and change the material only once the light is ruled out. On the treasure chest, moving one light revealed more wood detail than any material change.

## Set up once

* Put diagnostic lights in a separate review scene or a copy. The original scene's lights stay exact.
* Use the same camera, exposure, view transform and resolution for every comparison. Save named close and full views.
* Keep two light sets: **neutral** (white lights, Poly Haven Studio Small 03 desaturated through an RGB to BW node, tried at two rotations) and **reference matched** (warm key and fill like the reference).
* Separate the visible backdrop from what metal reflects: in the world, a Mix Shader driven by Light Path **Is Camera Ray** shows a dark backdrop to the camera while reflections still see the HDRI.

## The checks

Pick only the ones the question needs.

| Question | Check | What it showed on the chest |
|---|---|---|
| Is the relief real or painted? | Gray clay render plus grazing light | Channels were real geometry; some fractures existed only in pigment |
| Is it the pigment or the light? | Neutral light render | The wood was reddish brown; the warm lights pushed it orange |
| Is the light hiding detail? | Change only the key light's direction, then its size | One direction change revealed more fiber than any material edit; a smaller source gave clearer recess shadows |
| Which light makes this highlight? | Turn lights off one at a time | The broad fill made the continuous bright metal edge; the rear light did nothing |
| Is that area just in shadow? | Render with one light at a time, or ray cast from the surface toward each light | The lock blocked the warm key on the right, so the cool fill made that side look less detailed |
| Is the metal hiding its relief? | Clean metal control (below) | A nearly black metallic base color was hiding the hammer marks |
| Is it denoising or filtering? | Raw and denoised from the same samples; a narrower pixel filter | Neither was the cause; the standard filter stayed |
| Why pale pink highlights? | Same render with the lights' `visible_glossy = False` | Mostly light reflecting off smoother raised wood; pigment and roughness trials changed little |

**Gray clay:** `bpy.context.view_layer.material_override = clay` with a plain gray Principled material. It drops bump, normal maps and the material's Displacement output, so only mesh and modifier geometry shades. For relief that comes from material displacement, copy the material and unlink only Base Color, Roughness and Normal instead.

**Raw versus denoised:** `view_layer.cycles.denoising_store_passes = True` with `image_settings.media_type = 'MULTI_LAYER_IMAGE'` saves a Noisy Image pass beside the denoised one.

**Clean metal control:** keep geometry and normals, set the base color to a measured reflectance, metallic 1, and try a few roughness values. The owner's prompt gave Filament's clean iron as sRGB `#C4C6C6`; `Color((0.769, 0.776, 0.776)).from_srgb_to_scene_linear()` gives (0.552, 0.565, 0.565). For other metals read the table at google.github.io/filament/main/materials.html rather than values from memory. This is a diagnostic, never the finished material.

## Metal needs something to reflect

A metal face mirrors its surroundings, so a black environment gives black metal. Light the place its reflection points to:

```python
# P, N: surface point and normal in world space
V = (cam.matrix_world.translation - P).normalized()
L = (2 * N.dot(V) * N - V).normalized()            # mirror direction
light.location = P + L * distance
light.rotation_euler = (P - light.location).to_track_quat('-Z', 'Y').to_euler()
light.visible_diffuse = False                       # reflection only, Cycles and EEVEE
receivers = bpy.data.collections.new('Reflection receivers')
receivers.objects.link(target)                      # a Collection, not a list
light.light_linking.receiver_collection = receivers
```

* **Narrow beats broad.** Narrow warm strips aimed at the bevels gave warm edge highlights; broad strong sources washed out the whole face.
* **Reflection only means ray visibility.** The light's `diffuse_factor` does nothing in Cycles. The chest strips used it, so they also lit the face.
* **Long strips:** this aim keeps the light's X side level, so put the long side in `size`, not `size_y`. On the chest a tilted strip made a sharp bright wedge that looked like a material bug.
* Chest iron environment: 0.45 to 0.65 read too light, 0.18 hid face detail, 0.35 tinted (1, 0.88, 0.72) kept a dark face with readable reflections.
* Warm edges came from warm reflections, never from gold paint or emission.
* Cycles Light Groups only when one render must split many lights' contributions. Turning lights off is usually simpler.

Worked code: `treasure_chest_20261113/phase05/iron_character/edge_reflection.py` (reflection strips, light linking) and `environment.py` (tinted HDRI modes).

## Never

* Paint highlights or shadows into the base color to fix a lighting problem.
* Change two things between the renders you compare.
* Judge the look under the grazing test light: it exaggerates dark channels.
* Judge fine detail in Material Preview or in a small denoised draft.
* Trust the Blender connection's viewport capture in Cycles: it returns black. Open the saved render or a screenshot of the real window.

## Badges

The app's light is fixed (one environment map plus 8 point lights, key upper left, AgX view, glow above 1.5), so Blender lighting can never prove a badge's look, and only geometry and materials ship. Never tune Blender lights to make a badge look right. Use these checks to learn whether a problem lives in the material, then confirm in the app once the badge is ready (`AGENTS.md` sections 0 and 5).

* A face far off in lightness in the app usually mirrors a studio light or a dark area: change its tilt, not its paint (`badge-build`). The app's eight light positions are in `skills/badge-build/scripts/light_centers.py`; the mirror formula above shows which one a face sees.
* If the color still will not match, use the measure and solve method in `AGENTS.md` section 4.
* The clean metal control still helps: it shows whether a dark base color is hiding the shape.
