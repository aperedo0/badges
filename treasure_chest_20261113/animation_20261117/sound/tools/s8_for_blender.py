"""The eighth try's sounds (the current ones), cut into pieces that fit a Blender file's own timeline (2026-11-23).
The owner: "add the sounds we have been working with to Codex_Temple_Fire.blend, sounds only".

    python3 sound/tools/s8_for_blender.py        (from the animation folder; needs sound/s8/ from s8_lid_drawer.py)

The sounds are timed to the frames of the whole scene preview video (860 frames), which is put together from four
pieces (tools/v12_render.py). A Blender file's timeline is the story played straight through, without the wait:
    video frames   0 to  77   arrival: scene frame = video frame - 28
    video frames  78 to 123   the chest held at scene frame 49 while the dust clears (no sound)
    video frames 124 to 348   waiting: the chest held at 49, rattling three times (not on the scene's timeline)
    video frames 349 on       reveal and ending: scene frame = video frame - 299
Each piece below is cut from its stem on whole frames, with the same low cut and ceiling as the mix, so that the
pieces laid back on the video's frames add up to sound/s8/mix.wav (checked at the end). Written to sound/blend/
(24 bit, so nothing is rounded twice) with strips.json, which tools/add_sound_to_blend.py reads inside Blender.
"""
import json, math, os, wave
import numpy as np
from scipy.signal import butter, sosfilt

SR, FPS = 48000, 30
HERE = os.path.dirname(os.path.abspath(__file__))
S8 = os.path.normpath(os.path.join(HERE, "..", "s8"))
OUT = os.path.normpath(os.path.join(HERE, "..", "blend"))
os.makedirs(OUT, exist_ok=True)
CEIL = 10.0 ** (-0.5 / 20.0)


def read(path):
    with wave.open(path, "rb") as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (2, 2, SR), path
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(float) / 32767.0


def write24(path, x):
    q = np.clip(np.round(x * 8388607.0), -8388607, 8388607).astype("<i4")
    b = q.reshape(-1).astype("<i4").tobytes()
    raw = np.frombuffer(b, "u1").reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(raw)


def ceiling(x):
    x = x.copy()
    big = np.abs(x) > CEIL
    x[big] = np.sign(x[big]) * (CEIL + (1 - CEIL) * np.tanh((np.abs(x[big]) - CEIL) / (1 - CEIL)))
    return x


# stem, file, name in Blender, video frames [a, b), scene frame of a (None: not on the scene's timeline), channel
PIECES = [("drops", "chest_lands.wav", "Chest lands (three drops)", 44, 70, 44 - 28, 1),
          ("lock", "lock.wav", "Lock (on the keyhole flash)", None, None, None, 2),
          ("lid", "lid_drawer.wav", "Lid opens (drawer)", None, None, None, 3),
          ("fire", "fire.wav", "Fire (fades in over half a second)", 425, 860, 425 - 299, 4),
          ("rattles", "waiting_rattles.wav", "Waiting rattles (footsteps)", 124, 349, None, 5)]
sos = butter(2, 70, btype="highpass", fs=SR, output="sos")
mix = read(os.path.join(S8, "mix.wav"))
back = np.zeros_like(mix)
strips = []
for stem, fname, label, a, b, scene, ch in PIECES:
    x = ceiling(sosfilt(sos, read(os.path.join(S8, f"stem_{stem}.wav")), axis=0))
    loud = np.nonzero(np.abs(x).max(1) > 12 / 32767.0)[0]
    first, last = loud[0] / SR * FPS, loud[-1] / SR * FPS
    if a is None:                                          # whole frames around the sound, a frame of room each side
        a, b = int(math.floor(first)) - 1, int(math.ceil(last)) + 2
        scene = a - 299
    assert a <= first and last <= b, (stem, a, first, last, b)
    i, j = int(round(a / FPS * SR)), int(round(b / FPS * SR))
    clip = x[i:j]
    write24(os.path.join(OUT, fname), clip)
    back[i:j] += clip
    strips.append(dict(name=label, file=fname, channel=ch, video_frame=a, frames=b - a, scene_frame=scene,
                       mute=scene is None, sounds_from_video_frame=round(first, 2), to=round(last, 2)))
    print(f"{label:38s} video {a:4d} to {b:4d}  scene {str(scene):>5s}  sound {first:7.2f} to {last:7.2f}  {os.path.getsize(os.path.join(OUT, fname)) / 1e6:5.2f} MB")
json.dump({"note": "pieces of the eighth try's sound for a Blender timeline; scene_frame null = the wait, which is not on the scene's "
                   "timeline (kept in the file, muted, starting after the frame the chest is held on)",
           "fps": FPS, "hold_frame": 49, "strips": strips}, open(os.path.join(OUT, "strips.json"), "w"), indent=1)
d = back - mix
print("pieces laid back on the video's frames against mix.wav: largest difference %.1f sixteen bit steps, average %.1f dB"
      % (np.abs(d).max() * 32767, 10 * math.log10(np.mean(d ** 2) + 1e-20)))
left = np.abs(mix).max(1) > 12 / 32767.0
left[np.abs(back).max(1) > 0] = False
print("samples of the mix louder than its noise floor that no piece covers:", int(left.sum()))
