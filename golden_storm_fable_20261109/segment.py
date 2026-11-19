"""Split the owner's mockup into its parts: outline, blue enamel, pearl clouds and gold.

Colors only decide which part a pixel belongs to. Every edge is smoothed afterwards,
so the geometry never follows single pixels.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

R = Path(__file__).resolve().parent
im = np.asarray(Image.open(R / 'reference/mockup.png').convert('RGB')).astype(float) / 255
H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
mx, mn = im.max(2), im.min(2)
sat = (mx - mn) / np.maximum(mx, 1e-6)


def disk(n):
    y, x = np.mgrid[-n:n + 1, -n:n + 1]
    return x * x + y * y <= n * n + .5


def largest(m):
    lab, n = ndi.label(m)
    if n == 0:
        return m
    s = np.bincount(lab.ravel()); s[0] = 0
    return lab == s.argmax()


def drop_small(m, area):
    lab, n = ndi.label(m)
    s = np.bincount(lab.ravel())
    keep = s >= area; keep[0] = False
    return keep[lab]


blue = (b > r + .08) & (b > g - .03) & (sat > .18)
pale = (sat < .24) & (mx > .55) & ~blue

# Outline: the paper is pale and reaches the picture's border.
paperish = (sat < .22) & (mx > .2) & ~blue & ((g - b) < .045)   # gold's pale highlights are yellowish, the paper is not
paper_seed = ndi.binary_erosion(paperish, disk(3), border_value=1)
lab, _ = ndi.label(paper_seed)
border = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
paper = np.isin(lab, border[border > 0])
paper = ndi.binary_dilation(paper, disk(4)) & paperish
sil = largest(ndi.binary_fill_holes(~paper))
sil = ndi.binary_opening(ndi.binary_closing(sil, disk(5)), disk(3))
sil = largest(ndi.binary_fill_holes(sil))

# Pearl: pale and pinkish. Gold highlights are pale too, but yellowish and thin.
pinkish = (r - g) >= (g - b) - .012
pearl = pale & pinkish & ndi.binary_erosion(sil, disk(6))
pearl = ndi.binary_opening(pearl, disk(5))
pearl = drop_small(pearl, 2500)
pearl = ndi.binary_closing(pearl, disk(4))

# Blue enamel: field and ribbons together. Hairline gold inside it stays painted.
# Painted shadows beside gold lines are dark and not warm: they are enamel, never gold. (Tracing them as gold gave
# the gold lines ragged, lumpy edges.) Only well inside the badge, so the mockup's drop shadow stays out.
dark_enamel = (mx < .36) & (r < b + .05) & ndi.binary_erosion(sil, disk(14))
bl = (blue | dark_enamel) & sil
bl = ndi.binary_closing(bl, disk(3))
bl = ndi.binary_opening(bl, disk(2))
bl = drop_small(bl, 600)
bl &= ~pearl

np.savez_compressed(R / 'work/seg_raw.npz', sil=sil, pearl=pearl, blue=bl)
show = np.zeros((H, W, 3))
show[:] = (.15, .15, .15)
show[sil] = (.85, .6, .1)
show[bl] = (.15, .2, .7)
show[pearl] = (.95, .95, .95)
edge = sil ^ ndi.binary_erosion(sil, disk(1))
show[edge] = (1, 0, 0)
both = np.concatenate([im, show], 1)
Image.fromarray(np.uint8(both * 255)).save(R / 'work/seg_raw.png')
print('outline box', np.argwhere(sil).min(0)[::-1], np.argwhere(sil).max(0)[::-1], 'areas', sil.sum(), pearl.sum(), bl.sum())
