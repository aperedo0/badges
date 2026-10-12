"""Invert the actual coupled RGB AgX cube; neutral-axis inversion diverges on blue."""
import numpy as np
from scipy.spatial import cKDTree
from agx import agx, cube, LO, HI

_tree = cKDTree(cube[..., :3].reshape(-1, 3))

def inverse(display):
    shape = display.shape
    target = display.reshape(-1, 3)
    _, index = _tree.query(target)
    b, g, r = np.unravel_index(index, (65, 65, 65))
    log = LO + np.stack([r, g, b], -1) / 64 * (HI - LO)
    for _ in range(7):
        linear = np.exp2(log)
        current = agx(linear)
        error = target - current
        jac = np.empty((len(target), 3, 3))
        for c in range(3):
            shifted = log.copy()
            shifted[:, c] += .025
            jac[:, :, c] = (agx(np.exp2(shifted)) - current) / .025
        jt = jac.transpose(0, 2, 1)
        delta = np.linalg.solve(jt @ jac + np.eye(3) * 1e-7,
                                (jt @ error[..., None])).squeeze(-1)
        delta = np.clip(delta, -1, 1)
        old_loss = np.sum(error ** 2, axis=1)
        accepted = np.zeros(len(target), bool)
        for step in [1., .5, .25, .125]:
            trial = np.clip(log + delta * step, LO, HI)
            loss = np.sum((agx(np.exp2(trial)) - target) ** 2, axis=1)
            use = ~accepted & (loss < old_loss)
            log[use] = trial[use]
            accepted |= use
    return np.exp2(log).reshape(shape)
