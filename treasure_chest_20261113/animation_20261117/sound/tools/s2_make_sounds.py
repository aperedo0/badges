"""Sound, second try (2026-11-21), still made from scratch in code. After the first try the owner said:
"there's a sound that I think that's just in the background. I want those sounds removed. I only want sounds for,
like, the chest opening, falling every time it hits the floor, the smoke that comes down [the sand], pretty much
just those ... they sound a little too cartoony ... I want like a realistic direction."

    python3 sound/tools/s2_make_sounds.py        (from the animation folder)

Writes sound/s2/mix.wav, stem_*.wav and cues.json. Same timing as the first try (frames of
`Chest reveal whole scene preview.mp4`).

Kept: the chest landing (each contact with the floor) with the side rings knocking, the sand falling from the vault,
the chest opening (bolt, lock, clasp, lid creak, lid stop). Removed: the hall's rumble and draft, the tone with the
keyhole glow, the air rushing past the falling chest, the cold burst and the smoke rising out of the chest, the
torches, the warm swell, the rattles (not in the owner's list; asked).

What made the first try sound like a cartoon, and what replaces it:
- clean ringing tones (a few pure decaying sines per knock: a woodblock, a bell) -> dozens of closely packed,
  heavily damped resonances at uneven frequencies, struck by a short rough contact, so each hit is a dull textured
  "thock" like real wood, iron and stone; higher resonances die faster, as they do in wood;
- a booming drop (a low tone sliding down in pitch) -> a short low thump from the floor and the chest's mass, no
  pitch slide, and two or three contacts a few milliseconds apart, the way a box lands on a corner;
- a squeaky door (one narrow singing resonance in the creak) -> slow uneven stick and slip of an iron hinge that
  comes in bursts, each catch shaking the whole lid, so it reads as an old wooden lid, not a tone;
- a whistling clasp (a sliding tone) -> a short gritty scrape of the hinge pin.
"""
import json, os, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR, FPS = 48000, 30
FRAMES = 860
N = int(round(FRAMES / FPS * SR))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "s2"))
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261122)
CUES = []


def db(x):
    return 10.0 ** (x / 20.0)


def secs(s):
    return np.arange(int(s * SR)) / SR


def flt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def norm(y):
    m = np.abs(y).max()
    return y / m if m > 0 else y


def place(y, x, at):
    i = int(round(at * SR))
    if 0 <= i < len(y):
        n = min(len(x), len(y) - i)
        y[i:i + n] += x[:n]


class Bus:
    def __init__(self, name):
        self.name, self.L, self.R, self.send = name, np.zeros(N), np.zeros(N), np.zeros(N)

    def add(self, sig, frame, gain=1.0, pan=0.0, wet=0.25, label=None):
        i = int(round(frame / FPS * SR))
        n = min(len(sig), N - i)
        a = (pan + 1.0) * np.pi / 4.0
        self.L[i:i + n] += sig[:n] * gain * np.cos(a)
        self.R[i:i + n] += sig[:n] * gain * np.sin(a)
        self.send[i:i + n] += sig[:n] * gain * wet
        if label:
            CUES.append({"sound": label, "frame": round(frame, 2), "seconds": round(frame / FPS, 3)})


# ------------------------------------------------------------------ materials
def modes(lo, hi, n, tau0, f0, alpha, tilt, s):
    """The ringing of a struck material: n resonances spread unevenly between lo and hi Hz, each dying away;
    tau0 is how long one at f0 Hz rings, alpha how much faster the higher ones die, tilt how much weaker they are."""
    f = np.exp(rng.uniform(np.log(lo), np.log(hi), n))
    tau = tau0 * (f / f0) ** (-alpha) * rng.uniform(0.7, 1.3, n)
    a = rng.lognormal(0, 0.5, n) * (f / f0) ** (-tilt)
    t = secs(s)[None, :]
    y = (a[:, None] * np.sin(2 * np.pi * f[:, None] * t + rng.uniform(0, 2 * np.pi, (n, 1))) * np.exp(-t / tau[:, None])).sum(0)
    return norm(y)


def contact(dur, rough=0.35):
    """The moment of touching: a short soft pulse with a rough edge (shorter = harder, brighter)."""
    m = max(int(dur * SR), 8)
    return np.sin(np.pi * np.arange(m) / m) ** 2 * (1 + rough * rng.standard_normal(m))


def strike(ir, dur, rough=0.35):
    return norm(fftconvolve(contact(dur, rough), ir)[: len(ir)])


def grit(s, count, lo=2500, level=0.03):
    """Tiny bits of dust and grit skittering on stone after a hit."""
    y = np.zeros(int(s * SR))
    for _ in range(count):
        tk = flt(rng.standard_normal(40), "highpass", lo) * np.exp(-np.arange(40) / 8.0)
        place(y, tk * level * rng.lognormal(0, 0.6), rng.uniform(0.02, s * 0.9))
    return y


def chest_lands(strength=1.0):
    """A wooden chest with iron straps landing on stone: dull wood, damped iron, a low thump, grit."""
    s = 1.0
    wood = modes(70, 3200, 56, 0.07, 100, 0.6, 0.45, s)
    iron = modes(700, 9000, 34, 0.035, 1000, 0.55, 0.25, s)
    low = modes(48, 130, 6, 0.08, 80, 0.3, 0.0, s)
    y = np.zeros(int(s * SR))
    hits = [(0.0, 1.0, 0.007), (rng.uniform(0.006, 0.013), 0.5, 0.005), (rng.uniform(0.022, 0.04), 0.25, 0.004)]
    for dt, a, d in hits[: 2 + int(strength > 0.6)]:
        place(y, a * (1.0 * strike(wood, d) + 0.3 * strike(iron, d * 0.6, 0.6) + 0.4 * strength * strike(low, d * 1.6, 0.1)), dt)
        floor = flt(rng.standard_normal(int(0.03 * SR)), "lowpass", 3800) * np.exp(-secs(0.03) / 0.006)
        place(y, a * 0.22 * norm(floor), dt)
    thump = flt(rng.standard_normal(int(0.25 * SR)), "lowpass", 150) * np.exp(-secs(0.25) / 0.05)
    place(y, 1.0 * strength * norm(thump), 0.0)                        # the low end is a thump of noise, not a tone
    y += np.pad(grit(0.5, int(14 * strength) + 3, level=0.04), (0, len(y) - int(0.5 * SR)))
    return norm(y)


def iron_ring_knock():
    """A heavy iron ring swinging against its iron mount on wood: short, damped, a little ring."""
    s = 0.5
    ring = modes(650, 6500, 26, 0.05, 1000, 0.45, 0.2, s)
    wood = modes(200, 2500, 20, 0.03, 300, 0.6, 0.4, s)
    return norm(strike(ring, 0.0015, 0.5) + 0.45 * strike(wood, 0.002))


def scrape(s, rate, steel_tau=0.004, bright=(1500, 9000)):
    """Metal sliding on metal: many tiny catches at an uneven rate, each a very short damped tick."""
    steel = modes(bright[0], bright[1], 24, steel_tau, 2500, 0.3, 0.1, 0.05)
    imp = np.zeros(int(s * SR))
    tc = 0.0
    while tc < s:
        u = tc / s
        imp[int(tc * SR)] += rng.uniform(0.3, 1.0) * np.sin(np.pi * u) ** 0.5
        tc += 1.0 / (rate * rng.uniform(0.5, 1.5))
    return norm(fftconvolve(imp, steel)[: len(imp) + int(0.03 * SR)])


# ------------------------------------------------------------------ the sounds
DROP, SAND, OPEN = Bus("landing"), Bus("sand"), Bus("opening")

# the chest lands on one corner (45), the other side comes down (49), it rocks and settles (60, 62.5)
DROP.add(chest_lands(1.0) * db(-3), 45, wet=0.3, label="chest lands, first corner")
DROP.add(chest_lands(0.6) * db(-8), 49, pan=0.12, wet=0.3, label="the other side comes down")
DROP.add(chest_lands(0.3) * db(-16), 60, pan=-0.08, wet=0.3, label="it rocks and settles")
DROP.add(chest_lands(0.15) * db(-26), 62.5, wet=0.3)
for k, (fr, g) in enumerate([(46.5, -20), (50, -23), (54, -27), (59, -30), (65, -34), (73, -38)]):
    for side in (-1, 1):
        DROP.add(iron_ring_knock() * db(g + rng.uniform(-2, 1)), fr + rng.uniform(0, 1.5), pan=0.5 * side, wet=0.25,
                 label="side rings knock against their mounts" if k == 0 and side < 0 else None)

# the sand (the "smoke that comes down"): a faint pour high up, then grains landing on the stone floor
for side, pan in ((-1, -0.55), (1, 0.55)):
    s = 0.9
    pour = norm(flt(rng.standard_normal(int(s * SR)), "bandpass", [2000, 7000])) * np.minimum(1, secs(s) / 0.08) * np.exp(-secs(s) / 0.28)
    SAND.add(pour * db(-34), 45 + 0.08 * FPS, pan=pan * 0.8, wet=0.7, label="sand pours from the vault" if side < 0 else None)
    s = 1.3
    tt = secs(s)
    y = np.zeros(len(tt))
    rate = 420 * np.exp(-((tt - 0.45) / 0.22) ** 2)
    stone = modes(2500, 11000, 18, 0.0025, 4000, 0.3, 0.2, 0.02)
    for i in np.nonzero(rng.poisson(rate / SR))[0]:
        place(y, stone * rng.lognormal(0, 0.7) * 0.5, i / SR)
    y += 0.18 * norm(flt(rng.standard_normal(len(tt)), "bandpass", [2500, 8000])) * np.exp(-((tt - 0.45) / 0.3) ** 2)
    SAND.add(norm(y) * db(-23), 45 + 1.3 * FPS, pan=pan, wet=0.45, label="sand lands on the stone" if side < 0 else None)

# the chest opening: the bolt slides back, the lock clicks, the clasp lifts and drops, the lid creaks up and stops
OPEN.add(scrape(0.16, 520) * db(-24), 349, wet=0.2, label="bolt slides back")
steel = modes(1800, 11000, 30, 0.02, 3000, 0.45, 0.15, 0.4)
box = modes(150, 2600, 30, 0.035, 300, 0.6, 0.4, 0.4)
clk = np.zeros(int(0.4 * SR))
place(clk, strike(steel, 0.0009, 0.6) + 0.55 * strike(box, 0.0015), 0.0)        # the bolt reaches its end
place(clk, 0.8 * (strike(steel, 0.0007, 0.6) + 0.5 * strike(box, 0.0012)), 0.011)  # the latch drops
OPEN.add(norm(clk) * db(-8), 355, wet=0.2, label="lock clicks open")
OPEN.add(scrape(0.11, 160, 0.003, (1200, 7000)) * db(-30), 365, wet=0.2, label="clasp lifts")
hasp = modes(900, 8000, 30, 0.05, 1000, 0.5, 0.2, 0.6)
plate = modes(200, 3000, 26, 0.035, 300, 0.6, 0.4, 0.6)
cl = np.zeros(int(0.6 * SR))
for dt, a in ((0.0, 1.0), (0.047, 0.32), (0.082, 0.1)):
    place(cl, a * (strike(hasp, 0.0012, 0.5) + 0.6 * strike(plate, 0.002)), dt)
OPEN.add(norm(cl) * db(-12), 373, wet=0.25, label="clasp drops against the chest")

# the lid's creak: an old iron hinge sticking and slipping in bursts, each catch shaking the hinge and the lid
T = (416 - 389) / FPS
imp = np.zeros(int(T * SR))
burst = flt(rng.standard_normal(int(T * SR)), "lowpass", 6)                    # when it sticks and when it slides quietly
burst = np.clip((burst - np.percentile(burst, 35)) / (np.percentile(burst, 95) - np.percentile(burst, 35)), 0, 1)
tc = 0.0
while tc < T:
    u = tc / T
    i = int(tc * SR)
    imp[i] += burst[i] * np.sin(np.pi * min(u * 1.1, 1.0)) ** 0.5 * rng.uniform(0.4, 1.0)
    tc += 1.0 / ((22 + 40 * burst[i]) * rng.uniform(0.7, 1.3))
hinge = modes(1200, 7000, 26, 0.008, 2000, 0.4, 0.15, 0.15)
lidw = modes(110, 2200, 40, 0.035, 200, 0.6, 0.45, 0.25)
cr = norm(fftconvolve(imp, 0.45 * hinge[: int(0.15 * SR)])[: len(imp)]) + norm(fftconvolve(imp, lidw[: int(0.25 * SR)])[: len(imp)])
cr += 0.25 * norm(flt(rng.standard_normal(len(imp)), "bandpass", [600, 3500])) * burst * 0.5          # the hinge pin's grit
OPEN.add(norm(cr) * db(-15), 389, wet=0.25, label="lid creaks open")
lid_stop = np.zeros(int(0.6 * SR))
for dt, a_ in ((0.0, 1.0), (0.06, 0.25)):
    place(lid_stop, a_ * strike(lidw, 0.004 if dt == 0 else 0.003), dt)
    place(lid_stop, a_ * 0.4 * strike(hinge, 0.0015, 0.5), dt)
OPEN.add(norm(lid_stop) * db(-13), 416, wet=0.3, label="lid stops, fully open")


# ------------------------------------------------------------------ the stone hall (the same kind as the first try)
def hall_ir(s=3.2):
    tt = secs(s)
    out = []
    for _ in range(2):
        nz = rng.standard_normal(len(tt))
        ir = (flt(nz, "lowpass", 500) * np.exp(-6.91 * tt / 2.8) + flt(nz, "bandpass", [500, 3000]) * np.exp(-6.91 * tt / 2.2)
              + flt(nz, "highpass", 3000) * np.exp(-6.91 * tt / 1.0))
        pre = int(0.02 * SR)
        ir = np.concatenate([np.zeros(pre), ir])[: len(tt)] * np.minimum(1, tt / 0.05)
        for d, gg in ((0.011, 0.55), (0.019, 0.45), (0.031, 0.38), (0.044, 0.3), (0.058, 0.25), (0.079, 0.2)):
            ir[int((d + rng.uniform(-0.002, 0.002)) * SR)] += gg * rng.choice([-1, 1]) * 3
        out.append(ir / np.sqrt((ir ** 2).sum()))
    return out


BUSES = (DROP, SAND, OPEN)
send = sum(b.send for b in BUSES)
irL, irR = hall_ir()
L = sum(b.L for b in BUSES) + fftconvolve(send, irL)[:N] * db(-5)
R = sum(b.R for b in BUSES) + fftconvolve(send, irR)[:N] * db(-5)
L, R = flt(L, "highpass", 25), flt(R, "highpass", 25)
g = db(-1.0) / max(np.abs(L).max(), np.abs(R).max())
L, R = L * g, R * g


def write(path, l, r):
    x = np.stack([l, r], 1)
    x = np.clip(x + (rng.uniform(-0.5, 0.5, x.shape) + rng.uniform(-0.5, 0.5, x.shape)) / 32768, -1, 1)
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
m = 0.5 * (L + R)
for name, a_, b_ in (("before the landing (0 to 1.4 s)", 0, 1.4), ("chest lands (1.4 to 2.2 s)", 1.4, 2.2), ("sand lands (2.6 to 3.4 s)", 2.6, 3.4),
                     ("waiting (4.2 to 11.6 s)", 4.2, 11.6), ("lock and clasp (11.6 to 12.9 s)", 11.6, 12.9), ("lid (12.9 to 14.2 s)", 12.9, 14.2),
                     ("after (15 to 28.6 s)", 15.0, 28.6)):
    seg = m[int(a_ * SR):int(b_ * SR)]
    r = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12)
    p = 20 * np.log10(np.abs(seg).max() + 1e-12)
    print(f"{name:34s} loudness {r:6.1f} dB   peak {p:6.1f} dB")
print("cues", len(CUES))
