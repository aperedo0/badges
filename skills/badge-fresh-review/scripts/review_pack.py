"""Make the review pictures, measurements and filled brief for one badge version.

Usage:
  review_pack.py CONFIG.json OUT_DIR              review of a build against the mockup

CONFIG.json:
{
  "name": "Ruby Crown",
  "mockup": "/abs/mockup.png",
  "mockup_box": [cx, top, bottom],          # badge center column and highest and lowest rows
  "build_front": "/abs/app/front.png",      # app capture, resting front
  "build_box": [cx, top, bottom],           # projected through the app camera, or measured
  "poses": {"early turn": "/abs/app/early_turn.png", "left side": "...", "back": "...", "right side": "..."},
  "regions": [["top ornament", dx0, y0, dx1, y1], ...],   # in badge heights; dx from the center, y from the top
  "intended": ["what the owner asked to differ", ...]
}
Pictures stay under about 1.15 megapixels each, the most a reviewer sees anyway.
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

SKILL = Path(__file__).resolve().parent.parent
H = 900          # common badge height for aligned pictures
MAXPX = 1_150_000


def load(path):
    return Image.open(path).convert('RGB')


def aligned(img, box, half_w, pad):
    """Scale so the badge is H tall; crop around its center. Returns image and badge top row in it."""
    cx, top, bottom = box
    s = H / (bottom - top)
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    left = round(cx * s - half_w); upper = round(top * s) - pad
    # Areas outside the picture take its own border color, not black: a black fill there was read as the
    # backdrop, so a narrow mockup's whole frame counted as badge (its widths and overlap were wrong).
    a = np.asarray(im)
    border = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    canvas = Image.new('RGB', (2 * half_w, H + 2 * pad), tuple(int(v) for v in np.median(border, 0)))
    canvas.paste(im, (-left, -upper))
    return canvas


def silhouette(img_aligned, pad, chroma=22, contrast=40, min_area=300):
    """Badge mask: pixels that are colored, or clearly brighter or darker than the backdrop at the row's edges.

    Keeps every piece bigger than min_area, since open badges have separate leaves and tips.
    A grey or silver badge on a grey stage may still need a lower contrast or a check by eye.
    """
    a = np.asarray(img_aligned).astype(int)
    edge = np.concatenate([a[:, :20], a[:, -20:]], 1)
    bg = np.median(edge, 1)[:, None, :]
    m = ((a.max(2) - a.min(2)) > chroma) | (np.abs(a - bg).max(2) > contrast)
    m[:pad - 3] = False; m[pad + H + 3:] = False
    m = ndi.binary_closing(m, iterations=3)
    m = ndi.binary_opening(m, iterations=1)
    m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m)
    if n:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.nonzero(sizes >= min_area)[0])
    return m


def outline(mask):
    return mask & ~ndi.binary_erosion(mask, iterations=2)


def fit(im):
    s = min(1.0, (MAXPX / (im.width * im.height)) ** 0.5)
    return im if s >= 1 else im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def labeled(im, text):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 * len(text) + 12, 20), fill=(0, 0, 0)); d.text((5, 4), text, fill=(255, 255, 0))
    return im


def pair(a, b, la, lb, gap=8):
    out = Image.new('RGB', (a.width + b.width + gap, max(a.height, b.height)), (40, 40, 40))
    out.paste(labeled(a.copy(), la), (0, 0)); out.paste(labeled(b.copy(), lb), (a.width + gap, 0))
    return out


def stack(ims, gap=8):
    out = Image.new('RGB', (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), (40, 40, 40))
    y = 0
    for i in ims:
        out.paste(i, (0, y)); y += i.height + gap
    return out


def crop_badge_auto(path):
    """Crop around a turned pose: colored pixels in the badge area, cut at the gap above the floor reflection."""
    img = load(path); a = np.asarray(img).astype(int)
    x0, x1, y0, y1 = int(a.shape[1] * 0.12), int(a.shape[1] * 0.88), int(a.shape[0] * 0.05), int(a.shape[0] * 0.56)
    sub = a[y0:y1, x0:x1]; m = ((sub.max(2) - sub.min(2)) > 40) & (sub.max(2) > 50)
    rows = np.nonzero(m.sum(1) > 3)[0]
    if len(rows) == 0:   # a grey or silver pose has no colored pixels: fall back to the badge area itself
        return img.crop((x0, y0, x1, y1))
    gaps = np.nonzero(np.diff(rows) > 15)[0]
    top = rows[0]; bot = rows[gaps[0]] if len(gaps) else rows[-1]
    cols = np.nonzero(m[top:bot].sum(0) > 2)[0]
    cx = (cols[0] + cols[-1]) / 2 + x0; cy = (top + bot) / 2 + y0; h = max(bot - top, cols[-1] - cols[0]) * 1.1
    return img.crop((int(cx - h / 2), int(cy - h / 2), int(cx + h / 2), int(cy + h / 2)))


def widths(mask, pad):
    rows = {}
    for f in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        r = pad + int(f * H); xs = np.nonzero(mask[max(r - 2, 0):r + 3].any(0))[0]
        rows[f] = (xs[-1] - xs[0]) / H if len(xs) else 0.0
    xs = np.nonzero(mask.any(0))[0]
    return rows, (xs[-1] - xs[0]) / H if len(xs) else 0.0


def overlap(mm, bm, pad, bands=10):
    """Silhouette overlap of the aligned outlines (1.00 = the same outline), the share of the mockup the build
    is missing, the share the build adds, and the worst horizontal band. A low score flags a wrong shape;
    a high score never proves the badge looks right."""
    inter, union = (mm & bm).sum(), (mm | bm).sum()
    score = inter / union if union else 0.0
    missing = (mm & ~bm).sum() / max(mm.sum(), 1); extra = (bm & ~mm).sum() / max(mm.sum(), 1)
    band = []
    for k in range(bands):
        r0, r1 = pad + k * H // bands, pad + (k + 1) * H // bands
        u = (mm[r0:r1] | bm[r0:r1]).sum()
        band.append(((mm[r0:r1] & bm[r0:r1]).sum() / u) if u else 1.0)
    return score, missing, extra, band


def mismatch_picture(mock, mm, bm, path):
    """Red = the mockup has it and the build does not; blue = the build has it and the mockup does not."""
    a = np.asarray(Image.blend(mock, Image.new('RGB', mock.size, (0, 0, 0)), 0.6)).copy()
    a[mm & ~bm] = (255, 60, 60); a[bm & ~mm] = (60, 140, 255)
    fit(labeled(Image.fromarray(a), 'red = build is missing it, blue = build adds it')).save(path)


def outline_points(full, count=6):
    """Points on the build's outline: top, bottom, leftmost and rightmost tips, then the brightest outline spots
    (where white dots appear, AGENTS.md 3.9), so the 4x zooms always cover the silhouette."""
    a = np.asarray(full).astype(int); edge = np.concatenate([a[:, :8], a[:, -8:]], 1); bg = np.median(edge, 1)[:, None, :]
    m = ((a.max(2) - a.min(2)) > 22) | (np.abs(a - bg).max(2) > 40)
    m = ndi.binary_fill_holes(ndi.binary_opening(ndi.binary_closing(m, iterations=3), iterations=1))
    lab, n = ndi.label(m)
    if not n:
        return []
    m = lab == (1 + int(np.argmax(ndi.sum(m, lab, range(1, n + 1)))))
    ys, xs = np.nonzero(m & ~ndi.binary_erosion(m, iterations=2))
    if not len(xs):
        return []
    pts = [(xs[ys.argmin()], ys.min()), (xs[ys.argmax()], ys.max()), (xs.min(), ys[xs.argmin()]), (xs.max(), ys[xs.argmax()])]
    lum = a[ys, xs].sum(1); order = np.argsort(-lum)
    for i in order:
        if len(pts) >= count:
            break
        if all(abs(xs[i] - px) > 60 or abs(ys[i] - py) > 45 for px, py in pts):
            pts.append((xs[i], ys[i]))
    return [(int(x), int(y)) for x, y in pts]


def finish_pictures(cfg, out, tile=(80, 60), zoom=4, count=6):
    """Full size crop of the resting front capture, 4x nearest neighbor zooms of its busiest edges, and 4x zooms of
    its outline (tips and brightest outline spots)."""
    img = load(cfg['build_front']); cx, top, bot = cfg['build_box']; h = bot - top
    box = (int(cx - 0.62 * h), int(top - 0.05 * h), int(cx + 0.62 * h), int(bot + 0.05 * h))
    full = img.crop(box)
    p_full = out / 'finish_full_size.png'; labeled(full.copy(), 'build at its real pixels (no resizing)').save(p_full)
    g = np.asarray(full.convert('L')).astype(float)
    energy = ndi.uniform_filter(np.hypot(*np.gradient(ndi.gaussian_filter(g, 0.6))), size=(tile[1], tile[0]))
    tw, th = tile; picks = []
    e = energy.copy(); e[:th // 2, :] = 0; e[-th // 2:, :] = 0; e[:, :tw // 2] = 0; e[:, -tw // 2:] = 0
    for _ in range(count):
        y, x = np.unravel_index(np.argmax(e), e.shape)
        if e[y, x] <= 0:
            break
        picks.append((x, y)); e[max(0, y - th):y + th, max(0, x - tw):x + tw] = 0
    tiles = [labeled(full.crop((x - tw // 2, y - th // 2, x + tw // 2, y + th // 2)).resize((tw * zoom, th * zoom), Image.NEAREST),
                     f'4x at ({x}, {y})') for x, y in picks]
    cols = 3; rows = (len(tiles) + cols - 1) // cols
    grid = Image.new('RGB', (cols * tw * zoom + (cols - 1) * 6, rows * th * zoom + (rows - 1) * 6), (60, 60, 60))
    for i, t in enumerate(tiles):
        grid.paste(t, ((i % cols) * (tw * zoom + 6), (i // cols) * (th * zoom + 6)))
    p_zoom = out / 'finish_4x.png'; grid.save(p_zoom)
    # the outline at 4x: the busiest spots above are usually inside the badge
    otiles = []
    for x, y in outline_points(full):
        x = min(max(x, tw // 2), full.width - tw // 2); y = min(max(y, th // 2), full.height - th // 2)
        otiles.append(labeled(full.crop((x - tw // 2, y - th // 2, x + tw // 2, y + th // 2)).resize((tw * zoom, th * zoom), Image.NEAREST),
                              f'outline 4x at ({x}, {y})'))
    p_out = None
    if otiles:
        rows = (len(otiles) + cols - 1) // cols
        og = Image.new('RGB', (cols * tw * zoom + (cols - 1) * 6, rows * th * zoom + (rows - 1) * 6), (60, 60, 60))
        for i, t in enumerate(otiles):
            og.paste(t, ((i % cols) * (tw * zoom + 6), (i // cols) * (th * zoom + 6)))
        p_out = out / 'finish_outline_4x.png'; og.save(p_out)
    # the whole badge at 2x, in four tiles, so no area is left unseen
    big = full.resize((full.width * 2, full.height * 2), Image.NEAREST); hw, hh = big.width // 2, big.height // 2
    tiles2 = []
    for k, (x0, y0) in enumerate(((0, 0), (hw, 0), (0, hh), (hw, hh))):
        pt = out / f'finish_2x_{k + 1}.png'; labeled(big.crop((x0, y0, x0 + hw, y0 + hh)), f'2x, quarter {k + 1} of 4').save(pt); tiles2.append(pt)
    return [(p_full, 'finish: the build front at its real pixels, exactly as the phone shows it')] + \
           [(pt, f'finish: quarter {k + 1} of the whole badge at 2x') for k, pt in enumerate(tiles2)] + [
            (p_zoom, 'finish: 4x zooms (nearest neighbor) of the build\'s busiest lines and edges')] + (
           [(p_out, 'finish: 4x zooms (nearest neighbor) of the build\'s outline: its tips and brightest edge spots')] if p_out else [])


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
    pad = 40; half_w = int(H * 0.78)
    mock = aligned(load(cfg['mockup']), cfg['mockup_box'], half_w, pad)
    pics = []

    def region_crop(im, r):
        _, dx0, y0, dx1, y1 = r
        return im.crop((int(half_w + dx0 * H), int(pad + y0 * H), int(half_w + dx1 * H), int(pad + y1 * H)))

    build = aligned(load(cfg['build_front']), cfg['build_box'], half_w, pad)
    mm, bm = silhouette(mock, pad), silhouette(build, pad)
    # far 1: same height side by side
    p = out / 'far_same_height.png'; fit(pair(mock, build, 'mockup', 'build')).save(p)
    pics.append((p, 'far: mockup (left) and build front (right) at the same height'))
    # far 2: phone size, how it reads at a glance
    small = [im.resize((im.width * 150 // im.height, 150), Image.LANCZOS) for im in (mock, build)]
    p = out / 'far_phone_size.png'; pair(*small, 'mockup', 'build').save(p)
    pics.append((p, 'far: both at about the size the owner sees on the phone'))
    # far 3: outlines over the mockup
    ov = Image.blend(mock, Image.new('RGB', mock.size, (0, 0, 0)), 0.45); a = np.asarray(ov).copy()
    a[ndi.binary_dilation(outline(mm), iterations=1)] = (255, 220, 0); a[ndi.binary_dilation(outline(bm), iterations=1)] = (0, 230, 255)
    p = out / 'far_outline_overlay.png'; fit(labeled(Image.fromarray(a), 'yellow = mockup outline, cyan = build outline')).save(p)
    pics.append((p, 'far: outlines at the same height over the dimmed mockup'))
    # close ups: matching regions, mockup left, build right
    rows = [pair(region_crop(mock, r), region_crop(build, r), 'mockup: ' + r[0], 'build: ' + r[0]) for r in cfg['regions']]
    for i in range(0, len(rows), 2):
        p = out / f'close_{i // 2 + 1}.png'; fit(stack(rows[i:i + 2])).save(p)
        pics.append((p, 'close: ' + ', '.join(r[0] for r in cfg['regions'][i:i + 2]) + ' (mockup left, build right)'))
    # finish: the app capture at its own pixels (never resized) and 4x zooms of its busiest edges, so surface
    # defects (fuzz or glitter along lines, stair steps, speckle, white dots on the outline) cannot hide in scaling
    for p, d in finish_pictures(cfg, out):
        pics.append((p, d))
    # turns
    if cfg.get('poses'):
        tiles = [labeled(mock.resize((mock.width * 420 // mock.height, 420)), 'mockup')]
        turn_finish = []
        for k, v in cfg['poses'].items():
            c = crop_badge_auto(v)
            # the strip is for shape: every pose smooth at one height, so no tile shows enlargement steps that read
            # as stair stepped edges. Real pixels are judged in the separate 2x pictures below.
            tiles.append(labeled(c.resize((420, 420), Image.LANCZOS), k))
            z = 2 if c.width * c.height * 4 <= MAXPX else 1
            pt = out / f'finish_turn_{"".join(ch if ch.isalnum() else "_" for ch in k)}.png'
            labeled(c.resize((c.width * z, c.height * z), Image.NEAREST), f'{k}: {z}x, each block is one phone pixel').save(pt)
            turn_finish.append((pt, f'finish: the {k} pose at {z}x with hard pixel steps (blocks are the zoom, not the badge)'))
        strip = Image.new('RGB', (sum(t.width for t in tiles), 420), (40, 40, 40)); x = 0
        for t in tiles:
            strip.paste(t, (x, 0)); x += t.width
        p = out / 'turns.png'; fit(strip).save(p); pics.append((p, 'far: the build turning (it spins on the Home screen)'))
        pics += turn_finish
    # measurements
    wm, tm = widths(mm, pad); wb, tb = widths(bm, pad)
    table = ['| height from top | mockup width | build width |', '|---|---|---|']
    table += [f'| {int(f * 100)}% | {wm[f]:.2f} | {wb[f]:.2f} |' for f in wm]
    table += [f'| widest | {tm:.2f} | {tb:.2f} |']
    meas = 'Silhouette width as a fraction of badge height, measured from the aligned front pictures:\n\n' + '\n'.join(table)
    score, missing, extra, band = overlap(mm, bm, pad)
    worst = int(np.argmin(band))
    # the overlap score stays out of the brief: a reviewer anchors on a number, and a high one says nothing about
    # closeness (Ruby Crown version 12: overlap 0.91, closeness 66)
    mismatch_picture(mock, mm, bm, out / 'outline_mismatch.png')
    prompt = (SKILL / 'references/reviewer-prompt.md').read_text()
    finish_prompt = (SKILL / 'references/finish-prompt.md').read_text()
    version = hashlib.sha256((prompt + finish_prompt).encode()).hexdigest()[:10]   # scores compare only within a version
    (out / 'overlap.json').write_text(json.dumps({'overlap': round(float(score), 4), 'missing': round(float(missing), 4),
                                                   'extra': round(float(extra), 4), 'worst_band_from_top': worst / 10,
                                                   'bands': [round(float(b), 4) for b in band], 'brief_version': version}, indent=1))
    print(f'outline overlap {score:.2f} (missing {missing:.0%}, extra {extra:.0%}, weakest {worst * 10}% to {worst * 10 + 10}% from the top); '
          f'below 0.85 fix the outline before details. Picture: {out / "outline_mismatch.png"}')
    # the finish brief: the shippable question alone, on the finish pictures, for the second fresh agent (step 0)
    fin = [(p, d) for p, d in pics if d.startswith('finish:') or d.startswith('far: the build turning')]
    (out / 'finish_brief.md').write_text(finish_prompt.replace('{NAME}', cfg['name']).replace(
        '{PICTURES}', '\n'.join(f'{k + 1}. {d}: {p}' for k, (p, d) in enumerate(fin))) + f'\n\nBrief version {version}.\n')
    text = prompt
    text = text.replace('{NAME}', cfg['name'])
    text = text.replace('{PICTURES}', '\n'.join(f'{k + 1}. {d}: {p}' for k, (p, d) in enumerate(pics)))
    text = text.replace('{INTENDED}', '\n'.join('* ' + s for s in cfg.get('intended', [])) or '* none')
    text = text.replace('{MEASUREMENTS}', meas)
    (out / 'brief.md').write_text(text + f'\n\nBrief version {version}.\n')
    print('review brief:', out / 'brief.md', 'pictures:', len(pics))


if __name__ == '__main__':
    main()
