"""After a version 12 render: measure how cleanly the pieces join and lay out key moments.
    python3 temple/tools/v12_check.py [OUT.png]      (run from the animation folder)
A join is the mean difference per pixel (0 to 255) between the last frame of one piece and the first of the
next. Two neighbouring frames of the ending are printed for scale."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R = "render/v12_frames/"
def A(p): return np.asarray(Image.open(R + p).convert("RGB")).astype(float)
def last(d): return sorted(f for f in os.listdir(R + d) if f.endswith(".png"))[-1]
pairs = [("arrival end into waiting start", "arrival/" + last("arrival"), "waiting/0000.png"),
         ("waiting end into waiting start (three rattles)", "waiting/0224.png", "waiting/0000.png"),
         ("waiting frame 74 into waiting start (one rattle)", "waiting/0074.png", "waiting/0000.png"),
         ("waiting end into reveal start", "waiting/0224.png", "reveal/0000.png"),
         ("reveal end into ending start", "reveal/" + last("reveal"), "ending/0000.png"),
         ("ending loop end into its start", "ending_loop/0089.png", "ending_loop/0000.png"),
         ("for scale: two neighbouring ending frames", "ending/0040.png", "ending/0041.png"),
         ("for scale: two neighbouring reveal frames (camera moving)", "reveal/0100.png", "reveal/0101.png")]
for name, a, b in pairs:
    d = np.abs(A(a) - A(b)).mean(2)
    h = d.shape[0]
    print(f"{name:56s} mean {d.mean():5.2f}  top third {d[:h // 3].mean():5.2f}  max {d.max():4.0f}")
# how much the picture changes from frame to frame through the reveal (a spike is a jolt)
prev = None; steps = []
for f in sorted(x for x in os.listdir(R + "reveal") if x.endswith(".png")):
    cur = np.asarray(Image.open(R + "reveal/" + f).convert("L").resize((189, 410))).astype(float)
    if prev is not None:
        steps.append(float(np.abs(cur - prev).mean()))
    prev = cur
s = np.array(steps)
print("reveal frame to frame change: median %.2f, largest %.2f at frame %d (largest five: %s)" % (
    np.median(s), s.max(), int(s.argmax()) + 1, ", ".join("%d:%.2f" % (i + 1, s[i]) for i in np.argsort(s)[-5:][::-1])))
print("brightness of the whole picture every half second of the reveal:", " ".join(
    "%d" % np.asarray(Image.open(R + "reveal/%04d.png" % i).convert("L")).mean() for i in range(0, len(steps) + 1, 15)))
if len(sys.argv) > 1:
    f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    picks = [("arrival", 5, "empty temple"), ("arrival", 46, "chest lands"), ("arrival", 62, "dust"), ("arrival", 123, "at rest"),
             ("waiting", 4, "rattle 1"), ("waiting", 154, "rattle 3"), ("reveal", 6, "lock clicks"), ("reveal", 52, "lid opens"),
             ("reveal", 80, "badge rises"), ("reveal", 100, "first torches"), ("reveal", 125, "more torches"), ("reveal", 150, "beam arriving"),
             ("reveal", 175, "all lit"), ("reveal", 200, "mist thinning"), ("reveal", 230, "mist gone"), ("ending", 40, "ending loop")]
    W = 300
    ims = []
    for d, i, t in picks:
        im = Image.open(R + f"{d}/{i:04d}.png").convert("RGB")
        ims.append((im.resize((W, round(im.size[1] * W / im.size[0])), Image.LANCZOS), t))
    h = ims[0][0].size[1]
    top, pad = 30, 6
    sh = Image.new("RGB", (W * 8 + pad * 7, (h + top) * 2 + pad), (18, 18, 18))
    dr = ImageDraw.Draw(sh)
    for k, (im, t) in enumerate(ims):
        x, y = (k % 8) * (W + pad), (k // 8) * (h + top + pad)
        sh.paste(im, (x, y + top)); dr.text((x + 6, y + 5), t, fill=(235, 235, 235), font=f)
    sh.save(sys.argv[1]); print("sheet", sh.size)
