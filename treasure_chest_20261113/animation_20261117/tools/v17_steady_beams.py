"""Version 17: the two shafts of night light hold steady (owner, 2026-11-23).

Run inside Claude_Temple_Ceiling.blend; safe to run again; two numbers change and nothing else.

The owner, on the whole scene video of Codex_Temple_Fire.blend: "the light on the left shifts, like very sudden
very sharp shifts ... it happens between the 2 and 3 second mark ... I still want the light and the sand. just no
sudden light change".

What it was. At second 2.00 exactly (video frame 60, the arrival's frame 60, scene frame 32, the chest's third
impact) the right side of the left shaft goes from a soft edge to a wider beam with a hard edge in one frame, and
stays that way for the rest of the video. It is the only such jump in the 860 frames. Nothing in the scene
switches there: no keyed number, no light, no camera move, and it is not the dust's clock, the landing dust, the
grit, motion blur or the other lights' shadows (each was tested by rendering those two frames).

The shape of each shaft is the shadow of a mask (a plate with the hole's outline, Temple Shaft Mask L and R) in
the light of a spot 270 above it (Temple Shaft L and R). The renderer keeps every shadow at several levels of
detail and, for the air, uses the finest level that happens to be in memory. Which levels are in memory depends on
what the camera sees: with the chest's body in view at rest the left shaft got a finer level (hard edge); with
the chest still in the air, hidden, or not yet in the picture it got the coarsest (soft edge). So the beam's edge
followed the chest, not the light.

The fix: both shaft lights are told never to use more shadow detail than the coarsest level (Resolution Limit 10,
was 0.001). The beam then cannot change with what is in view. Tested limits: 1.2, 2 and 3 still jump; 5, 10 and
40 do not and give the same picture. The beam keeps the hard right edge it has had for most of the video.

    V17 test, saves nothing:  blender -b <file> --python tools/v17_steady_beams.py --python tools/v12_render.py
V17_LIMIT sets the number (10)."""
import bpy, os

LIMIT = float(os.environ.get("V17_LIMIT", "10"))
done = []
for name in ("Temple Shaft L", "Temple Shaft R"):
    light = bpy.data.objects[name].data
    done.append((name, round(light.shadow_maximum_resolution, 4), LIMIT))
    light.shadow_maximum_resolution = LIMIT
bpy.context.view_layer.update()
print("V17 steady beams (light, limit before, limit now):", done, flush=True)
