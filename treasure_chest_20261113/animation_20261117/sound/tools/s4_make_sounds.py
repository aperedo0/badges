"""Sound, fourth try (2026-11-21), still made from scratch in code: the third try made lighter. The owner: "I want
them to sound more light/light hearted without sounding fake, still very real."

    python3 sound/tools/s4_make_sounds.py        (from the animation folder)

The same events, timing and method as the third try (s3_make_sounds.py: contacts from the scene, the room built
from the hall). What makes it lighter while staying real:
- less weight: the deep thump under every hit is about a third as strong, the very lowest rumble is cut, and the
  big landing sits 4 dB lower against everything else, so it no longer dominates;
- a smaller, friendlier wooden box: the wood rings a little higher and crisper (shorter, brighter contacts), and
  the hollow box sound is higher and softer, like a well made chest rather than a crate;
- brighter, pleasant metal: the clasp and the side rings ring a touch longer and a little higher, and the small
  clinks are a little more present;
- a drier, smaller sounding hall: the echo dies in about 1.3 seconds instead of 2.6, and there is less of it, so
  the sounds are close and clear rather than cavernous;
- a gentler lid: a shorter, higher, softer creak with little groan;
- no added density on the hits (the third try squeezed them a little to sound heavier).
"""
import json, math, os, wave
import numpy as np
from scipy.signal import butter, sosfilt, lfilter, iirpeak, fftconvolve

SR, FPS = 48000, 30
FRAMES = 860
N = int(round(FRAMES / FPS * SR))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "s4"))
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261123)
CUES = []
U = 0.127                                              # metres per scene unit (the chest is 5.5 units, about 0.7 m)


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


def fit(x, n):
    return x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))


# ------------------------------------------------------------------ materials
def modes(lo, hi, n, tau0, f0, alpha, tilt, s):
    f = np.exp(rng.uniform(np.log(lo), np.log(hi), n))
    tau = tau0 * (f / f0) ** (-alpha) * rng.uniform(0.7, 1.3, n)
    a = rng.lognormal(0, 0.5, n) * (f / f0) ** (-tilt)
    t = secs(s)[None, :]
    return norm((a[:, None] * np.sin(2 * np.pi * f[:, None] * t + rng.uniform(0, 2 * np.pi, (n, 1))) * np.exp(-t / tau[:, None])).sum(0))


def contact(dur, rough=0.35):
    m = max(int(dur * SR), 8)
    return np.sin(np.pi * np.arange(m) / m) ** 2 * (1 + rough * rng.standard_normal(m))


def excite(force, ir, n):
    return norm(fit(fftconvolve(force, ir), n))


def cavity(force, n, f=235.0, q=4.0):
    """The air inside the hollow chest answering a knock: a short low hollow resonance."""
    b, a = iirpeak(f * rng.uniform(0.95, 1.05), q, fs=SR)
    return norm(fit(lfilter(b, a, np.pad(force, (0, n))), n))


def chatter(n, count, gap, decay, lo=300, hi=4000):
    """Loose planks and straps knocking against each other for a moment after a hit."""
    y = np.zeros(n)
    t = rng.uniform(0.004, 0.01)
    for j in range(count):
        place(y, rng.uniform(0.5, 1.0) * np.exp(-j / decay) * contact(0.0008, 0.6), t)
        t += gap * rng.uniform(0.7, 1.4)
    return excite(y, modes(lo, hi, 30, 0.012, 600, 0.5, 0.3, 0.08), n)


def grit(n, count, level):
    y = np.zeros(n)
    for _ in range(count):
        tk = flt(rng.standard_normal(40), "highpass", 2500) * np.exp(-np.arange(40) / 8.0)
        place(y, tk * level * rng.lognormal(0, 0.6), rng.uniform(0.02, n / SR * 0.9))
    return y


def chest_hit(v, flat=False, s=1.1):
    """The chest's bottom hitting stone floor. v is the speed as a share of the first landing's speed."""
    n = int(s * SR)
    dur = 0.0042 * max(v, 0.05) ** -0.2 * (1.2 if flat else 1.0)          # faster = harder, shorter contact
    force = np.zeros(int(0.06 * SR))
    flam = [(0.0, 1.0)] + ([(rng.uniform(0.005, 0.01), 0.45), (rng.uniform(0.013, 0.022), 0.25)] if flat else [(rng.uniform(0.006, 0.012), 0.4)])
    for dt, a in flam:
        place(force, a * contact(dur), dt)
    bright = min(1.0, v) ** 0.5
    y = (1.0 * excite(force, modes(110, 4200, 60, 0.045, 140, 0.65, 0.35, s), n)               # wooden planks
         + 0.45 * cavity(force, n)                                                              # the hollow inside
         + 0.35 * bright * excite(force, modes(700, 10000, 40, 0.03, 1000, 0.55, 0.2, s), n)    # iron straps and corners
         + 0.3 * bright * excite(force, modes(1500, 12000, 30, 0.004, 3000, 0.3, 0.1, 0.05), n))  # the stone floor
    thump = flt(rng.standard_normal(int(0.3 * SR)), "lowpass", 190) * np.exp(-secs(0.3) / (0.035 if flat else 0.03))
    place(y, (0.3 if flat else 0.4) * norm(thump), 0.0)
    if v > 0.12:
        place(y, 0.35 * v * chatter(int(0.25 * SR), int(6 + 14 * v), 0.009, 4.0 + 4 * v), 0.012)
    y += grit(n, int(3 + 14 * v), 0.03)
    return norm(y)


def lid_knock(v, s=0.7):
    """The lid (wood with an iron rim) dropping back onto the chest's rim."""
    n = int(s * SR)
    force = contact(0.003 * max(v, 0.05) ** -0.2)
    y = (1.0 * excite(force, modes(200, 4500, 44, 0.035, 250, 0.6, 0.35, s), n)
         + 0.4 * cavity(force, n, 245, 4.5)
         + 0.4 * excite(force, modes(900, 9000, 28, 0.022, 1000, 0.5, 0.18, s), n))
    if v > 0.5:
        place(y, 0.2 * chatter(int(0.15 * SR), 5, 0.008, 2.5, 600, 6000), 0.006)
    return norm(y)


def iron_knock(pitch=1.0, s=0.5, wood=0.45):
    """An iron part (the hasp, a side ring) striking its iron plate on the wooden chest."""
    n = int(s * SR)
    force = contact(0.0013, 0.5)
    y = (excite(force, modes(800 * pitch, 9000 * pitch, 28, 0.06, 1000, 0.45, 0.18, s), n)
         + 0.75 * wood * excite(force, modes(250, 3000, 20, 0.028, 300, 0.6, 0.4, s), n) + 0.2 * wood * cavity(force, n))
    return norm(y)


def scrape(s, rate, steel_tau=0.004, band=(1500, 9000), env_pow=0.5):
    steel = modes(band[0], band[1], 24, steel_tau, 2500, 0.3, 0.1, 0.05)
    imp = np.zeros(int(s * SR))
    tc = 0.0
    while tc < s:
        u = tc / s
        imp[int(tc * SR)] += rng.uniform(0.3, 1.0) * np.sin(np.pi * u) ** env_pow
        tc += 1.0 / (rate * rng.uniform(0.5, 1.5))
    return norm(fit(fftconvolve(imp, steel), len(imp) + int(0.03 * SR)))


# ------------------------------------------------------------------ the hall
C = 343.0
ROOM = dict(x=(-4.2, 4.2), y=(-3.8, 11.3), z=(0.0, 7.0))
REFL = dict(x=(0.7, 0.7), y=(0.55, 0.6), z=(0.85, 0.7))     # how much each surface sends back (low side, high side)
EARS = [(-0.09, -1.81, 0.25), (0.09, -1.81, 0.25)]        # the camera while the chest is shut (scene units (0, -14.24, 0.62))


def hall(src, drr_db=0.0, s=1.6):
    """Impulse responses (left, right) from a point in the hall to the camera: the direct sound, the first echoes from
    each surface at their true delays (images up to three bounces), and the long stone tail. The direct path has gain 1."""
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
                    t = (d - d0) / C + 0.002                    # everything 2 ms late so nothing comes before the direct sound
                    i = t * SR
                    k0 = int(i)
                    if k0 + 2 >= len(ir):
                        continue
                    fr = i - k0
                    target = ir if order == 0 else early
                    target[k0] += g * d0 / d * (1 - fr)
                    target[k0 + 1] += g * d0 / d * fr
        early = flt(early, "lowpass", 7000)                     # stone scatters the highs a little at each bounce
        tt = secs(s)
        nz = tail_seed[e_i]
        tail = (flt(nz, "lowpass", 500) * np.exp(-6.91 * tt / 1.3) + flt(nz, "bandpass", [500, 3000]) * np.exp(-6.91 * tt / 1.2)
                + flt(nz, "highpass", 3000) * np.exp(-6.91 * tt / 0.7))
        tail *= np.clip((tt - 0.03) / 0.05, 0, 1)
        tail *= math.sqrt(db(drr_db) / max((tail ** 2).sum(), 1e-12))   # its energy against the direct sound's (1)
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


CHEST = Spot("chest", (0.0, 0.0, 2.0), -7.0)
RINGL = Spot("ring_left", (-2.9, 0.0, 2.0), -7.0)
RINGR = Spot("ring_right", (2.9, 0.0, 2.0), -7.0)
SANDL = Spot("sand_left", (-10.0, 36.0, 0.0), 2.0)
SANDR = Spot("sand_right", (11.5, 47.0, 0.0), 3.0)
SPOTS = (CHEST, RINGL, RINGR, SANDL, SANDR)

# ------------------------------------------------------------------ the landing (measured in the scene)
LAND = [(44.6, 1.00, False, "chest lands on its left corner"), (49.6, 0.51, True, "the right side comes down flat"),
        (60.1, 0.18, True, "it rocks back and the left side comes down"), (61.9, 0.05, False, "a last small settle")]
for fr, v, flat, lab in LAND:
    # the flat landing's low end builds up in the room more than the corner's: it is set 2 dB under its speed's level
    # with the deep thump mostly gone the flat landing no longer builds up in the room: it gets 4 dB back, so the
    # second thud stays clearly there (the owner's note on the second try)
    CHEST.add(chest_hit(v, flat), fr, -4.0 + 20 * math.log10(v) + (4.0 if flat else 0.0), label=lab)
for k, (fr, g) in enumerate([(46.0, -18), (50.0, -20), (53.5, -24), (58.5, -27), (64.5, -31), (72.5, -35)]):
    RINGL.add(iron_knock(1.3), fr + rng.uniform(0, 1.2), g + 3 + rng.uniform(-2, 1), label="side rings swing back against their mounts" if k == 0 else None)
    RINGR.add(iron_knock(1.25), fr + rng.uniform(0.3, 1.6), g + 3 + rng.uniform(-2, 1))

# ------------------------------------------------------------------ the sand from the vault ("the smoke that comes down")
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
def smooth(x, a, b):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def bump(k, a, b, amp):
    return amp * math.sin(math.pi * (k - a) / (b - a)) ** 2 if a <= k <= b else 0.0


STRONG, RATTLE = (2.0, 2.0, 3.0), 30


def rattle(k, kind):
    """Copied from tools/v12_render.py (the motion the video shows)."""
    z = dict(lid=0.0, roll=0.0, yaw=0.0, hop=0.0, hasp=0.0, ring=0.0)
    if k >= RATTLE:
        return z
    w = 1.0 - smooth(k, RATTLE - 8, RATTLE - 1)
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
    for part in ("lid", "hop"):                         # these rest at zero and drop back onto it
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


ALL = {kind: contacts(kind) for kind in (0, 1, 2)}
REF = {}
for kind, cs in ALL.items():                          # reference speeds: the strongest of each part across the three rattles
    for k, part, v in cs:
        base = part.split("_")[0]
        REF[base] = max(REF.get(base, 0), v)
EDGE = 2.78                                            # half the chest's width (units): a roll of one degree lifts an edge this much * pi/180


def lvl(base_db, v, ref):
    return base_db + max(-30.0, 20 * math.log10(max(v, 1e-6) / ref))


KIND_DB = {0: 13.0, 1: 1.0, 2: -4.0}                  # so the three rattles are about equally noticeable (the first moves slowest)
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
            edge_v = EDGE * math.radians(v)
            CHEST.add(chest_hit(0.07, False), fr, lvl(-17, v, REF["roll"]) + KIND_DB[kind], label=lab if first else None)
        elif part == "yaw":
            CHEST.add(scrape(0.18, 260, 0.006, (500, 6000), 1.0) * 0.7, fr - 2, lvl(-24, v, REF["yaw"]) + KIND_DB[kind])
        elif part.startswith("hasp"):
            CHEST.add(iron_knock(1.7, 0.4, 0.6), fr, lvl(-17, v, REF["hasp"]) + KIND_DB[kind])
        elif part.startswith("ring"):
            CHEST.add(iron_knock(1.3), fr + 0.5, lvl(-22, v, REF["ring"]) + KIND_DB[kind])
            CHEST.add(iron_knock(1.25), fr + 1.2, lvl(-24, v, REF["ring"]) + KIND_DB[kind])
        first = False

# ------------------------------------------------------------------ the chest opening (as the second try, with the hollow box)
CHEST.add(scrape(0.16, 520), 349, -20, label="bolt slides back")
n = int(0.4 * SR)
clk = np.zeros(n)
for dt, a, d in ((0.0, 1.0, 0.0009), (0.011, 0.8, 0.0007)):
    f_ = contact(d, 0.6)
    part = excite(f_, modes(1800, 11000, 30, 0.02, 3000, 0.45, 0.15, 0.4), n) + 0.55 * excite(f_, modes(150, 2600, 30, 0.035, 300, 0.6, 0.4, 0.4), n) \
        + 0.35 * cavity(f_, n)
    place(clk, a * part, dt)
CHEST.add(norm(clk), 355, -3, label="lock clicks open")
CHEST.add(scrape(0.11, 160, 0.003, (1200, 7000)), 365, -24, label="clasp lifts")
n = int(0.6 * SR)
cl = np.zeros(n)
for dt, a in ((0.0, 1.0), (0.047, 0.32), (0.082, 0.1)):
    place(cl, a * iron_knock(1.1, 0.6, 0.6), dt)
CHEST.add(norm(cl), 373, -6, label="clasp drops against the chest")
T = (416 - 389) / FPS
imp = np.zeros(int(T * SR))
burst = flt(rng.standard_normal(int(T * SR)), "lowpass", 6)
burst = np.clip((burst - np.percentile(burst, 35)) / (np.percentile(burst, 95) - np.percentile(burst, 35)), 0, 1)
tc = 0.0
while tc < T:
    u = tc / T
    i = int(tc * SR)
    imp[i] += burst[i] * np.sin(np.pi * min(u * 1.1, 1.0)) ** 0.5 * rng.uniform(0.4, 1.0)
    tc += 1.0 / ((32 + 55 * burst[i]) * rng.uniform(0.7, 1.3))
hinge = modes(1500, 8500, 26, 0.008, 2000, 0.4, 0.12, 0.15)
lidw = modes(180, 3200, 40, 0.03, 250, 0.6, 0.4, 0.25)
cr = norm(fit(fftconvolve(imp, 0.45 * hinge), len(imp))) + norm(fit(fftconvolve(imp, lidw), len(imp))) + 0.2 * cavity(imp, len(imp), 235, 3.0)
cr += 0.12 * norm(flt(rng.standard_normal(len(imp)), "bandpass", [600, 3500])) * burst
CHEST.add(norm(cr), 389, -13, label="lid creaks open")
CHEST.add(lid_knock(0.6), 416, -7, label="lid stops, fully open")

# ------------------------------------------------------------------ mix
L, R = np.zeros(N), np.zeros(N)
stems = {}
for sp in SPOTS:
    l, r = sp.render()
    stems[sp.name] = (l, r)
    L += l
    R += r
L, R = flt(L, "highpass", 75), flt(R, "highpass", 75)
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
                     ("lock and clasp (11.6 to 12.9 s)", 11.6, 12.9), ("lid (12.9 to 14.2 s)", 12.9, 14.2)):
    seg = m[int(a_ * SR):int(b_ * SR)]
    print(f"{name:34s} loudness {20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12):6.1f} dB   peak {20 * np.log10(np.abs(seg).max() + 1e-12):6.1f} dB")
for kind in (0, 1, 2):
    print("rattle", kind, "contacts:", ", ".join(f"{p} {k:.1f}" for k, p, v in ALL[kind]))
print("cues", len(CUES))
