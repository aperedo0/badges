"""Match relief materials to the references under measured Home illumination.

The casing is excluded completely. Each relief role has its own atlas, so
hidden layers never inherit the color of an overlapping object.
"""
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, distance_transform_edt, maximum_filter, map_coordinates

ROOT = Path(__file__).resolve().parent
TEMP = Path('/tmp/star_island_20261016')
sys.path.insert(0, str(ROOT.parent / 'botanical_match_20261014'))
from solve import inverse, encode, sample, CAM_POS, F, R, U

SIZE = 512


def project(points):
    p = np.asarray(points) * .96 + [0, -.1206 + .56, 0]
    d = p - CAM_POS
    depth = d @ F
    master = np.stack([540 + 2250 * (d @ R) / depth,
                       720 - 2250 * (d @ U) / depth], -1)
    return master * 47 / 60 + [180, 70]


def fill(image, valid, rounds=16):
    assert valid.any()
    _, (y, x) = distance_transform_edt(~valid, return_indices=True)
    out = image[y, x].copy()
    for _ in range(rounds):
        smooth = gaussian_filter(out, (1, 1, 0))
        out[~valid] = smooth[~valid]
    return out


def raster(name):
    meta = json.loads((ROOT / name / 'design.json').read_text())
    geometry = np.load(TEMP / (name + '_geometry.npz'))
    layers = {}
    for i, group in enumerate(meta['groups']):
        role = group['role']
        layer = layers.setdefault(role, {'cover': np.zeros((SIZE, SIZE), bool),
                                         'pos': np.zeros((SIZE, SIZE, 3))})
        cover, pos = layer['cover'], layer['pos']
        for tri in geometry[str(i) + '_points'][geometry[str(i) + '_triangles']]:
            uv = (tri[:, :2] + 3.015) / 6.03
            px = np.c_[uv[:, 0] * SIZE - .5, (1 - uv[:, 1]) * SIZE - .5]
            lo = np.maximum(np.floor(px.min(0)).astype(int), 0)
            hi = np.minimum(np.ceil(px.max(0)).astype(int), SIZE - 1)
            gx, gy = np.meshgrid(np.arange(lo[0], hi[0] + 1), np.arange(lo[1], hi[1] + 1))
            e1, e2 = px[1] - px[0], px[2] - px[0]
            den = e1[0] * e2[1] - e1[1] * e2[0]
            if abs(den) < 1e-9:
                continue
            a = ((gx-px[0,0])*e2[1] - (gy-px[0,1])*e2[0]) / den
            b = (e1[0]*(gy-px[0,1]) - e1[1]*(gx-px[0,0])) / den
            inside = (a >= -1e-4) & (b >= -1e-4) & (a+b <= 1.0001)
            if not inside.any():
                continue
            x, y = gx[inside], gy[inside]
            p = (1-a[inside]-b[inside])[:,None]*tri[0] + a[inside,None]*tri[1] + b[inside,None]*tri[2]
            take = (~cover[y,x]) | (p[:,2] >= pos[y,x,2])
            x,y,p = x[take],y[take],p[take]
            cover[y,x] = True
            pos[y,x] = p
    return layers


def solve(name, only_role=None):
    layers = raster(name)
    reference = np.asarray(Image.open(ROOT/'references'/(name+'.png')).convert('RGB'), float)/255
    reference = gaussian_filter(reference, (1.2,1.2,0))
    calibration = np.asarray(Image.open(TEMP/(name+'_calibration.png')).convert('RGB'), float)/255
    yy,xx = np.indices((SIZE,SIZE))
    wx = (xx+.5)/SIZE*6.03-3.015
    wy = 3.015-(yy+.5)/SIZE*6.03
    cx,cy,scale = (625,625,566/3.015) if name=='star_ascent' else (626,613,485/2.42)
    target = sample(reference,cx+wx*scale,cy-wy*scale)
    z = np.full((SIZE,SIZE),-100.)
    for layer in layers.values():
        mask = layer['cover']
        z[mask] = np.maximum(z[mask],layer['pos'][mask,2])
    out = ROOT/name/'textures'
    out.mkdir(exist_ok=True)
    for role,layer in layers.items():
        if only_role is not None and role!=only_role:
            continue
        cover,pos = layer['cover'],layer['pos']
        visible = cover & (pos[:,:,2] >= z-.002)
        r,g,b = np.moveaxis(target,-1,0)
        valid = visible.copy()
        if role in ['silver','cloud']:
            valid &= (np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b]) < .19) & (g > .17)
        elif role=='gold':
            valid &= (r > g*1.05) & (g > b*1.4) & (g > .20)
        elif role=='leaf':
            valid &= (g > r*1.4) & (g > b*1.1) & (r < .30)
        elif role=='sea':
            valid &= (g > r*1.4) & (b > r*1.3)
        elif role=='sky':
            valid &= (r > g*1.15) & ((b > g*1.05) | (wy < -.2))
        elif role=='sun':
            valid &= (r > .50) & (g > .15) & (g > b*1.4)
        else:
            # A subtly textured charcoal backing, never a copy of the relief.
            valid &= (np.max(target,axis=-1) < .23)
        if valid.sum()<8:
            valid = visible
        role_target = fill(target,valid,24)
        # The sky is an intrinsic sunset gradient, not reflected light.
        # Row medians remove the palms and give hidden areas the same sky.
        if role=='sky':
            row_color=np.full((SIZE,3),np.nan)
            for row in range(SIZE):
                if valid[row].sum()>6:row_color[row]=np.median(target[row,valid[row]],axis=0)
            good=np.isfinite(row_color[:,0])
            for c in range(3):row_color[:,c]=np.interp(np.arange(SIZE),np.flatnonzero(good),row_color[good,c])
            row_color=gaussian_filter(row_color,(6,0))
            role_target=np.repeat(row_color[:,None,:],SIZE,axis=1)
        screen = project(pos[cover])
        observed = sample(calibration,screen[:,0]-.5,screen[:,1]-.5)
        light = np.zeros((SIZE,SIZE,3))
        light[cover] = np.clip(inverse(observed)/.15,.003,120.)
        dist = distance_transform_edt(visible)
        threshold = np.clip(maximum_filter(dist,size=11)*.6,.8,3.2)
        inner = visible & (dist >= threshold)
        if inner.sum()<8:
            inner=visible
        light=fill(light,inner,16)
        distance=distance_transform_edt(cover)
        border=cover & (distance < np.clip(maximum_filter(distance,size=11)*.6,.8,3.2))
        continued=fill(role_target,cover & ~border,18)
        role_target[border]=continued[border]
        desired=inverse(np.clip(role_target[cover],.006,.92))
        color=np.zeros((SIZE,SIZE,3));glow=color.copy()
        color[cover]=np.clip(desired/light[cover],0,1)
        # Only colored enamel may fill unreachable saturated light. Metal
        # remains entirely reflective, including the complete existing rim.
        if role in ['sky','sea','sun','leaf']:
            glow[cover]=np.clip(desired-color[cover]*light[cover],0,4)/4
        color=fill(color,cover,8);glow=fill(glow,cover,8)
        if role=='sky':
            # Strong studio exposure otherwise compresses a dark saturated
            # sky into only a few8bit codes. Normalize each linear channel
            # and restore its scale in the USD texture node, not in lighting.
            color_scale=np.maximum(color.max(axis=(0,1)),1e-6)
            physical_glow=glow*4
            glow_scale=np.maximum(physical_glow.max(axis=(0,1)),1e-6)
            scales_path=ROOT/name/'texture_scales.json'
            scales=json.loads(scales_path.read_text()) if scales_path.exists() else {}
            scales[role]={'color':color_scale.tolist(),'emission':glow_scale.tolist()}
            scales_path.write_text(json.dumps(scales,indent=2)+'\n')
            color=color/color_scale
            glow=physical_glow/glow_scale
        Image.fromarray(encode(color)).save(out/(role+'_color.png'))
        if role in ['sky','sea','sun','leaf']:
            Image.fromarray(encode(glow)).save(out/(role+'_emission.png'))
        print(name,role,'fitted',int(cover.sum()),'texels',flush=True)


if __name__=='__main__':
    for name in sys.argv[1:]:
        solve(name)
