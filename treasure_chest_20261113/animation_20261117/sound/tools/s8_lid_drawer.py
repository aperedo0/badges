"""Sound, eighth try (2026-11-22): the seventh try (s7_use_downloads_dry.py, the owner's recordings with no echo) plus
the owner's drawer recording on the lid opening. The owner asked for a sound when the chest opens, then: "I
downloaded a drawer opening effect. try that". On the sixth try the owner said:
- fire: "I actually don't want every single fire to turn on. Just when the fire turns on, just turn on the sound ...
  turn it on over the course of like half a second";
- "each drop has like a luggage drop sound, but you're gonna adjust it because one's gonna be louder than the other";
- "With the door lock, it's just a door lock. That's it, just boop, when it happens";
- footsteps on a wood floor for the rattles: "each rattle, when it's supposed to be like wood on wood or metal on
  metal or whatever, like it has one of those";
- "any other noise that I didn't mention, just remove it" (no sand, no latch, nothing made);
- "you can't adjust the files that I downloaded. Keep them pristine".

    python3 sound/tools/s8_lid_drawer.py         (from the animation folder; needs ffmpeg)

The recordings are read from copies in sound/sources/ (copied byte for byte from Downloads; checksums in
sound/sources/checksums.txt). Nothing is ever written to them: they are only decoded, and every change (trim, fade,
level, pitch, filter, echo) happens to the decoded numbers in memory.
"""
import json, math, os, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt, find_peaks, resample

SR, FPS = 48000, 30
FRAMES = 860
N = int(round(FRAMES / FPS * SR))
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "sources"))
OUT = os.path.normpath(os.path.join(HERE, "..", "s8"))
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261130)
FILES = dict(fire="u_d3475dm30o-fire-sound-222359.mp3", drop="freesound_community-luggage-drop-1-47660.mp3",
             lock="freesound_community-door-lock-43124.mp3", steps="freesound_community-footsteps-on-wood-floor-14735.mp3",
             drawer="freesound_community-drawer-41055.mp3")
CUES = []


def db(x):
    return 10.0 ** (x / 20.0)


def flt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x, axis=0)


def load(key, start=0.0, dur=None):
    """Decode a copy of the owner's recording to 48 kHz stereo numbers (read only)."""
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.4f}"] + (["-t", f"{dur:.4f}"] if dur else []) + \
          ["-i", os.path.join(SRC, FILES[key]), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, "<f4").reshape(-1, 2).astype(float)


def onset(x, frac):
    m = np.abs(x).max(1)
    return int(np.nonzero(m > frac * m.max())[0][0])


def fade(x, fin=0.002, out_start=None, out_end=None):
    x = x.copy()
    k = max(int(fin * SR), 1)
    x[:k] *= np.linspace(0, 1, k)[:, None]
    if out_end is not None:
        a, b = int(out_start * SR), min(int(out_end * SR), len(x))
        x[a:b] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, b - a)))[:, None]
        x = x[:b]
    return x


def pitch(x, semitones):
    """Higher and shorter (a smaller, lighter thing) or lower and longer, as when a recording is played faster or slower."""
    if abs(semitones) < 1e-6:
        return x
    return resample(x, int(round(len(x) / 2 ** (semitones / 12.0))), axis=0)


def place(y, x, at):
    i = int(round(at * SR))
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(y) - i)
    if n > 0:
        y[i:i + n] += x[:n]


def rms_db(x, a, b):
    seg = x[int(a * SR):int(b * SR)]
    return 10 * math.log10(np.mean(seg ** 2) + 1e-20)


def loud(x, a, b, win=0.05):
    """How loud the loudest twentieth of a second between a and b is (closer to what the ear hears than the peak)."""
    e = (x[int(a * SR):int(b * SR)] ** 2).mean(1)
    k = int(win * SR)
    return 10 * math.log10(np.convolve(e, np.ones(k) / k, "valid").max() + 1e-20)


def peak1(x):
    return x / np.abs(x).max()


def cue(label, frame, level):
    CUES.append({"sound": label, "frame": round(frame, 2), "seconds": round(frame / FPS, 3), "level_db": round(level, 1)})


DROPS, LOCK, RATTLES, FIRE, LID = (np.zeros((N, 2)) for _ in range(5))

# ------------------------------------------------------------------ the luggage drop on each landing (measured in the scene)
drop = load("drop")
o = onset(drop, 0.25)
drop = peak1(drop[o - int(0.004 * SR):])                    # from just before the hit; the handling noise before it is left out
# frame, level, pitch (a hair apart so the three are not the same copy), how long it keeps sounding (cut before the next)
LAND = [(44.6, 0.0, 0.0, 0.16, "chest lands on its left corner"),
        (49.6, -4.0, -0.6, 0.30, "the right side comes down flat"),
        (60.1, -12.0, 0.5, 0.22, "it rocks back and the left side comes down")]
for fr, lv, st, keep, lab in LAND:
    d = fade(pitch(drop, st), 0.002, keep - 0.05, keep)
    if lv < -8:
        d = flt(d, "lowpass", 5000)                           # a softer hit has less crack in it
    place(DROPS, d * db(lv), fr / FPS - 0.004)
    cue(lab, fr, lv)

# ------------------------------------------------------------------ the door lock, once, its clack on the keyhole's flash
lock = load("lock")
o = onset(lock, 0.5)                                          # the clack (the key turning before it is kept)
lock = fade(peak1(lock[int(0.045 * SR):]), 0.005, 0.50, 0.58)
place(LOCK, lock, 355 / FPS - (o / SR - 0.045))
cue("door lock", 355, 0.0)

# ------------------------------------------------------------------ the drawer on the lid opening
# The lid starts to lift at frame 393 (13.1 s), moves fastest around 400 to 405 and is fully open at 410 (13.67 s). The
# drawer's slide starts 0.13 s into the recording, is strongest from 0.28 to 0.55 s and is gone by 0.70 s: its start
# goes on frame 393, so its strongest part falls while the lid moves fastest and it ends as the lid comes to rest.
drawer = load("drawer")
DRAWER_START = 0.13
drawer = fade(peak1(drawer[int(0.10 * SR):]), 0.01, 0.70, 0.80)
place(LID, drawer, 393 / FPS - (DRAWER_START - 0.10))
cue("lid opens (drawer)", 393, 0.0)

# ------------------------------------------------------------------ footsteps for the rattles
steps_all = load("steps")
m = np.abs(steps_all).max(1)
env = np.convolve(m, np.ones(96) / 96, "same")
pk, _ = find_peaks(env, height=0.12 * env.max(), distance=int(0.3 * SR))
STEPS = []
for p in pk:
    lo = max(p - int(0.03 * SR), 0)
    s0 = lo + int(np.nonzero(m[lo:p + 1] > 0.2 * m[p])[0][0])
    STEPS.append(peak1(steps_all[max(s0 - int(0.003 * SR), 0):s0 + int(0.3 * SR)]))
order = list(rng.permutation(len(STEPS)))
used = [0]


def next_step():
    s = STEPS[order[used[0] % len(order)]]
    used[0] += 1
    return s


STRONG, RATTLE = (2.0, 2.0, 3.0), 30


def ss(x, a, b):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def bump(k, a, b, amp):
    return amp * math.sin(math.pi * (k - a) / (b - a)) ** 2 if a <= k <= b else 0.0


def rattle(k, kind):
    """Copied from tools/v12_render.py (the motion the video shows)."""
    z = dict(lid=0.0, roll=0.0, yaw=0.0, hop=0.0, hasp=0.0, ring=0.0)
    if k >= RATTLE:
        return z
    w = 1.0 - ss(k, RATTLE - 8, RATTLE - 1)
    q = k * 24.0 / RATTLE
    if kind == 0:
        z["lid"] = bump(q, 0, 9, 0.45) + bump(q, 10, 20, 0.3)
        z["roll"] = 0.5 * math.sin(2 * math.pi * q / 10) * math.exp(-q / 8) * w
        z["hasp"] = 4.0 * math.sin(2 * math.pi * q / 7) * math.exp(-q / 7) * w
        z["ring"] = 5.0 * math.sin(2 * math.pi * q / 12) * math.exp(-q / 9) * w
    elif kind == 1:
        z["lid"] = bump(q, 0, 7, 0.75) + bump(q, 8, 15, 0.25) + bump(q, 16, 22, 0.08)
        z["hop"] = bump(q, 0, 8, 0.035)
        z["yaw"] = 0.35 * math.sin(2 * math.pi * q / 9) * math.exp(-q / 6) * w
        z["hasp"] = 6.0 * math.sin(2 * math.pi * q / 8) * math.exp(-q / 7) * w
        z["ring"] = 7.0 * math.sin(2 * math.pi * q / 12) * math.exp(-q / 9) * w
    else:
        z["roll"] = 0.35 * math.sin(2 * math.pi * q / 4) * math.exp(-q / 10) * w
        z["lid"] = 0.2 * abs(math.sin(2 * math.pi * q / 4)) * math.exp(-q / 9) * w
        z["hasp"] = 3.0 * math.sin(2 * math.pi * q / 4) * math.exp(-q / 8) * w
        z["ring"] = 3.0 * math.sin(2 * math.pi * q / 10) * math.exp(-q / 9) * w
    return {key: v * STRONG[kind] for key, v in z.items()}


def contacts(kind):
    """Moments of contact in one rattle, with the speed at contact: (frame within the rattle, part, speed)."""
    step = 1.0 / 32
    ks = np.arange(0, RATTLE + 1, step)
    curves = {p: np.array([rattle(k, kind)[p] for k in ks]) for p in ("lid", "roll", "yaw", "hop", "hasp", "ring")}
    found = []
    for part in ("lid", "hop"):
        c = curves[part]
        up = c > 1e-6
        for i in range(1, len(c)):
            if up[i - 1] and not up[i]:
                found.append((ks[i], part, abs(c[i - 1] - c[max(i - 3, 0)]) / (2 * step)))
    for part, both in (("roll", True), ("hasp", False), ("ring", False)):
        c = curves[part]
        for i in range(1, len(c)):
            if (c[i - 1] > 0 >= c[i]) or (both and c[i - 1] < 0 <= c[i]):
                if abs(c[i - 1]) + abs(c[i]) > 1e-6:
                    found.append((ks[i], part + ("_left" if c[i - 1] > 0 else "_right"), abs(c[i] - c[i - 1]) / step))
    return sorted(found)


ALL = {kind: contacts(kind) for kind in (0, 1, 2)}
REF = {}
for kind, cs in ALL.items():
    for k, part, v in cs:
        REF[part.split("_")[0]] = max(REF.get(part.split("_")[0], 0), v)
BASE = dict(lid=-12, hop=-12, roll=-17, hasp=-19, ring=-25)
KIND_DB = {0: 14.0, 1: 3.0, 2: -4.0}
WOOD = ("lid", "roll", "hop")
# wood on wood: the footstep as it is, a little lower for the heavy jolt; the shiver's taps are short and light
WOOD_PITCH = dict(hop=-2.0, roll=-1.0, lid=0.0)
# metal on metal (the gold latch, the side rings): a footstep made small, higher and shorter, only its click left
METAL = dict(hasp=(7.0, 1500.0), ring=(5.0, 1100.0))
RATTLE_AT = (124, 199, 274)
for start, kind in zip(RATTLE_AT, (0, 1, 2)):
    evs = []
    for k, part, v in ALL[kind]:
        b = part.split("_")[0]
        lv = BASE[b] + KIND_DB[kind] + (0.0 if b == "hop" else max(-30.0, 20 * math.log10(max(v, 1e-6) / REF[b])))
        if evs and k - evs[-1]["k"] < 0.15:
            evs[-1]["parts"].append((b, lv))
        else:
            evs.append(dict(k=k, parts=[(b, lv)]))
    top = max(lv for e in evs for _, lv in e["parts"])
    for e in evs:
        wood = [(b, lv) for b, lv in e["parts"] if b in WOOD]
        metal = [(b, lv) for b, lv in e["parts"] if b in METAL]
        at = (start + e["k"]) / FPS
        if wood:
            b, lv = max(wood, key=lambda p: p[1])
            if lv >= top - 20:
                st = WOOD_PITCH[b] + (2.0 if kind == 2 else 0.0)
                keep = 0.085 if kind == 2 else 0.24
                s = fade(pitch(next_step(), st), 0.002, keep - 0.03, keep)
                place(RATTLES, s * db(lv), at - 0.003)
                cue(f"rattle {kind + 1}: footstep ({b})", start + e["k"], lv)
        for b, lv in metal:
            if lv >= top - 20 and (not wood or lv >= max(w[1] for w in wood) - 8):
                st, hp = METAL[b]
                s = fade(flt(pitch(next_step(), st), "highpass", hp), 0.001, 0.045, 0.07)
                place(RATTLES, peak1(s) * db(lv - 3), at - 0.002)
                cue(f"rattle {kind + 1}: small footstep click ({b})", start + e["k"], lv - 3)

# ------------------------------------------------------------------ the fire: one sound, faded in over half a second as the first torches light
FIRE_FROM = 9.5                                               # seconds into the owner's recording
t0 = 425 / FPS                                                # the first pair starts to catch (their light is full at 439)
f = load("fire", FIRE_FROM, N / SR - t0 + 0.05)
f = flt(f, "highpass", 80, 4)                                 # its deep rumble (half its energy is below 64 Hz) is left out
ramp = np.clip(np.arange(len(f)) / (0.5 * SR), 0, 1)
f *= (ramp * ramp * (3 - 2 * ramp))[:, None]
place(FIRE, f, t0)
cue("fire comes on (over half a second)", 425, 0.0)

# ------------------------------------------------------------------ levels, all against the first landing
land = loud(DROPS, 44.6 / FPS - 0.01, 44.6 / FPS + 0.12)
LOCK *= db(land - 7.0 - loud(LOCK, 355 / FPS - 0.25, 355 / FPS + 0.3))
for start in RATTLE_AT:                                       # each rattle's strongest knock about as loud as the others'
    a, b = int(start / FPS * SR), int((start / FPS + 1.0) * SR)
    RATTLES[a:b] *= db(land - 8.0 - loud(RATTLES, start / FPS, start / FPS + 1.0))
LID *= db(land - 9.0 - loud(LID, 393 / FPS - 0.1, 410 / FPS + 0.1))
FIRE *= db(rms_db(DROPS, 44.6 / FPS - 0.01, 44.6 / FPS + 0.15) - 17.0 - rms_db(FIRE, 16.0, 28.0))


# ------------------------------------------------------------------ mix, dry (no hall echo: the owner's call)
L, R = np.zeros(N), np.zeros(N)
stems = {}
for name, st in (("drops", DROPS), ("lock", LOCK), ("rattles", RATTLES), ("lid", LID), ("fire", FIRE)):
    stems[name] = (st[:, 0].copy(), st[:, 1].copy())
    L += st[:, 0]
    R += st[:, 1]
L, R = flt(L, "highpass", 70), flt(R, "highpass", 70)
a, b = int((44.6 / FPS - 0.01) * SR), int((44.6 / FPS + 0.15) * SR)
g = db(-1.0) / max(np.abs(L[a:b]).max(), np.abs(R[a:b]).max())   # the first landing's peak sits at 1 dB below full
L, R = L * g, R * g
CEIL = db(-0.5)
over = int((np.abs(L) > CEIL).sum() + (np.abs(R) > CEIL).sum())
for ch in (L, R):                                             # the rare sharper click (a crackle, a heel) is rounded off, not clipped
    big = np.abs(ch) > CEIL
    ch[big] = np.sign(ch[big]) * (CEIL + (1 - CEIL) * np.tanh((np.abs(ch[big]) - CEIL) / (1 - CEIL)))


def write(path, l, r):
    x = np.stack([l, r], 1)
    x = np.clip(x + (rng.uniform(-0.5, 0.5, x.shape) + rng.uniform(-0.5, 0.5, x.shape)) / 32768, -1, 1)
    with wave.open(path, "wb") as w_:
        w_.setnchannels(2)
        w_.setsampwidth(2)
        w_.setframerate(SR)
        w_.writeframes((x * 32767).astype("<i2").tobytes())


write(os.path.join(OUT, "mix.wav"), L, R)
for name, (l, r) in stems.items():
    write(os.path.join(OUT, f"stem_{name}.wav"), l * g, r * g)
json.dump({"note": "frames of Chest reveal whole scene preview.mp4 at 30 a second; sounds are the owner's recordings",
           "sources": FILES, "fire_from_seconds": FIRE_FROM, "footsteps_found": len(STEPS),
           "cues": sorted(CUES, key=lambda c: c["frame"])}, open(os.path.join(OUT, "cues.json"), "w"), indent=1)
mono = 0.5 * (L + R)
for name, a_, b_ in (("first drop (1.45 to 1.6 s)", 1.45, 1.6), ("second drop (1.64 to 1.8 s)", 1.64, 1.8), ("third drop (1.99 to 2.15 s)", 1.99, 2.15),
                     ("rattle 1 (4.1 to 5.1 s)", 4.1, 5.1), ("rattle 2 (6.6 to 7.6 s)", 6.6, 7.6), ("rattle 3 (9.1 to 10.1 s)", 9.1, 10.1),
                     ("lock (11.6 to 12.2 s)", 11.6, 12.2), ("lid opening (13.0 to 13.8 s)", 13.0, 13.8), ("fire fading in (14.17 to 14.67 s)", 14.17, 14.67), ("fire (16 to 28 s)", 16.0, 28.0)):
    seg = mono[int(a_ * SR):int(b_ * SR)]
    print(f"{name:36s} loudness {20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12):6.1f} dB   peak {20 * np.log10(np.abs(seg).max() + 1e-12):6.1f} dB")
print("footsteps found", len(STEPS), "used", used[0], "cues", len(CUES), "samples rounded off", over)
