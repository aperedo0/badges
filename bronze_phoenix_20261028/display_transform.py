"""Forward and inverse of the app's AgX view transform (same cube and shaper as the finish shader)."""
import numpy as np
cube = np.frombuffer(open(__import__('pathlib').Path(__file__).resolve().parent/'agx_cube.bin','rb').read(), dtype=np.float16).astype(float).reshape(65, 65, 65, 4)  # [b][g][r]
LO, HI = -12.47393, 12.5260688117
def agx(lin):
    """Forward AgX for an (...,3) linear color, trilinear in the cube like the shader."""
    s = np.clip((np.log2(np.maximum(lin, 2.0 ** LO)) - LO) / (HI - LO), 0, 1) * 64
    i0 = np.clip(np.floor(s).astype(int), 0, 63); f = s - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]; fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
    out = 0
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (fr if dr else 1 - fr) * (fg if dg else 1 - fg) * (fb if db else 1 - fb)
                out = out + w * cube[b0 + db, g0 + dg, r0 + dr, :3]
    return out
grid = 2.0 ** np.linspace(-12, 8, 4000)
grey_disp = agx(np.repeat(grid[:, None], 3, axis=1))
def agx_inv(disp):
    """Inverse per channel along the grey axis (silver is near neutral)."""
    res = np.empty_like(disp)
    for c in range(3):
        res[..., c] = np.interp(disp[..., c], grey_disp[:, c], grid)
    return res
def refine(lin_guess, disp_target, steps=6):
    """Newton style per channel correction with the full 3D transform."""
    lin = lin_guess.copy()
    for _ in range(steps):
        d = agx(lin); err = disp_target - d
        h = lin * 0.01 + 1e-6
        for c in range(3):
            l2 = lin.copy(); l2[..., c] += h[..., c]
            slope = (agx(l2)[..., c] - d[..., c]) / h[..., c]
            lin[..., c] = np.maximum(lin[..., c] + err[..., c] / np.maximum(slope, 1e-6), 1e-6)
    return lin
