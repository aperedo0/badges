"""Sound, fifth try (2026-11-21), still made from scratch in code. The owner on the fourth try: "they sound like
this like deep metal. They really should sound like wood. Like the drops should sound like wood hitting wood. I
don't need a creak sound for when the chest opens, just a quick unlock, you know, when the latch opens. And then I
want to hear the fire, when the fires go on, I want to hear them turn on."

    python3 sound/tools/s5_make_sounds.py        (from the animation folder)

Same events and timing as the fourth try (s4_make_sounds.py), with these changes:
- Wood, not metal. Every knock is now a wooden body answering: many close resonances that wood's own friction kills
  within a few cycles (wood loses about 3 percent of its energy per cycle, iron about a tenth of a percent; that is
  the difference between a knock and a ring). They are made as noise in thirds of an octave, each band dying at
  tau = 1 / (pi f eta), plus a few just as damped low panel resonances for the box's body. The ringing iron straps,
  the stone floor's ring and the side rings' clinks after the landing are gone.
- Wood hitting wood: each landing excites the chest and a wooden floor (planks on joists), with a hard first touch
  that makes the knock crisp.
- The hall no longer rings: its first echoes were single clicks at exact delays, which comb filter into a metallic,
  tube like colour. Each echo is now a short scattered burst, as off rough stone.
- The opening is just the unlock: the lock clicks when the keyhole flashes, and the latch flips up with a light
  clack. No bolt scrape, no creak, no knock when the lid stops.
- Fire: each pair of torches catches with a soft whump and a rush as the flame climbs, a burst of crackles, then
  burns on quietly (a low flutter and an occasional pop). Each torch is placed where it stands, so the far pairs
  come later, quieter and more echoey.
- The sand is unchanged in kind.
"""
import json, math, os, wave
import numpy as np
from scipy.signal import butter, sosfilt, lfilter, iirpeak, fftconvolve

SR, FPS = 48000, 30
FRAMES = 860
N = int(round(FRAMES / FPS * SR))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "s5"))
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261125)
CUES = []
U = 0.127                                              # metres per scene unit (the chest is 5.5 units, about 0.7 m)
C = 343.0


def db(x):
    return 10.0 ** (x / 20.0)


def secs(s):
    return np.arange(int(s * SR)) / SR


def flt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def norm(y):
    m = np.abs(y).max()
    return y / m if m > 0 else y


def unit(y):
    return y / math.sqrt((y ** 2).sum() + 1e-12)


def place(y, x, at):
    i = int(round(at * SR))
    if 0 <= i < len(y):
        n = min(len(x), len(y) - i)
        y[i:i + n] += x[:n]


def fit(x, n):
    return x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))


def smooth(x, a, b):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ materials
BANDS = 63.0 * 2 ** (np.arange(24) / 3)               # 63 Hz to 10 kHz in thirds of an octave


def wood(s, peak, width=1.4, eta=0.032, lo=80, hi=10000, panels=(), panel_w=0.4, radiates=250.0):
    """How a wooden body answers a knock (its impulse response). peak and width (octaves) shape where its sound sits;
    eta is how much energy it loses per cycle; panels are its low resonances (frequency, eta). Below `radiates` Hz
    a box this size barely pushes air (front and back of a board cancel), and its glued and nailed joints rub away
    the slow, big movements faster: so the low end is weaker and shorter than the wood alone would give, which is
    what keeps a wooden knock from booming."""
    n = int(s * SR)
    t = secs(s)
    y = np.zeros(n)
    for f in BANDS[(BANDS >= lo) & (BANDS <= hi)]:
        b = flt(rng.standard_normal(n), "bandpass", [f * 2 ** (-1 / 6), min(f * 2 ** (1 / 6), 0.45 * SR)])
        e = eta * max(1.0, (radiates / f) ** 0.7)
        b *= np.exp(-t * math.pi * f * e * rng.uniform(0.8, 1.25))
        y += math.exp(-0.5 * (math.log2(f / peak) / width) ** 2) * min(1.0, f / radiates) ** 1.2 * unit(b)
    for f, e in panels:
        f *= rng.uniform(0.94, 1.06)
        y += panel_w * rng.uniform(0.7, 1.0) * unit(np.sin(2 * np.pi * f * t) * np.exp(-t * math.pi * f * e))
    return norm(y)


def modes(lo, hi, n, tau0, f0, alpha, tilt, s):
    """Separate resonances (small brass parts only, kept very short so they click rather than ring)."""
    f = np.exp(rng.uniform(np.log(lo), np.log(hi), n))
    tau = tau0 * (f / f0) ** (-alpha) * rng.uniform(0.7, 1.3, n)
    a = rng.lognormal(0, 0.5, n) * (f / f0) ** (-tilt)
    t = secs(s)[None, :]
    return norm((a[:, None] * np.sin(2 * np.pi * f[:, None] * t) * np.exp(-t / tau[:, None])).sum(0))


CHEST_PANELS = ((150, 0.09), (205, 0.08), (265, 0.07))   # the chest's big side and bottom boards
FLOOR_PANELS = ((115, 0.11),)                             # floor boards over their joists
LID_PANELS = ((230, 0.07),)


def contact(dur, rough=0.3):
    m = max(int(dur * SR), 8)
    return np.sin(np.pi * np.arange(m) / m) ** 2 * (1 + rough * rng.standard_normal(m))


def strike(T, crisp, flam, rough=0.3):
    """The force of one landing: a main push lasting T seconds, led by a hard first touch of edge on edge (what makes
    wood on wood crisp), repeated for each part that comes down (flam: delay, strength)."""
    f = np.zeros(int(0.08 * SR))
    for dt, a in flam:
        place(f, a * contact(T, rough), dt)
        place(f, a * crisp * contact(0.0003, 0.2), dt)
    return f


def excite(force, ir, n):
    return norm(fit(fftconvolve(force, ir), n))


def cavity(force, n, f=225.0, q=2.5):
    """The air inside the hollow chest answering a knock: a short, low, hollow tone."""
    b, a = iirpeak(f * rng.uniform(0.95, 1.05), q, fs=SR)
    return norm(fit(lfilter(b, a, np.pad(force, (0, n))), n))


def chatter(n, count, gap, decay, peak=1500):
    """Loose boards knocking against each other for a moment after a hit."""
    y = np.zeros(n)
    t = rng.uniform(0.004, 0.01)
    for j in range(count):
        place(y, rng.uniform(0.5, 1.0) * np.exp(-j / decay) * contact(0.0006, 0.5), t)
        t += gap * rng.uniform(0.7, 1.4)
    return excite(y, wood(0.12, peak, 1.2, 0.03, 250, 10000), n)


def grit(n, count, level):
    y = np.zeros(n)
    for _ in range(count):
        tk = flt(rng.standard_normal(40), "highpass", 2500) * np.exp(-np.arange(40) / 8.0)
        place(y, tk * level * rng.lognormal(0, 0.6), rng.uniform(0.02, n / SR * 0.9))
    return y


def chest_hit(v, flat=False, s=0.7):
    """The chest's wooden bottom landing on a wooden floor. v is the speed as a share of the first landing's speed."""
    n = int(s * SR)
    T = 0.0022 * max(v, 0.05) ** -0.2 * (1.2 if flat else 1.0)            # faster = harder, shorter contact
    flam = [(0.0, 1.0)] + ([(rng.uniform(0.006, 0.011), 0.5), (rng.uniform(0.014, 0.024), 0.3)] if flat
                           else [(rng.uniform(0.005, 0.01), 0.35)])
    F = strike(T, 0.6 * min(1.0, v) ** 0.3, flam)
    y = (1.0 * excite(F, wood(s, 700, 1.4, 0.032, 110, 10000, CHEST_PANELS), n)      # the chest's boards
         + 0.75 * excite(F, wood(s, 450, 1.4, 0.035, 90, 9000, FLOOR_PANELS, radiates=200.0), n)     # the floor's boards
         + 0.22 * cavity(F, n))                                                     # the hollow inside
    if v > 0.12:
        place(y, 0.3 * v * chatter(int(0.2 * SR), int(5 + 12 * v), 0.009, 3.0 + 4 * v), 0.012)
    y += grit(n, int(2 + 8 * v), 0.02)
    return norm(y)


def lid_knock(v, s=0.5):
    """The wooden lid dropping back onto the chest's wooden rim."""
    n = int(s * SR)
    F = strike(0.0016 * max(v, 0.05) ** -0.2, 0.55, [(0.0, 1.0), (rng.uniform(0.003, 0.007), 0.3)])
    y = (1.0 * excite(F, wood(s, 780, 1.3, 0.03, 120, 10000, LID_PANELS), n)
         + 0.6 * excite(F, wood(s, 460, 1.4, 0.032, 80, 10000, CHEST_PANELS), n)
         + 0.25 * cavity(F, n, 240, 3.0))
    return norm(y)


def tap(metal=0.35, peak=1600, s=0.25):
    """A small fitting (the gold latch, a side ring) tapping the chest: a light wooden tick with a brief click."""
    n = int(s * SR)
    F = contact(0.0005, 0.4)
    return norm(excite(F, wood(s, peak, 1.2, 0.03, 250, 10000), n)
                + metal * excite(F, modes(2500, 11000, 16, 0.004, 4000, 0.5, 0.1, s), n))


def scuff(s=0.2, rate=280):
    """The chest twisting a little on the floor: wood rubbing wood, many tiny catches."""
    imp = np.zeros(int(s * SR))
    tc = 0.0
    while tc < s:
        imp[int(tc * SR)] += rng.uniform(0.3, 1.0) * math.sin(math.pi * tc / s)
        tc += 1.0 / (rate * rng.uniform(0.5, 1.5))
    n = len(imp) + int(0.05 * SR)
    return norm(excite(imp, wood(0.12, 900, 1.3, 0.035, 150, 9000), n) + 0.6 * excite(imp, wood(0.12, 600, 1.4, 0.04, 100, 8000), n))


# ------------------------------------------------------------------ the hall
ROOM = dict(x=(-4.2, 4.2), y=(-3.8, 11.3), z=(0.0, 7.0))
REFL = dict(x=(0.7, 0.7), y=(0.55, 0.6), z=(0.85, 0.7))     # how much each surface sends back (low side, high side)
EARS = [(-0.09, -1.81, 0.25), (0.09, -1.81, 0.25)]        # the camera while the chest is shut (scene units (0, -14.24, 0.62))


def tail_ir(seed, s=1.6, rts=(1.3, 1.2, 0.7)):
    tt = secs(s)
    tail = (flt(seed, "lowpass", 500) * np.exp(-6.91 * tt / rts[0]) + flt(seed, "bandpass", [500, 3000]) * np.exp(-6.91 * tt / rts[1])
            + flt(seed, "highpass", 3000) * np.exp(-6.91 * tt / rts[2]))
    return tail * np.clip((tt - 0.03) / 0.05, 0, 1)


def scatter(order):
    """One echo off rough stone: a short burst rather than a single click (unit energy)."""
    m = int((0.0006 + 0.0012 * order) * SR)
    return unit(rng.standard_normal(m) * np.exp(-np.arange(m) / (0.35 * m)))


def hall(src, drr_db=0.0, s=1.6):
    """Impulse responses (left, right) from a point in the hall to the camera: the direct sound, the first echoes from
    each surface at their true delays (images up to three bounces, each scattered), and the long stone tail."""
    out = []
    lo = {k: ROOM[k][0] for k in ROOM}
    L = {k: ROOM[k][1] - ROOM[k][0] for k in ROOM}
    src_ = {k: v - lo[k] for k, v in zip("xyz", src)}
    tail_seed = rng.standard_normal((2, int(s * SR)))
    for e_i, ear in enumerate(EARS):
        ear_ = {k: v - lo[k] for k, v in zip("xyz", ear)}
        d0 = math.dist(src, ear)
        ir = np.zeros(int(s * SR))
        early = np.zeros(int(s * SR))
        for nx in range(-3, 4):
            for ny in range(-3, 4):
                for nz in range(-3, 4):
                    order = abs(nx) + abs(ny) + abs(nz)
                    if order > 3:
                        continue
                    p, g = [], 1.0
                    for k, nn in zip("xyz", (nx, ny, nz)):
                        p.append(nn * L[k] + (src_[k] if nn % 2 == 0 else L[k] - src_[k]))
                        hi_hits = (abs(nn) + 1) // 2 if nn > 0 else abs(nn) // 2
                        lo_hits = abs(nn) - hi_hits
                        g *= REFL[k][0] ** lo_hits * REFL[k][1] ** hi_hits
                    d = math.dist(p, (ear_["x"], ear_["y"], ear_["z"]))
                    t = (d - d0) / C + 0.002
                    k0 = int(t * SR)
                    if order == 0:
                        fr = t * SR - k0
                        ir[k0] += 1 - fr
                        ir[k0 + 1] += fr
                    elif k0 + 200 < len(ir):
                        place(early, g * d0 / d * scatter(order), t)
        early = flt(early, "lowpass", 6000)
        tail = tail_ir(tail_seed[e_i], s)
        tail *= math.sqrt(db(drr_db) / max((tail ** 2).sum(), 1e-12))
        out.append(ir + early + tail)
    return out


class Spot:
    """Sounds that come from one place in the hall."""
    def __init__(self, name, pos_units, drr_db):
        self.name = name
        self.pos = tuple(v * U for v in pos_units)
        self.drr = drr_db
        self.dry = np.zeros(N)

    def add(self, sig, frame, gain_db=0.0, label=None):
        place(self.dry, sig * db(gain_db), frame / FPS)
        if label:
            CUES.append({"sound": label, "frame": round(frame, 2), "seconds": round(frame / FPS, 3), "level_db": round(gain_db, 1)})

    def render(self):
        irL, irR = hall(self.pos, self.drr)
        return fit(fftconvolve(self.dry, irL), N), fit(fftconvolve(self.dry, irR), N)


class Torches:
    """The torches stand far down the hall, most beyond the room the echoes are built from: each is heard directly
    (later, quieter and duller with distance, to its side) plus the hall's echo, which in a big stone hall is about as
    loud everywhere, so a far torch is mostly echo."""
    EAR = (0.0, -15.0, 4.0)                            # the camera while the torches catch (scene units)
    RC = 5.0                                           # metres at which the direct sound and the echo are equally loud
    name = "torches"

    def __init__(self):
        self.L, self.R, self.send = np.zeros(N), np.zeros(N), np.zeros(N)
        self.d0 = None

    def add(self, sig, frame, pos_units, gain_db=0.0, label=None):
        rel = [(a - b) * U for a, b in zip(pos_units, self.EAR)]
        d = math.hypot(*rel)
        self.d0 = self.d0 or d
        p = rel[0] / d                                 # how far to the side
        g = db(gain_db)
        dry = flt(sig, "lowpass", max(5000.0, 16000.0 - 330.0 * d))
        at = frame / FPS + d / C
        place(self.L, math.sqrt(1 - p) * g * self.d0 / d * dry, at + 0.0003 * p)
        place(self.R, math.sqrt(1 + p) * g * self.d0 / d * dry, at - 0.0003 * p)
        place(self.send, g * self.d0 / self.RC * math.sqrt(self.d0 / d) * sig, at)   # a long hall's echo still fades along it
        if label:
            CUES.append({"sound": label, "frame": round(frame, 2), "seconds": round(frame / FPS, 3), "level_db": round(gain_db, 1)})

    def render(self):
        seed = rng.standard_normal((2, int(2.2 * SR)))
        out = []
        for e, direct in enumerate((self.L, self.R)):
            ir = tail_ir(seed[e], 2.2, (1.6, 1.4, 0.8))
            ir[: int(0.012 * SR)] = 0.0
            out.append(direct + fit(fftconvolve(self.send, unit(ir)), N))
        return out


CHEST = Spot("chest", (0.0, 0.0, 2.0), -7.0)
SANDL = Spot("sand_left", (-10.0, 36.0, 0.0), 2.0)
SANDR = Spot("sand_right", (11.5, 47.0, 0.0), 3.0)
FIRE = Torches()
SPOTS = (CHEST, SANDL, SANDR, FIRE)

# ------------------------------------------------------------------ the landing (measured in the scene)
LAND = [(44.6, 1.00, False, "chest lands on its left corner"), (49.6, 0.51, True, "the right side comes down flat"),
        (60.1, 0.18, True, "it rocks back and the left side comes down"), (61.9, 0.05, False, "a last small settle")]
for fr, v, flat, lab in LAND:
    CHEST.add(chest_hit(v, flat), fr, -4.0 + 20 * math.log10(v) + (3.5 if flat else 0.0), label=lab)

# ------------------------------------------------------------------ the sand from the vault ("the smoke that comes down")
rng = np.random.default_rng(20261126)
for spot in (SANDL, SANDR):
    s = 0.9
    pour = norm(flt(rng.standard_normal(int(s * SR)), "bandpass", [2000, 7000])) * np.minimum(1, secs(s) / 0.08) * np.exp(-secs(s) / 0.28)
    spot.add(pour, 44.6 + 0.08 * FPS, -36, label="sand pours from the vault" if spot is SANDL else None)
    s = 1.3
    tt = secs(s)
    y = np.zeros(len(tt))
    stone = modes(2500, 11000, 18, 0.0025, 4000, 0.3, 0.2, 0.02)
    for i in np.nonzero(rng.poisson(420 * np.exp(-((tt - 0.45) / 0.22) ** 2) / SR))[0]:
        place(y, stone * rng.lognormal(0, 0.7) * 0.5, i / SR)
    y += 0.18 * norm(flt(rng.standard_normal(len(tt)), "bandpass", [2500, 8000])) * np.exp(-((tt - 0.45) / 0.3) ** 2)
    spot.add(norm(y), 44.6 + 1.3 * FPS, -24, label="sand lands on the stone" if spot is SANDL else None)


# ------------------------------------------------------------------ the waiting rattles (from the rendered motion)
def bump(k, a, b, amp):
    return amp * math.sin(math.pi * (k - a) / (b - a)) ** 2 if a <= k <= b else 0.0


STRONG, RATTLE = (2.0, 2.0, 3.0), 30


def ss(x, a, b):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


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
    yaw = curves["yaw"]
    sp = np.abs(np.gradient(yaw, step))
    if sp.max() > 0.05:
        found.append((float(ks[np.argmax(sp)]), "yaw", float(sp.max())))
    return sorted(found)


rng = np.random.default_rng(20261127)
ALL = {kind: contacts(kind) for kind in (0, 1, 2)}
REF = {}
for kind, cs in ALL.items():
    for k, part, v in cs:
        base = part.split("_")[0]
        REF[base] = max(REF.get(base, 0), v)


def lvl(base_db, v, ref):
    return base_db + max(-30.0, 20 * math.log10(max(v, 1e-6) / ref))


KIND_DB = {0: 14.0, 1: 3.0, 2: -4.0}                  # so the three rattles are about equally noticeable (the first moves slowest)
for start, kind in ((124, 0), (199, 1), (274, 2)):
    first = True
    lab = ("rattle: two knocks", "rattle: one hard jolt", "rattle: a shiver")[kind]
    for k, part, v in ALL[kind]:
        fr = start + k
        if part == "lid":
            CHEST.add(lid_knock(v / REF["lid"]), fr, lvl(-12, v, REF["lid"]) + KIND_DB[kind], label=lab if first else None)
        elif part == "hop":
            CHEST.add(chest_hit(0.16, True), fr, -12 + KIND_DB[kind], label=lab if first else None)
        elif part.startswith("roll"):
            CHEST.add(chest_hit(0.07, False), fr, lvl(-17, v, REF["roll"]) + KIND_DB[kind], label=lab if first else None)
        elif part == "yaw":
            CHEST.add(scuff(0.18, 280) * 0.7, fr - 2, lvl(-24, v, REF["yaw"]) + KIND_DB[kind])
        elif part.startswith("hasp"):
            CHEST.add(tap(0.4, 1700), fr, lvl(-19, v, REF["hasp"]) + KIND_DB[kind])
        elif part.startswith("ring"):
            CHEST.add(tap(0.25, 1100), fr + 0.5, lvl(-25, v, REF["ring"]) + KIND_DB[kind])
        first = False

# ------------------------------------------------------------------ the unlock (no creak, no lid knock)
rng = np.random.default_rng(20261128)
n = int(0.35 * SR)
clk = np.zeros(n)
for dt, a, d in ((0.0, 1.0, 0.0006), (0.012, 0.65, 0.0005)):         # the lock's catch lets go, the bolt snaps back
    f_ = contact(d, 0.5)
    place(clk, a * (0.8 * excite(f_, modes(2200, 12000, 18, 0.005, 4000, 0.5, 0.15, 0.3), n)
                    + 1.0 * excite(f_, wood(0.35, 700, 1.3, 0.03, 120, 10000, CHEST_PANELS), n) + 0.2 * cavity(f_, n)), dt)
CHEST.add(norm(clk), 355, -7, label="lock clicks open")
n = int(0.4 * SR)
cl = np.zeros(n)
for dt, a in ((0.0, 1.0), (0.038, 0.3), (0.061, 0.1)):               # the latch flips up and knocks against the lid
    f_ = contact(0.0007, 0.4)
    place(cl, a * (0.6 * excite(f_, modes(1600, 10000, 18, 0.007, 3000, 0.5, 0.15, 0.3), n)
                   + 1.0 * excite(f_, wood(0.35, 950, 1.3, 0.03, 150, 10000, LID_PANELS), n)), dt)
CHEST.add(norm(cl), 373, -6, label="latch flips up")


# ------------------------------------------------------------------ the torches catching, pair after pair
def torch_fire(length):
    """One torch from the moment it starts to catch: a soft whump as its fuel lights, a rush as the flame climbs the
    head, a burst of crackles, then a quiet steady burn (a low flutter and now and then a pop). Follows the flame's
    size as the scene keys it: 0 at the start, 1.15 at 14 frames, 1.0 at 34."""
    n = int(length * SR)
    t = secs(length)
    fr = t * FPS
    size = np.where(fr < 14, 1.15 * smooth(fr, 0, 14), 1.15 - 0.15 * smooth(fr, 14, 34))
    grow = np.clip(np.gradient(size, 1.0 / SR), 0, None)
    grow /= grow.max()
    t0 = 2.5 / FPS                                                      # the flame shows a few frames in
    tw = np.clip(t - t0, 0, None)
    whump = flt(flt(rng.standard_normal(n), "lowpass", 600), "highpass", 90) * np.clip(tw / 0.06, 0, 1) ** 2 * np.exp(-tw / 0.17)
    rush = flt(rng.standard_normal(n), "bandpass", [500, 4500]) * grow ** 1.5
    flick = np.clip(1 + 0.45 * norm(flt(rng.standard_normal(n), "lowpass", 7)), 0.2, None)
    burn = flt(flt(rng.standard_normal(n), "lowpass", 1100), "highpass", 90) * size * flick
    crack = np.zeros(n)
    rate = 3.0 + 70.0 * grow
    for i in np.nonzero(rng.random(n) < rate / SR)[0]:
        if rng.random() < 0.12:                                         # a pop: a pocket of pitch bursting
            m = int(rng.uniform(0.003, 0.006) * SR)
            ev = 2.5 * flt(rng.standard_normal(m), "bandpass", [600, 5000]) * np.exp(-np.arange(m) / (0.25 * m))
        else:
            m = int(rng.uniform(0.0004, 0.002) * SR)
            ev = flt(rng.standard_normal(m), "highpass", 1500) * np.exp(-np.arange(m) / (0.3 * m))
        place(crack, ev * rng.lognormal(0, 0.7), i / SR)
    return 1.0 * norm(whump) + 0.35 * norm(rush) + 0.05 * norm(burn) + 0.3 * norm(crack)


rng = np.random.default_rng(20261129)
FIRE_DB = -18.0
TORCH_SPOTS = []
for sx in (-1, 1):
    TORCH_SPOTS.append((0, sx * 17.2, 58.0, 15.0))
    TORCH_SPOTS.append((1, sx * 17.5, 87.0, 13.5))
    for k, yb in enumerate((116.0, 145.0, 174.0, 203.0)):
        TORCH_SPOTS.append((2 + k, sx * 14.4, yb, 12.5))
for g, x, y, z in sorted(TORCH_SPOTS):
    a = 425 + 15 * g + rng.uniform(0.0, 0.8)                           # the two of a pair catch together, a hair apart
    FIRE.add(torch_fire((FRAMES - a) / FPS + 0.2), a, (x, y, z), FIRE_DB,
             label=f"torches catch, pair {g + 1} of 6" if x < 0 else None)

# ------------------------------------------------------------------ mix
L, R = np.zeros(N), np.zeros(N)
stems = {}
for sp in SPOTS:
    l, r = sp.render()
    stems[sp.name] = (l, r)
    L += l
    R += r
L, R = flt(L, "highpass", 70), flt(R, "highpass", 70)
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
for name, (l, r) in stems.items():
    write(os.path.join(OUT, f"stem_{name}.wav"), l * g, r * g)
json.dump({"note": "frames of Chest reveal whole scene preview.mp4 at 30 a second",
           "rattle_contacts": {str(k): [(round(a, 2), p, round(v, 3)) for a, p, v in cs] for k, cs in ALL.items()},
           "cues": sorted(CUES, key=lambda c: c["frame"])}, open(os.path.join(OUT, "cues.json"), "w"), indent=1)
m = 0.5 * (L + R)
for name, a_, b_ in (("chest lands (1.45 to 1.6 s)", 1.45, 1.6), ("second thud (1.64 to 1.8 s)", 1.64, 1.8), ("left side down (1.99 to 2.15 s)", 1.99, 2.15),
                     ("rattle 1 (4.1 to 5.1 s)", 4.1, 5.1), ("rattle 2 (6.6 to 7.6 s)", 6.6, 7.6), ("rattle 3 (9.1 to 10.1 s)", 9.1, 10.1),
                     ("lock (11.8 to 12.1 s)", 11.8, 12.1), ("latch (12.4 to 12.8 s)", 12.4, 12.8),
                     ("first torches (14.1 to 14.8 s)", 14.1, 14.8), ("last torches (16.6 to 17.3 s)", 16.6, 17.3),
                     ("torches burning (25 to 28 s)", 25.0, 28.0)):
    seg = m[int(a_ * SR):int(b_ * SR)]
    print(f"{name:34s} loudness {20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12):6.1f} dB   peak {20 * np.log10(np.abs(seg).max() + 1e-12):6.1f} dB")
print("cues", len(CUES))
