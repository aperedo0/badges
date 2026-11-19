"""Planar rigid body drop of the chest (real physics, impulse based), plain Python:
    python3 rigid2d.py OUT.json [key=value ...]

The chest is a rigid box seen from the front: the boot footprint half width B = 2.775, centre of mass
2.15 above the boot bottoms, height 5.0. It falls under gravity and touches the floor with its two
bottom edges. Every contact is resolved with Newton's impact law (coefficient of restitution e on
the approach speed) and Coulomb friction (mu), using the true effective mass at the corner (mass and
rotational inertia together). Small approach speeds get no bounce (resting contact).

Scale: the chest is about 0.7 m wide, so 1 unit = 0.126 m and real gravity is 77.9 units/s^2.
Output uses Blender's convention: roll is the rotation about the chest's +y axis (negative roll
lowers the -x end). Samples at 120 per second; impacts list time, edge (-1 or +1) and speed."""
import json, math, sys

P = dict(g=77.9, drop=13.0, roll=-16.0, w0=0.0, vx0=0.0, e=0.35, mu=0.6, com=2.15, width=5.55,
         height=5.0, seconds=3.0, dt=2e-5, rate=120, vthr=1.5)
for kv in sys.argv[2:]:
    k, v = kv.split("=")
    P[k] = float(v)
B = P["width"] / 2
h = P["com"]
m = 1.0
I = m * (P["width"] ** 2 + P["height"] ** 2) / 12.0 + m * (P["height"] / 2 - h) ** 2

# state: COM position (x, z), angle th (2D, counter clockwise; th = -roll), velocities
th = -math.radians(P["roll"])
c, s = math.cos(th), math.sin(th)


def corner(sx, x, z, th):
    c, s = math.cos(th), math.sin(th)
    rx, rz = c * (sx * B) - s * (-h), s * (sx * B) + c * (-h)
    return rx, rz, x + rx, z + rz


low = min(corner(sx, 0, 0, th)[3] for sx in (-1, 1))
x, z = 0.0, P["drop"] - low
vx, vz, w = P["vx0"], 0.0, P["w0"]
g, e, mu, dt = P["g"], P["e"], P["mu"], P["dt"]
out_every = int(round(1.0 / P["rate"] / dt))
samples, impacts = [], []
n = int(P["seconds"] / dt)
last_imp = {-1: -1.0, 1: -1.0}
for i in range(n + 1):
    t = i * dt
    if i % out_every == 0:
        roll = -th
        samples.append({"t": t, "loc": [x, 0.0, z], "quat": [math.cos(roll / 2), 0.0, math.sin(roll / 2), 0.0]})
    # free flight
    vz -= g * dt
    # contacts: sequential impulses over the touching corners
    touching = []
    for sx in (-1, 1):
        rx, rz, cx, cz = corner(sx, x, z, th)
        if cz <= 0.0:
            touching.append((sx, rx, rz, cz))
    if touching:
        # restitution targets from the approach speed before any impulse this step
        target = {}
        for sx, rx, rz, cz in touching:
            vn = vz + w * rx
            if vn < -P["vthr"]:
                target[sx] = -e * vn
                if t - last_imp[sx] > 0.02:
                    impacts.append({"t": t, "edge": sx, "speed": -vn})
                elif impacts and impacts[-1]["edge"] == sx:
                    impacts[-1]["speed"] = max(impacts[-1]["speed"], -vn)
                last_imp[sx] = t
            else:
                target[sx] = 0.0
        jn_acc = {sx: 0.0 for sx, *_ in touching}
        jt_acc = {sx: 0.0 for sx, *_ in touching}
        for it in range(12):
            for sx, rx, rz, cz in touching:
                vn = vz + w * rx
                kn = 1 / m + rx * rx / I
                jn = (target[sx] - vn) / kn
                old = jn_acc[sx]
                jn_acc[sx] = max(0.0, old + jn)
                jn = jn_acc[sx] - old
                vz += jn / m
                w += rx * jn / I
                vt = vx - w * rz
                kt = 1 / m + rz * rz / I
                jt = -vt / kt
                oldt = jt_acc[sx]
                lim = mu * jn_acc[sx]
                jt_acc[sx] = max(-lim, min(lim, oldt + jt))
                jt = jt_acc[sx] - oldt
                vx += jt / m
                w += -rz * jt / I
        # push out of the floor (position only, no energy added)
        pen = max(-cz for sx, rx, rz, cz in touching)
        if pen > 0:
            z += pen
    x += vx * dt
    z += vz * dt
    th += w * dt

json.dump({"params": P, "frames": samples, "impacts": impacts}, open(sys.argv[1], "w"))
print("IMPACTS", [(round(im["t"], 3), im["edge"], round(im["speed"], 1)) for im in impacts])
print("FINAL x=%.3f z=%.3f roll=%.3f deg" % (x, z, math.degrees(-th)))
