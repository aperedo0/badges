"""Put the current sounds (the eighth try) on the timeline of the Blender file that is open, as sound strips (2026-11-23).
The owner: "add the sounds we have been working with to Codex_Temple_Fire.blend, sounds only".

Run inside Blender, with the file open, after sound/tools/s8_for_blender.py has made sound/blend/:
    exec(compile(open(path).read(), path, "exec"), {"__file__": path})
It only adds sound: one strip per sound in the Chest Reveal scene, each packed into the file so the file carries it.
Nothing else in the file is touched, the frame is not moved and the file is not saved here. Sound strips alone do not
change what a render shows. Safe to run again: a strip that is already there is left as it is.

On the scene's own timeline (the story played straight through):
    Chest lands (three drops)      from frame  16   (the drops at 16.6, 21.6 and 32.1)
    Lock                           from frame  49   (the key turns from 50.3, the clack on the flash at 56)
    Lid opens (drawer)             from frame  92   (the slide from 94 to 111)
    Fire                           from frame 126   (as the first fire catches; runs on through the ending loop)
    Waiting rattles (footsteps)    from frame  50, MUTED: the wait, where the chest rattles three times, is not on this
                                   timeline (tools/v12_render.py makes it while the chest is held on frame 49). The strip
                                   is the whole 225 frame wait, kept here for whoever builds that piece.
"""
import bpy, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "blend"))
plan = json.load(open(os.path.join(SRC, "strips.json")))
scn = bpy.data.scenes["Chest Reveal"]
assert scn.render.fps == plan["fps"] and scn.render.fps_base == 1.0, "the sounds are timed at 30 frames a second"
se = scn.sequence_editor or scn.sequence_editor_create()
have = {s.name for s in se.strips_all}
added = []
for st in plan["strips"]:
    if st["name"] in have:
        continue
    start = st["scene_frame"] if st["scene_frame"] is not None else plan["hold_frame"] + 1
    s = se.strips.new_sound(st["name"], os.path.join(SRC, st["file"]), st["channel"], start)
    s.mute = bool(st["mute"])
    s.show_waveform = True
    if bpy.data.filepath:
        s.sound.filepath = bpy.path.relpath(os.path.join(SRC, st["file"]))
    if not s.sound.packed_file:
        s.sound.pack()
    se.channels[st["channel"]].name = st["name"].split(" (")[0]
    added.append(st["name"])
result = {"added": added,
          "strips": [(s.name, s.channel, int(s.frame_final_start), int(s.frame_final_end), s.mute, s.volume, s.pan,
                      s.sound.filepath, bool(s.sound.packed_file)) for s in se.strips_all]}
