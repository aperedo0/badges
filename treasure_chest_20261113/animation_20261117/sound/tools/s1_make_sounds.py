"""Sound, first try (2026-11-21). Every sound is made from scratch in code: no recordings, no downloads.
The owner wants to hear how good made sounds can get before deciding between working on them over time and
downloading recordings ("I'll hear what you got and then we'll take it from there").

    python3 sound/tools/s1_make_sounds.py        (from the animation folder; about a minute)

Writes sound/s1/mix.wav (the whole preview's sound, 28.67 s, 48 kHz stereo), one file per group of sounds
(stems), and sound/s1/cues.json (when each sound plays). It does not touch the scene or any video; laying the
sound under the last exported preview is a separate ffmpeg step that copies the picture as it is.

Timing: frame numbers are frames of `Chest reveal whole scene preview.mp4` (30 a second): arrival 0 to 123,
waiting 124 to 348 (rattles at 124, 199, 274), reveal 349 to 589, ending 590 to 859. Measured on that video:
the chest's first corner hits the floor at 45, the other side comes down at 49, it rocks and settles at 60;
the lock clicks at 355, the clasp lands at 373, the lid opens from 389 to 416. The rest comes from the scene's
own keys (tools/v12_story.py): torch pairs catch at 425, 440, 455, 470, 485, 500; the gold light rises from 421
to 537; the cold burst from the chest peaks at 413.

How the sounds are made:
- wood and metal knocks, clicks and rings: modal synthesis (a few decaying tones at the frequencies a real piece
  of wood or iron rings at) plus a short burst of filtered noise for the impact itself;
- the lid's creak: stick and slip, a train of tiny jolts at an uneven rate driving the resonances of wood and
  a hinge;
- air, smoke, sand, fire: filtered noise, shaped in time (sand and crackle from thousands of tiny ticks);
- the hall: every sound is sent into a made stone hall reverb (about 3 seconds long).
"""
import json, os, wave
import numpy as np
from scipy.signal import butter, sosfilt, lfilter, iirpeak, fftconvolve

SR, FPS = 48000, 30
FRAMES = 860
N = int(round(FRAMES / FPS * SR))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "s1"))
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261121)
CUES = []


def db(x):
    return 10.0 ** (x / 20.0)


def secs(s):
    return np.arange(int(s * SR)) / SR


def flt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def noise(s):
    return rng.standard_normal(int(s * SR))


def norm(y):
    m = np.abs(y).max()
    return y / m if m > 0 else y


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def keys_env(keys, frames=FRAMES):
    """A curve through (frame, value) keys, eased between keys, one value per sample."""
    f = np.arange(N) / SR * FPS
    out = np.full(N, float(keys[0][1]))
    for (f0, v0), (f1, v1) in zip(keys[:-1], keys[1:]):
        m = (f >= f0) & (f <= f1)
        out[m] = v0 + (v1 - v0) * smooth(f[m], f0, f1)
    out[f > keys[-1][0]] = keys[-1][1]
    return out


class Bus:
    """A group of sounds: dry stereo plus what it sends into the hall."""
    def __init__(self, name):
        self.name, self.L, self.R, self.send = name, np.zeros(N), np.zeros(N), np.zeros(N)

    def add(self, sig, frame, gain=1.0, pan=0.0, wet=0.3, right=None, label=None):
        i = int(round(frame / FPS * SR))
        if i >= N:
            return
        sl, sr = sig, (sig if right is None else right)
        n = min(len(sl), N - i)
        a = (pan + 1.0) * np.pi / 4.0
        gl, gr = np.cos(a), np.sin(a)
        if right is not None:
            gl = gr = 0.7071
        self.L[i:i + n] += sl[:n] * gain * gl
        self.R[i:i + n] += sr[:n] * gain * gr
        self.send[i:i + n] += 0.5 * (sl[:n] + sr[:n]) * gain * wet
        if label:
            CUES.append({"sound": label, "frame": round(frame, 2), "seconds": round(frame / FPS, 3)})


# ------------------------------------------------------------------ building blocks
def modal(freqs, decays, amps, s=None, jitter=0.02):
    s = s or max(decays) * 6
    t = secs(s)
    y = np.zeros_like(t)
    for f, d, a in zip(freqs, decays, amps):
        f *= 1 + rng.uniform(-jitter, jitter)
        y += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t / d)
    return y * np.minimum(1.0, t / 0.0008)


def burst(s, kind, f, decay, order=2):
    t = secs(s)
    return norm(flt(noise(s), kind, f, order) * np.exp(-t / decay))


def wood_knock(pitch=1.0, bright=1.0):
    f = np.array([118, 196, 287, 405, 560, 790, 1120, 1580]) * pitch
    d = np.array([0.20, 0.15, 0.11, 0.085, 0.065, 0.05, 0.035, 0.025])
    a = np.array([1, .85, .65, .5, .38, .28 * bright, .18 * bright, .1 * bright])
    y = modal(f, d, a, s=0.9)
    b = burst(0.06, "bandpass", [300 * pitch, 3500], 0.012)
    y[:len(b)] += 0.55 * bright * b
    return norm(y)


def metal_tick(pitch=1.0, decay=1.0, hum=0.0):
    f = np.array([1620, 2390, 3480, 4720, 6150, 7900]) * pitch
    d = np.array([0.16, 0.12, 0.09, 0.065, 0.045, 0.03]) * decay
    a = np.array([1, .8, .6, .45, .3, .2])
    y = modal(f, d, a, s=0.9)
    if hum:
        y += hum * modal([980 * pitch], [0.45 * decay], [1.0], s=0.9)
    b = burst(0.01, "highpass", 2500, 0.002)
    y[:len(b)] += 0.4 * b
    return norm(y)


def place(y, x, at):
    i = int(at * SR)
    if i < len(y):
        n = min(len(x), len(y) - i)
        y[i:i + n] += x[:n]


def heavy_thud(scale=1.0, s=1.4):
    t = secs(s)
    f = 36 + 44 * np.exp(-t / 0.035)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.26 * (0.6 + 0.4 * scale))) * np.minimum(1, t / 0.002)
    body = norm(flt(noise(s), "lowpass", 260) * np.exp(-t / 0.07))
    y = sub + 0.6 * body
    place(y, 0.75 * wood_knock(0.78, 0.9), 0.0)
    place(y, 0.22 * burst(0.05, "highpass", 1800, 0.008), 0.0)
    for _ in range(int(5 * scale) + 2):                # iron bands and studs rattling just after
        dt = rng.uniform(0.004, 0.24)
        place(y, metal_tick(rng.uniform(0.85, 1.2), 0.7) * rng.uniform(0.07, 0.22) * np.exp(-dt / 0.12), dt)
    return norm(y)


def lowpass_sweep(x, cut, cuts=(250, 600, 1400, 3200, 7000)):
    """x through a low pass whose cut off follows `cut` (Hz, one per sample): crossfades between fixed filters."""
    banks = [flt(x, "lowpass", c) for c in cuts]
    lc = np.log(np.clip(cut, cuts[0], cuts[-1]))
    lk = np.log(np.array(cuts, dtype=float))
    out = np.zeros_like(x)
    for k in range(len(cuts) - 1):
        m = (lc >= lk[k]) & (lc <= lk[k + 1])
        w = (lc[m] - lk[k]) / (lk[k + 1] - lk[k])
        out[m] = banks[k][m] * (1 - w) + banks[k + 1][m] * w
    return out


# ------------------------------------------------------------------ the buses
ROOM, DROP, SAND, RATTLE, MAGIC, LOCK, LID, AIR, FIRE, PAD = (Bus(n) for n in (
    "room", "drop", "sand", "rattle", "magic", "lock", "lid", "air", "fire", "pad"))

# --- the hall's own sound, all the way through: a deep stone rumble and a faint moving draft
t = np.arange(N) / SR
brown = np.cumsum(noise(N / SR))
brown = flt(brown - brown.mean(), "highpass", 18)
rum = norm(flt(brown, "lowpass", 140))
lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.071 * t + 1.3) * np.sin(2 * np.pi * 0.113 * t + 0.4)
draftL = norm(flt(noise(N / SR), "bandpass", [250, 1400])) * lfo
draftR = norm(flt(noise(N / SR), "bandpass", [250, 1400])) * (1.5 - lfo)
ROOM.add(rum * db(-26), 0, right=norm(flt(np.cumsum(noise(N / SR)), "lowpass", 140)) * db(-26), wet=0.0)
ROOM.add(draftL * db(-37), 0, right=draftR * db(-37), wet=0.15)

# --- arrival: the chest falls in, lands on one corner, comes down on the other, rocks and settles
s = 0.45
w = noise(s)
u = secs(s) / s
wh = lowpass_sweep(flt(w, "highpass", 200), 300 + 2200 * u ** 2) * u ** 2.2
DROP.add(norm(wh) * db(-24), 45 - s * FPS, wet=0.35, label="air rushing past the falling chest")
DROP.add(heavy_thud(1.0) * db(-7), 45, wet=0.45, label="chest lands, first corner")
DROP.add(heavy_thud(0.5) * db(-12), 49, pan=0.15, wet=0.45, label="the other side comes down")
DROP.add(wood_knock(0.85, 0.7) * db(-17), 60, pan=-0.1, wet=0.4, label="it rocks and settles")
DROP.add(wood_knock(0.9, 0.5) * db(-28), 62.5, wet=0.4)
for k, (fr, g) in enumerate([(46.5, -14), (49.5, -17), (52.5, -20), (56, -22), (60.5, -23), (65, -27), (71, -30), (79, -34), (89, -38)]):
    for side in (-1, 1):                               # the two side rings swinging against the iron
        DROP.add(metal_tick(1.32 * rng.uniform(0.97, 1.03), 1.0, hum=0.35) * db(g + rng.uniform(-2, 1)), fr + rng.uniform(0, 1.2),
                 pan=0.5 * side, wet=0.35, label="side rings swing and knock" if k == 0 and side < 0 else None)

# --- sand shaken loose from the vault, in the two streaks of light: a high faint release, then it lands
for side, pan in ((-1, -0.55), (1, 0.55)):
    rel = norm(flt(noise(0.9), "bandpass", [2500, 8000])) * np.minimum(1, secs(0.9) / 0.05) * np.exp(-secs(0.9) / 0.3)
    SAND.add(rel * db(-44), 45 + 0.05 * FPS, pan=pan * 0.8, wet=0.8, label="sand lets go high up" if side < 0 else None)
    s = 1.3
    y = np.zeros(int(s * SR))
    tt = secs(s)
    rate = 520 * np.exp(-((tt - 0.45) / 0.22) ** 2)     # ticks per second, peaking as most of it lands
    cnt = rng.poisson(rate / SR)
    for i in np.nonzero(cnt)[0]:
        tick = flt(rng.standard_normal(70), "highpass", 3000) * np.exp(-np.arange(70) / 14.0)
        y[i:i + 70] += tick[:len(y) - i] * rng.lognormal(0, 0.6)
    y += 0.25 * norm(flt(noise(s), "bandpass", [3000, 9000])) * np.exp(-((tt - 0.45) / 0.3) ** 2)
    SAND.add(norm(y) * db(-36), 45 + 1.3 * FPS, pan=pan, wet=0.55, label="sand lands on the stone" if side < 0 else None)

# --- the waiting rattles (the same shapes as tools/v12_render.py's rattle(), 30 frames each, 2, 2 and 3 times strong)
RAT = 30.0


def lid_angle(k, kind):
    def bump(q, a, b, amp):
        return amp * np.sin(np.pi * (q - a) / (b - a)) ** 2 if a <= q <= b else 0.0
    q = k * 24.0 / RAT
    if kind == 0:
        return 2 * (bump(q, 0, 9, 0.45) + bump(q, 10, 20, 0.3))
    if kind == 1:
        return 2 * (bump(q, 0, 7, 0.75) + bump(q, 8, 15, 0.25) + bump(q, 16, 22, 0.08))
    w_ = 1.0 - (lambda x: x * x * (3 - 2 * x))(min(max((k - (RAT - 8)) / 7.0, 0), 1))
    return 3 * 0.2 * abs(np.sin(2 * np.pi * q / 4)) * np.exp(-q / 9) * w_


def q2k(q):
    return q * RAT / 24.0


for start, kind in ((124, 0), (199, 1), (274, 2)):
    lab = ("rattle: two knocks", "rattle: one hard jolt", "rattle: a shiver")[kind]
    if kind == 0:
        RATTLE.add(wood_knock(1.45, 0.9) * db(-15), start + q2k(9), wet=0.3, label=lab)       # the lid drops back
        RATTLE.add(wood_knock(1.5, 0.8) * db(-19), start + q2k(20), wet=0.3)
        for q, g in ((1, -24), (5, -27), (9.5, -26), (14, -31), (20.5, -30)):
            RATTLE.add(metal_tick(2.0, 0.5) * db(g), start + q2k(q), pan=0.05, wet=0.25)      # the hasp
        for q, g in ((2, -28), (8, -31), (15, -35)):
            for sd in (-1, 1):
                RATTLE.add(metal_tick(1.32, 1.0, 0.35) * db(g + rng.uniform(-2, 1)), start + q2k(q) + rng.uniform(0, 1), pan=0.5 * sd, wet=0.3)
    elif kind == 1:
        RATTLE.add(heavy_thud(0.35) * db(-11), start + q2k(8), wet=0.4, label=lab)           # the whole chest hops and lands
        RATTLE.add(wood_knock(1.45, 1.0) * db(-14), start + q2k(7), wet=0.3)
        RATTLE.add(wood_knock(1.5, 0.8) * db(-21), start + q2k(15), wet=0.3)
        RATTLE.add(wood_knock(1.55, 0.6) * db(-29), start + q2k(22), wet=0.3)
        for q, g in ((1, -22), (5, -24), (9, -23), (13, -28), (17, -31), (21, -34)):
            RATTLE.add(metal_tick(2.0, 0.5) * db(g), start + q2k(q), pan=0.05, wet=0.25)
        for q, g in ((3, -25), (9, -25), (15, -29), (22, -34)):
            for sd in (-1, 1):
                RATTLE.add(metal_tick(1.32, 1.0, 0.35) * db(g + rng.uniform(-2, 1)), start + q2k(q) + rng.uniform(0, 1), pan=0.5 * sd, wet=0.3)
    else:
        for j in range(12):                              # quick chatter: the lid taps at every half shake
            q = 1 + 2 * j
            g = -14 - 1.5 * j
            RATTLE.add(wood_knock(1.6 + rng.uniform(-0.05, 0.05), 0.7) * db(g - 3), start + q2k(q), wet=0.3, label=lab if j == 0 else None)
            RATTLE.add(metal_tick(2.05, 0.4) * db(g - 9), start + q2k(q) + 0.4, pan=0.05, wet=0.25)
        for q, g in ((2, -27), (7, -30), (12, -33), (18, -36)):
            for sd in (-1, 1):
                RATTLE.add(metal_tick(1.32, 1.0, 0.35) * db(g), start + q2k(q) + rng.uniform(0, 1), pan=0.5 * sd, wet=0.3)

# --- the glow behind the keyhole: a faint airy tone that breathes with it and flares when the lock clicks
key = np.zeros(N)
fr = np.arange(N) / SR * FPS
key += np.where(fr < 124, keys_env([(62, 0.0), (77, 0.5), (123, 0.5)]), 0)
for i0 in range(124, 349):
    pass
wait = (fr >= 124) & (fr < 349)
kk = fr[wait] - 124
lid = np.array([lid_angle(x % 75, int(x // 75) % 3) if (x % 75) < RAT else 0.0 for x in kk])
key[wait] = 0.5 + 0.13 * np.sin(2 * np.pi * (kk % 75) / 75) + 0.9 * lid
rev = fr >= 349
key[rev] = keys_env([(349, 0.5), (354, 1.5), (355, 3.0), (358, 0.5), (365, 0.15), (387, 0.15), (391, 0.0)])[rev]
lvl = np.clip(key, 0, 3) / 3.0
amp = db(-58) * (lvl / (1 / 6)) ** 0.9                    # 0.5 of 3 -> -58 dB, the flash -> about -42 dB
vib = 1 + 0.003 * np.sin(2 * np.pi * 4.3 * t)
tone = sum(a * np.sin(2 * np.pi * f * np.cumsum(vib) / SR + rng.uniform(0, 6.28)) for f, a in ((880, 1.0), (1318.5, 0.6), (1760, 0.35), (2637, 0.15)))
air = norm(flt(noise(N / SR), "bandpass", [3000, 9000]))
MAGIC.add(norm(tone) * amp + air * amp * 0.5, 0, wet=0.7, label="keyhole glow breathes")

# --- the reveal: bolt, click, clasp
s = 0.18
sc = norm(flt(noise(s), "bandpass", [1800, 5200])) * (0.6 + 0.4 * np.abs(flt(noise(s), "lowpass", 90)) / 1.5) * np.sin(np.pi * secs(s) / s) ** 0.5
LOCK.add(sc * db(-24), 349, wet=0.3, label="bolt slides")
LOCK.add(metal_tick(2.2, 0.35) * db(-26), 349 + s * FPS, wet=0.3)
click = modal([2650, 3980, 5520, 7300, 210, 430], [0.09, 0.06, 0.045, 0.03, 0.05, 0.04], [1, .8, .55, .35, .6, .4], s=0.6)
place(click, 0.8 * burst(0.004, "highpass", 3000, 0.0008), 0)
LOCK.add(norm(click) * db(-9), 355, wet=0.35, label="lock clicks open")
s = 0.14
sq = np.sin(2 * np.pi * np.cumsum(1500 + 600 * secs(s) / s) / SR) * (1 + 0.5 * flt(noise(s), "lowpass", 60)) * np.sin(np.pi * secs(s) / s)
LOCK.add(norm(sq) * db(-30), 365, wet=0.3, label="clasp lifts")
LOCK.add(metal_tick(0.78, 1.3) * db(-14), 373, wet=0.4, label="clasp falls back")
LOCK.add(wood_knock(1.4, 0.6) * db(-24), 373, wet=0.3)

# --- the lid creaks open (389 to 416) and stops
T = (416 - 389) / FPS
nT = int(T * SR)
imp = np.zeros(nT)
tc, k = 0.0, 0
while tc < T:
    u = tc / T
    rate = (38 + 55 * np.sin(np.pi * min(u * 1.15, 1.0)) ** 0.7) * rng.uniform(0.75, 1.25)
    i = int(tc * SR)
    imp[i] += (0.45 + 0.55 * np.sin(np.pi * u) ** 0.6) * rng.uniform(0.55, 1.0) * (1 if rng.random() > 0.08 else 2.2)
    tc += 1.0 / rate
cr = np.zeros(nT)
for f, q, g in ((430, 9, 1.0), (760, 12, 0.8), (1180, 16, 0.65), (1730, 18, 0.45), (2480, 20, 0.3)):
    b, a = iirpeak(f, q, fs=SR)
    cr += g * lfilter(b, a, imp)
b, a = iirpeak(1260, 70, fs=SR)                          # the hinge's narrow squeal
cr += 0.5 * lfilter(b, a, imp)
cr += 0.25 * norm(flt(noise(T), "bandpass", [90, 260])) * np.sin(np.pi * np.arange(nT) / nT)   # low groan of the wood
LID.add(norm(cr) * db(-13), 389, wet=0.4, label="lid creaks open")
LID.add(wood_knock(1.1, 0.8) * db(-15), 416, wet=0.45, label="lid stops, fully open")
LID.add(metal_tick(1.6, 0.6) * db(-27), 416.5, wet=0.3)

# --- the cold light bursting out, and the smoke rushing out of the chest
burst_env = keys_env([(387, 0.0), (413, 1.0), (433, 0.8), (483, 0.3), (527, 0.0)])
swell = lowpass_sweep(noise(N / SR), 350 + 3600 * burst_env ** 1.5) * burst_env
subs = np.sin(2 * np.pi * 44 * t) * burst_env ** 1.4
AIR.add(norm(swell) * db(-27) + subs * db(-24), 0, wet=0.6,
        right=norm(lowpass_sweep(noise(N / SR), 350 + 3600 * burst_env ** 1.5) * burst_env) * db(-27) + subs * db(-24), label="cold light bursts out")
CUES[-1].update(frame=387, seconds=round(387 / FPS, 3))
smoke_env = keys_env([(393, 0.0), (430, 1.0), (480, 0.8), (545, 0.0)])
turb = 0.75 + 0.25 * np.sin(2 * np.pi * 0.9 * t + 0.3) * np.sin(2 * np.pi * 1.37 * t)
sm_l = norm(flt(noise(N / SR), "bandpass", [150, 900])) * smoke_env * turb
sm_r = norm(flt(noise(N / SR), "bandpass", [150, 900])) * smoke_env * (1.5 - turb)
AIR.add(sm_l * db(-30), 0, right=sm_r * db(-30), wet=0.4, label="smoke rushes out and rises")
CUES[-1].update(frame=393, seconds=round(393 / FPS, 3))

# --- the torches catch, pair after pair, nearest first, and keep burning
for g in range(6):
    fr0 = 425 + 15 * g
    near = 0.72 ** g
    cut = 7000 * 0.78 ** g
    for side in (-1, 1):
        s = 0.7
        tt = secs(s)
        fw = lowpass_sweep(noise(s), 250 + 2600 * np.minimum(1, tt / 0.06)) * np.minimum(1, tt / 0.012) * np.exp(-tt / 0.32)
        th = np.sin(2 * np.pi * 85 * tt) * np.exp(-tt / 0.12) * np.minimum(1, tt / 0.004)
        sig = flt(norm(fw) + 0.6 * th, "lowpass", cut)
        FIRE.add(norm(sig) * db(-15) * near, fr0 + (1.5 if side > 0 else 0), pan=0.7 * side, wet=0.35 + 0.08 * g,
                 label=f"torch pair {g + 1} catches" if side < 0 else None)
        # its fire from then on: a low roar and crackles
        s = (FRAMES - fr0) / FPS
        tt = secs(s)
        grow = np.minimum(1, tt / 0.6)
        mod = 0.7 + 0.3 * np.sin(2 * np.pi * rng.uniform(0.2, 0.5) * tt + rng.uniform(0, 6)) * np.sin(2 * np.pi * rng.uniform(1.1, 2.1) * tt)
        roar = norm(flt(noise(s), "bandpass", [80, 420])) * mod * grow
        y = 0.5 * roar
        cnt = rng.poisson(np.full(len(tt), rng.uniform(4.0, 6.5)) / SR)
        for i in np.nonzero(cnt)[0]:
            L_ = int(rng.uniform(0.003, 0.014) * SR)
            pop = flt(rng.standard_normal(L_), "bandpass", [1200, 6000]) * np.exp(-np.arange(L_) / (L_ / 4))
            y[i:i + L_] += pop[:len(y) - i] * rng.lognormal(-0.3, 0.7) * grow[i]
        FIRE.add(flt(norm(y), "lowpass", cut) * db(-27) * near, fr0, pan=0.7 * side, wet=0.3 + 0.08 * g)

# --- the gold light rising: a low warm swell (an open chord of D) that stays under the ending
gold = keys_env([(421, 0.0), (475, 0.42), (537, 1.0)])
pad = np.zeros(N)
for f, a in ((73.42, 1.0), (110.0, 0.8), (146.83, 0.65), (220.0, 0.45), (329.63, 0.25)):
    for det in (-0.0018, 0.0018):
        ff = f * (1 + det)
        ph = 2 * np.pi * ff * t + rng.uniform(0, 6.28)
        pad += a * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
pad = flt(pad, "lowpass", 900) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.09 * t))
PAD.add(norm(pad) * gold * db(-26), 0, wet=0.5, label="warm swell as the gold light rises")
CUES[-1].update(frame=421, seconds=round(421 / FPS, 3))

# ------------------------------------------------------------------ the stone hall
def hall_ir(s=3.6):
    tt = secs(s)
    out = []
    for _ in range(2):
        nz = rng.standard_normal(len(tt))
        ir = (flt(nz, "lowpass", 500) * np.exp(-6.91 * tt / 3.1) + flt(nz, "bandpass", [500, 3000]) * np.exp(-6.91 * tt / 2.5)
              + flt(nz, "highpass", 3000) * np.exp(-6.91 * tt / 1.2))
        pre = int(0.022 * SR)
        ir = np.concatenate([np.zeros(pre), ir])[:len(tt)] * np.minimum(1, tt / 0.05)
        for d, gg in ((0.011, 0.55), (0.019, 0.45), (0.031, 0.38), (0.044, 0.3), (0.058, 0.25), (0.079, 0.2), (0.103, 0.15)):
            ir[int((d + rng.uniform(-0.002, 0.002)) * SR)] += gg * rng.choice([-1, 1]) * 3
        out.append(ir / np.sqrt((ir ** 2).sum()))
    return out


BUSES = (ROOM, DROP, SAND, RATTLE, MAGIC, LOCK, LID, AIR, FIRE, PAD)
send = sum(b.send for b in BUSES)
irL, irR = hall_ir()
wetL = fftconvolve(send, irL)[:N] * db(-4)
wetR = fftconvolve(send, irR)[:N] * db(-4)
L = sum(b.L for b in BUSES) + wetL
R = sum(b.R for b in BUSES) + wetR
L, R = flt(L, "highpass", 22), flt(R, "highpass", 22)
peak = max(np.abs(L).max(), np.abs(R).max())
g = db(-1.0) / peak
L, R = L * g, R * g


def write(path, l, r):
    x = np.stack([l, r], 1)
    x = np.clip(x + rng.uniform(-0.5, 0.5, x.shape) / 32768 + rng.uniform(-0.5, 0.5, x.shape) / 32768, -1, 1)
    with wave.open(path, "wb") as w_:
        w_.setnchannels(2)
        w_.setsampwidth(2)
        w_.setframerate(SR)
        w_.writeframes((x * 32767).astype("<i2").tobytes())


write(os.path.join(OUT, "mix.wav"), L, R)
for b in BUSES:
    write(os.path.join(OUT, f"stem_{b.name}.wav"), b.L * g, b.R * g)
json.dump({"note": "frames of Chest reveal whole scene preview.mp4 at 30 a second", "cues": sorted(CUES, key=lambda c: c["frame"])},
          open(os.path.join(OUT, "cues.json"), "w"), indent=1)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


m = 0.5 * (L + R)
for name, a_, b_ in (("empty temple (0 to 1.3 s)", 0, 1.3), ("chest lands (1.4 to 2.2 s)", 1.4, 2.2), ("waiting (4.2 to 11.6 s)", 4.2, 11.6),
                     ("lock and lid (11.6 to 14 s)", 11.6, 14.0), ("torches and gold (14 to 19.6 s)", 14.0, 19.6), ("ending (19.7 to 28.6 s)", 19.7, 28.6)):
    seg = m[int(a_ * SR):int(b_ * SR)]
    print(f"{name:34s} loudness {rms_db(seg):6.1f} dB   peak {20 * np.log10(np.abs(seg).max() + 1e-12):6.1f} dB")
print("cues", len(CUES), "written to", OUT)
