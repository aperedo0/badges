"""Version 7 landing dust, step 1: where, when and how fast the air under the landing chest leaves,
and how much floor dust it carries (owner, 2026-11-18: when the left side hits the floor, dust must
come up from that location and follow real dust physics). Plan, audited twice:
badges/plans/chest_dust_physics_20261118.md.

Run with Blender's Python (it has numpy):
  /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 tools/v7_squeeze.py [MAPDIR]
Writes physics/dust_sources.json, read by tools/v7_dust.py. MAPDIR gets top down source maps.

Physics:
- Landing: rigid2d.py rerun with the parameters of physics/landing.json at 2400 samples per second
  (the Blender keys are 120 per second, too coarse for the gap), checked against its five impacts.
- Air under the chest: inertial (gap Reynolds number about 11,000), so the inviscid depth averaged
  mass balance div(h grad phi) = dh/dt, air velocity u = -grad phi, on a 0.05 grid over the footprint.
  phi = 0 on the real perimeter (the four gaps between the boots and any lifted boot sole); walls only
  where a boot sole touches the floor. Gaps that open draw air in (no dust from inflow edges).
- Floor dust: an even light layer that is used up. Fine cohesive dust lifts where the air over the
  floor is faster than about 16 units/s (2 m/s): rate k (u^2 - ut^2). Under the chest the air is far
  faster, so all of it goes and is carried to the opening its air leaves by. Outside, the air leaves
  as a wall jet along the floor, decaying as sqrt(h / (h + s)), lifting dust out to 2 units.
- Impact blast: the boots that hit throw out the dust under and around them, a share set by the
  impact's energy, at 0.4 of the impact speed.
- Emission: per opening segment, the jet's impulse is re-emitted from a thicker emitter as a burst of
  up to 5 frames at no more than 80 units/s (the gas grid cannot carry 200 units/s jets); the dust
  goes out with it."""
import json, math, os, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPDIR = sys.argv[1] if len(sys.argv) > 1 else None

# ---------------------------------------------------------------- landing at 2400 per second
LJ = json.load(open(ROOT + "/physics/landing.json"))
P = LJ["params"]
EV = json.load(open(ROOT + "/physics/landing_events.json"))
assert abs(EV["T0"]) < 1e-9, "the mapping below assumes frame 1 shows simulation time 0"
RATE = 2400
tmp = tempfile.mktemp(suffix=".json")
subprocess.run([sys.executable, ROOT + "/tools/rigid2d.py", tmp]
               + [f"{k}={P[k]}" for k in ("g", "drop", "roll", "w0", "vx0", "e", "mu", "com", "width", "height", "seconds")]
               + [f"rate={RATE}"], check=True, capture_output=True)
HR = json.load(open(tmp))
os.remove(tmp)
for a, b in zip(HR["impacts"], LJ["impacts"]):
    assert a["edge"] == b["edge"] and abs(a["t"] - b["t"]) < 1e-4 and abs(a["speed"] / b["speed"] - 1) < 0.01, (a, b)
H, DX, G = P["com"], EV["DX"], P["g"]
fr = HR["frames"]
T = np.array([f["t"] for f in fr])
ROLL = np.array([2 * math.atan2(f["quat"][2], f["quat"][0]) for f in fr])
BX = np.array([f["loc"][0] + DX for f in fr]) - H * np.sin(ROLL)
BZ = np.array([f["loc"][2] for f in fr]) - H * np.cos(ROLL)
FPS = 30.0


def frame_of(t):
    return 1.0 + t * FPS


def idx(t):
    return int(round(t * RATE))


# ---------------------------------------------------------------- chest underside (chest frame)
B, D = 2.775, 1.865            # boot footprint half width and half depth
XB, YB = 1.887, 0.85           # boots are |x| >= XB and |y| >= YB
ZB = 0.237                     # body underside above the boot soles
DXC = 0.05
NX = int(round(2 * B / DXC))
NY = 75
DYC = 2 * D / NY
xs = -B + DXC * (np.arange(NX) + 0.5)
ys = -D + DYC * (np.arange(NY) + 0.5)
Xc, Yc = np.meshgrid(xs, ys, indexing="ij")
BOOT = (np.abs(Xc) >= XB) & (np.abs(Yc) >= YB)
ZC = np.where(BOOT, 0.0, ZB)
HWALL = 0.002


def gap(i):
    r = ROLL[i]
    return BZ[i] - Xc * math.sin(r) + ZC * math.cos(r)


# ---------------------------------------------------------------- the air solve
def solve(h, dhdt):
    """A phi = -dh/dt with A = -div(h grad) on fluid cells; phi = 0 outside the footprint."""
    # thin layer of air (the film) only where the gap is under HFILM; deeper parts are open air that
    # the gas grid resolves (phi = 0 there), touching soles are walls
    fl = (h > HWALL) & (h < HFILM)
    op = h >= HFILM
    hh = np.where(fl, h, 0.0)
    ce = np.zeros((NX + 1, NY)); cn = np.zeros((NX, NY + 1))
    both = fl[:-1, :] & fl[1:, :]
    to_open = (fl[:-1, :] & op[1:, :]) | (op[:-1, :] & fl[1:, :])
    ce[1:-1, :] = (np.where(both, 0.5 * (hh[:-1, :] + hh[1:, :]), 0.0) + np.where(to_open, hh[:-1, :] + hh[1:, :], 0.0)) / DXC ** 2
    ce[0, :] = 2 * hh[0, :] / DXC ** 2
    ce[-1, :] = 2 * hh[-1, :] / DXC ** 2
    both = fl[:, :-1] & fl[:, 1:]
    to_open = (fl[:, :-1] & op[:, 1:]) | (op[:, :-1] & fl[:, 1:])
    cn[:, 1:-1] = (np.where(both, 0.5 * (hh[:, :-1] + hh[:, 1:]), 0.0) + np.where(to_open, hh[:, :-1] + hh[:, 1:], 0.0)) / DYC ** 2
    cn[:, 0] = 2 * hh[:, 0] / DYC ** 2
    cn[:, -1] = 2 * hh[:, -1] / DYC ** 2
    diag = ce[:-1, :] + ce[1:, :] + cn[:, :-1] + cn[:, 1:]
    diag = np.where(fl, diag, 1.0)

    def A(p):
        p = np.where(fl, p, 0.0)
        q = diag * p
        q[1:, :] -= ce[1:-1, :] * p[:-1, :]
        q[:-1, :] -= ce[1:-1, :] * p[1:, :]
        q[:, 1:] -= cn[:, 1:-1] * p[:, :-1]
        q[:, :-1] -= cn[:, 1:-1] * p[:, 1:]
        return np.where(fl, q, 0.0)

    b = np.where(fl, -dhdt, 0.0)
    x = np.zeros_like(b); r = b - A(x); z = r / diag; p = z.copy(); rz = (r * z).sum()
    bn = math.sqrt((b * b).sum()) + 1e-30
    for it in range(4000):
        Ap = A(p); al = rz / ((p * Ap).sum() + 1e-30)
        x += al * p; r -= al * Ap
        if math.sqrt((r * r).sum()) < 1e-9 * bn:
            break
        z = r / diag; rz2 = (r * z).sum(); p = z + (rz2 / rz) * p; rz = rz2
    phi = np.where(fl, x, 0.0)
    # outward volume flux per boundary cell (units^3/s), per edge
    out = dict(left=hh[0, :] * phi[0, :] / (DXC / 2) * DYC, right=hh[-1, :] * phi[-1, :] / (DXC / 2) * DYC,
               front=hh[:, 0] * phi[:, 0] / (DYC / 2) * DXC, back=hh[:, -1] * phi[:, -1] / (DYC / 2) * DXC)
    # depth averaged air velocity at the cells: u = -grad phi (ghost phi = 0 outside, walls mirror)
    pe = np.pad(phi, 1)
    fe = np.pad(fl, 1)
    right = np.where(fe[2:, 1:-1] | (np.arange(NX)[:, None] == NX - 1), pe[2:, 1:-1], phi)
    left = np.where(fe[:-2, 1:-1] | (np.arange(NX)[:, None] == 0), pe[:-2, 1:-1], phi)
    up = np.where(fe[1:-1, 2:] | (np.arange(NY)[None, :] == NY - 1), pe[1:-1, 2:], phi)
    dn = np.where(fe[1:-1, :-2] | (np.arange(NY)[None, :] == 0), pe[1:-1, :-2], phi)
    gx = (right - left) / (2 * DXC); gy = (up - dn) / (2 * DYC)
    ux, uy = np.where(fl, -gx, 0.0), np.where(fl, -gy, 0.0)
    lost = -(np.where(fl, dhdt, 0.0)).sum() * DXC * DYC
    inner = (ce[1:-1, :] * np.where(op[1:, :], phi[:-1, :], 0) + ce[1:-1, :] * np.where(op[:-1, :], phi[1:, :], 0)).sum() * DXC * DYC \
        + (cn[:, 1:-1] * np.where(op[:, 1:], phi[:, :-1], 0) + cn[:, 1:-1] * np.where(op[:, :-1], phi[:, 1:], 0)).sum() * DXC * DYC
    out["_inner"] = np.array([inner])
    return fl, phi, out, ux, uy, lost, it


# ---------------------------------------------------------------- opening segments
SEGS = []


def add_segs(edge, a0, a1, n, kind):
    for k in range(n):
        s0 = a0 + (a1 - a0) * k / n; s1 = a0 + (a1 - a0) * (k + 1) / n
        SEGS.append(dict(edge=edge, s0=s0, s1=s1, kind=kind))


for edge in ("front", "back"):
    add_segs(edge, -B, -XB, 2, "boot"); add_segs(edge, -XB, XB, 9, "gap"); add_segs(edge, XB, B, 2, "boot")
for edge in ("left", "right"):
    add_segs(edge, -D, -YB, 3, "boot"); add_segs(edge, -YB, YB, 4, "gap"); add_segs(edge, YB, D, 3, "boot")
NORMAL = dict(front=(0.0, -1.0), back=(0.0, 1.0), left=(-1.0, 0.0), right=(1.0, 0.0))
for i, s in enumerate(SEGS):
    s["name"] = f"{s['edge']} {i:02d}"
    along = xs if s["edge"] in ("front", "back") else ys
    s["cells"] = np.where((along >= s["s0"]) & (along < s["s1"]))[0]
    s["L"] = s["s1"] - s["s0"]
    s["side"] = "left" if (s["edge"] == "left" or (s["edge"] in ("front", "back") and 0.5 * (s["s0"] + s["s1"]) < 0)) else "right"
    s["boot_x"] = (-1 if s["edge"] == "left" else 1 if s["edge"] == "right" else int(np.sign(0.5 * (s["s0"] + s["s1"])))) if s["kind"] == "boot" else 0


def seg_point(s):
    """chest frame centre of a segment's opening, on the edge"""
    m = 0.5 * (s["s0"] + s["s1"])
    return dict(front=(m, -D), back=(m, D), left=(-B, m), right=(B, m))[s["edge"]]


# ---------------------------------------------------------------- floor dust map (floor frame = chest home frame)
FX0, FX1, FY0, FY1, FD = -6.0, 6.0, -4.0, 4.0, 0.05
FNX, FNY = int((FX1 - FX0) / FD), int((FY1 - FY0) / FD)
dust = np.ones((FNX, FNY))           # dust per floor cell (1 = the full light layer)
released = np.zeros((FNX, FNY))      # for the maps
UT = 16.0                            # lift threshold of the free stream (units/s): 2 m/s
KP = 10.0 / UT ** 2                  # at twice the threshold a cell is cleared in about a frame


def take(fx, fy, want):
    """remove up to want from the floor cells at (fx, fy); returns what was taken per point"""
    i = np.clip(((fx - FX0) / FD).astype(int), 0, FNX - 1)
    j = np.clip(((fy - FY0) / FD).astype(int), 0, FNY - 1)
    wg = np.zeros_like(dust)
    np.add.at(wg, (i, j), want)               # several points can fall on one floor cell
    gg = np.minimum(dust, wg)
    dust[...] -= gg
    released[...] += gg
    ratio = np.where(wg > 0, gg / np.maximum(wg, 1e-30), 0.0)
    return want * ratio[i, j]


# ---------------------------------------------------------------- run the landing
H_EM, T_EM, UCAP, HOLD = 0.2, 0.2, 80.0, 5   # emitter height and thickness, emitted speed cap, burst frames
HFILM = 0.5  # the thin layer of air under the chest: gaps below this (6 cm); deeper gaps are open air
HRES = 0.5   # gaps above this the gas grid resolves itself (moving collider): dust only, no extra jet (no double count)
SUB = 8
snap = {}
F_START, F_END = 12, 40
nseg = len(SEGS)
nfr = F_END - F_START + 1
IMP = np.zeros((nseg, nfr))          # impulse per density, units^4/s ... (Q * U * dt)
DUST = np.zeros((nseg, nfr))         # dust released into each opening per frame
QMAX = np.zeros(nseg); UMAX = np.zeros(nseg)
QU = np.zeros((nseg, nfr)); QQ = np.zeros((nseg, nfr))   # for the mean exit speed per frame (all gaps)
mass_err, iters, side_dust = 0.0, 0, {}
peak = []
cell_area = FD * FD
for f in range(F_START, F_END + 1):
    if f in (21, 24, 32):
        snap[f] = released.copy()
    for k in range(SUB):
        t = (f - 1 + k / SUB) / FPS
        i = idx(t)
        dt = 1.0 / (FPS * SUB)
        h = gap(i)
        dhdt = (gap(i + 1) - gap(i - 1)) / (2.0 / RATE)
        if h.min() >= HFILM:           # no thin layer of air yet: the grid moves the air itself
            continue
        fl, phi, out, ux, uy, lost, it = solve(h, dhdt)
        iters = max(iters, it)
        tot = sum(v.sum() for v in out.values())   # perimeter plus into open air under the chest
        if abs(lost) > 1e-3:
            mass_err = max(mass_err, abs(tot - lost) / abs(lost))
        r = ROLL[i]
        # under the chest: dust lifted by the air in the gap, carried along the air to its opening
        sp = np.hypot(ux, uy)
        fxc = BX[i] + Xc * math.cos(r)
        want = np.where(fl & (sp > UT), KP * (sp ** 2 - UT ** 2) * dt, 0.0)
        got = take(fxc.ravel(), Yc.ravel(), want.ravel()).reshape(want.shape)
        if got.sum() > 0:
            src = np.argwhere(got > 0)
            px, py = Xc[got > 0].copy(), Yc[got > 0].copy()
            amt = got[got > 0]
            done = np.zeros(len(px), bool)
            for step in range(400):
                ii = np.clip(((px + B) / DXC).astype(int), 0, NX - 1)
                jj = np.clip(((py + D) / DYC).astype(int), 0, NY - 1)
                vx, vy = ux[ii, jj], uy[ii, jj]
                vn = np.hypot(vx, vy) + 1e-9
                px = np.where(done, px, px + vx / vn * 0.7 * DXC)
                py = np.where(done, py, py + vy / vn * 0.7 * DXC)
                done |= (np.abs(px) >= B) | (np.abs(py) >= D) | (vn < 1e-6)
                if done.all():
                    break
            px, py = np.clip(px, -B, B), np.clip(py, -D, D)
            for x, y, a in zip(px, py, amt):
                # nearest outflowing segment to the exit point
                best, bd = None, 1e9
                for si, s in enumerate(SEGS):
                    sx, sy = seg_point(s)
                    d2 = (sx - x) ** 2 + (sy - y) ** 2
                    if d2 < bd:
                        best, bd = si, d2
                if best is not None:
                    DUST[best, f - F_START] += a
        # each opening: jet out along the floor
        for si, s in enumerate(SEGS):
            q = out[s["edge"]][s["cells"]].sum()
            QMAX[si] = max(QMAX[si], q)
            if q <= 0:
                continue                      # air drawn in here: no dust
            if s["edge"] in ("front", "back"):
                he = h[s["cells"], 0 if s["edge"] == "front" else -1]
            else:
                he = h[0 if s["edge"] == "left" else -1, s["cells"]]
            he = max(float(np.mean(np.maximum(he, HWALL))), 0.01)
            U = q / (s["L"] * he)
            UMAX[si] = max(UMAX[si], U)
            QU[si, f - F_START] += q * U * dt; QQ[si, f - F_START] += q * dt
            if he < HRES:
                IMP[si, f - F_START] += q * U * dt
            if U > UT:
                ex, ey = seg_point(s)
                nx, ny = NORMAL[s["edge"]]
                fx0 = BX[i] + ex * math.cos(r)
                ss = np.arange(0.0, 2.0, FD) + FD / 2
                us = U * np.sqrt(he / (he + ss))
                lat = np.arange(s["s0"], s["s1"], FD) + FD / 2 - 0.5 * (s["s0"] + s["s1"])
                SS, LL = np.meshgrid(ss, lat, indexing="ij")
                USS = U * np.sqrt(he / (he + SS))
                if s["edge"] in ("front", "back"):
                    gx_, gy_ = fx0 + LL, ey + ny * SS
                else:
                    gx_, gy_ = fx0 + nx * SS, ey + LL
                want = np.where(USS > UT, KP * (USS ** 2 - UT ** 2) * dt, 0.0)
                DUST[si, f - F_START] += take(gx_.ravel(), gy_.ravel(), want.ravel()).sum()

# ---------------------------------------------------------------- impact blasts at the touching boots
VTOP = LJ["impacts"][0]["speed"]
blasts = []
for im in LJ["impacts"]:
    t, e, v = im["t"], im["edge"], im["speed"]
    f = frame_of(t)
    i = idx(t)
    r = ROLL[i]
    share = min(1.0, (v / VTOP) ** 2)           # energy of this hit relative to the first
    fi = int(math.floor(f)) - F_START
    for sy in (-1, 1):
        x0, x1 = sorted((e * XB, e * B))
        y0, y1 = sorted((sy * YB, sy * D))
        gx_, gy_ = np.meshgrid(np.arange(x0 - 0.3, x1 + 0.3, FD), np.arange(y0 - 0.3, y1 + 0.3, FD), indexing="ij")
        fxp = BX[i] + gx_ * math.cos(r)
        ii = np.clip(((fxp - FX0) / FD).astype(int), 0, FNX - 1); jj = np.clip(((gy_ - FY0) / FD).astype(int), 0, FNY - 1)
        want = dust[ii, jj] * share * 0.8
        got = take(fxp.ravel(), gy_.ravel(), want.ravel())
        amount = float(got.sum())
        segs = [si for si, s in enumerate(SEGS) if s["kind"] == "boot" and s["boot_x"] == e
                and ((s["edge"] in ("left", "right") and s["edge"] == ("left" if e < 0 else "right") and np.sign(0.5 * (s["s0"] + s["s1"])) == sy)
                     or (s["edge"] == ("front" if sy < 0 else "back")))]
        Ltot = sum(SEGS[si]["L"] for si in segs)
        U = 0.4 * v
        for si in segs:
            w = SEGS[si]["L"] / Ltot
            DUST[si, fi] += amount * w
            IMP[si, fi] += SEGS[si]["L"] * H_EM * U * U * (2.0 / FPS)   # a jet at U out of this opening for 2 frames
        blasts.append(dict(frame=round(f, 3), edge=e, boot_y=sy, speed=round(v, 2), dust=round(amount, 4), segments=[SEGS[si]["name"] for si in segs]))

# ---------------------------------------------------------------- re-emit as bursts the gas grid can carry
TF = 1.0 / FPS
keys, lost_imp, dens_max = [], 0.0, 0.0
sched = []
for si, s in enumerate(SEGS):
    A = s["L"] * H_EM
    carry, queue, age = 0.0, 0.0, 0
    rows = []
    for fi in range(nfr):
        if IMP[si, fi] > 0 or DUST[si, fi] > 0:
            age = 0
        avail = IMP[si, fi] + carry
        queue += DUST[si, fi]
        used = min(avail, A * TF * UCAP ** 2)
        U = math.sqrt(used / (A * TF)) if used > 0 else 0.0
        frac = used / avail if avail > 0 else 0.0
        dout = queue * frac
        queue -= dout
        carry = avail - used
        age += 1
        if age > HOLD:
            lost_imp += carry; carry = 0.0; queue = 0.0
        if U <= 0.5 and queue > 0:                 # dust lifted by air the grid moves itself: release it, no jet
            dout += queue; queue = 0.0
        dens = dout / (A * max(U, 4.0) * TF)      # below 4 units/s: the grid's own air carries it out
        dens_max = max(dens_max, dens)
        rows.append((F_START + fi, U, dens))
    sched.append(rows)
SCALE = 1.0 / dens_max if dens_max > 0 else 1.0
TOTAL_IMP = IMP.sum()
for si, s in enumerate(SEGS):
    ex, ey = seg_point(s)
    nx, ny = NORMAL[s["edge"]]
    if s["edge"] in ("front", "back"):
        box = (s["s0"], s["s1"], ey + ny * 0.05, ey + ny * (0.05 + T_EM))
    else:
        box = (ex + nx * 0.05, ex + nx * (0.05 + T_EM), s["s0"], s["s1"])
    box = (min(box[0], box[1]), max(box[0], box[1]), min(box[2], box[3]), max(box[2], box[3]), 0.0, H_EM)
    k = []
    for (f, U, dens) in sched[si]:
        i = idx((f - 1) / FPS)
        fi = f - F_START
        air = min(UCAP, QU[si, fi] / QQ[si, fi]) if QQ[si, fi] > 0 else 0.0   # the air's own exit speed this frame
        k.append(dict(frame=f, speed=round(U, 3), jet=U > 0.5, air_speed=round(air, 3), density=round(min(1.0, dens * SCALE), 4), roll=round(ROLL[i], 5)))
    keys.append(dict(name=s["name"], edge=s["edge"], kind=s["kind"], side=s["side"], normal=NORMAL[s["edge"]], box=box, keys=k,
                     peak_exit_speed=round(UMAX[si], 1), dust=round(float(DUST[si].sum()), 4)))

# ---------------------------------------------------------------- checks and logs
per_frame = {}
for fi in range(nfr):
    l = sum(DUST[si, fi] for si, s in enumerate(SEGS) if s["side"] == "left")
    rr = sum(DUST[si, fi] for si, s in enumerate(SEGS) if s["side"] == "right")
    per_frame[F_START + fi] = (round(l, 4), round(rr, 4))
right_start = next((f for f, (l, rr) in per_frame.items() if rr > 0.02 * max(1e-9, max(v[1] for v in per_frame.values()))), None)
capped = sum(1 for rows in sched for (_, U, _) in rows if U >= UCAP - 1e-6)
log = dict(mass_error_max=round(mass_err, 4), cg_iterations_max=iters, emitted_speed_cap=UCAP, frames_at_cap=capped,
           impulse_dropped_fraction=round(lost_imp / TOTAL_IMP, 4) if TOTAL_IMP else 0.0,
           peak_exit_speed_left=round(max(UMAX[si] for si, s in enumerate(SEGS) if s["side"] == "left"), 1),
           peak_exit_speed_right=round(max(UMAX[si] for si, s in enumerate(SEGS) if s["side"] == "right"), 1),
           dust_left_right_per_frame=per_frame, right_side_start_frame=right_start, blasts=blasts,
           floor_dust_left=round(float(dust.mean()), 4))
json.dump(dict(plan="badges/plans/chest_dust_physics_20261118.md", emitter=dict(height=H_EM, thickness=T_EM, density_scale=SCALE),
               segments=keys, impacts=[dict(frame=round(frame_of(im["t"]), 3), edge=im["edge"], speed=im["speed"]) for im in LJ["impacts"]],
               log=log), open(ROOT + "/physics/dust_sources.json", "w"), indent=1)
print(json.dumps(log, indent=1))

# ---------------------------------------------------------------- top down source map (floor frame, x right, y up)
if MAPDIR:
    os.makedirs(MAPDIR, exist_ok=True)
    snap[41] = released.copy()
    stages = [(21, None), (24, 21), (32, 24), (41, 32)]
    vmax = max((snap[k] - (snap[j] if j else 0)).max() for k, j in stages)
    for k, j in stages:
        stage = snap[k] - (snap[j] if j else 0)
        img = np.zeros((FNY, FNX, 3))
        v = np.sqrt(stage.T[::-1, :] / (vmax + 1e-12))
        img[..., 0] = np.clip(v * 3, 0, 1); img[..., 1] = np.clip(v * 3 - 1, 0, 1); img[..., 2] = np.clip(v * 3 - 2, 0, 1)
        # the chest at rest (white outline); the camera side (front, -y) is at the bottom
        for xx in np.arange(-B, B, FD):
            for yy in (-D, D):
                img[FNY - 1 - int((yy - FY0) / FD), int((xx - FX0) / FD)] = 1
        for yy in np.arange(-D, D, FD):
            for xx in (-B, B):
                img[FNY - 1 - int((yy - FY0) / FD), min(FNX - 1, int((xx - FX0) / FD))] = 1
        p = os.path.join(MAPDIR, f"released_until_{k}.ppm")
        with open(p, "wb") as fh:
            fh.write(b"P6 %d %d 255\n" % (FNX, FNY)); fh.write((img * 255).astype(np.uint8).tobytes())
        print("map", p)
