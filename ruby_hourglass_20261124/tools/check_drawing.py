"""Compare the real modeled silhouette and visible cut ridges with the source drawing."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[1];cand=root/'candidate01'
g=json.loads((cand/'geometry.json').read_text());s=5.45/1245
src=Image.open(Path.home()/'Downloads/Faceted ruby hourglass with side rails.png').convert('RGBA')
ref=Image.new('RGB',src.size,(18,18,20));ref.paste(src,mask=src.getchannel('A'))
mask=Image.new('1',src.size);target=np.asarray(src.getchannel('A'))>128
def proj(p): return np.array([558+p[0]/s,87+(2.995-p[1])/s])
view=Image.blend(ref,Image.new('RGB',ref.size,(0,0,0)),.35);painter=ImageDraw.Draw(view)
for name,obj in g.items():
    pts=np.array(obj['points']);tri=np.array(obj['triangles']);edges={}
    lines=np.array([proj(v) for v in pts])
    for f in tri:
        a,b,c=pts[f];n=np.cross(b-a,c-a);n/=np.linalg.norm(n)
        if n[2]<1e-5:continue
        ImageDraw.Draw(mask).polygon([tuple(lines[i]) for i in f],fill=1)
        if 'Ruby' in name:
            for j in range(3):
                e=tuple(sorted((f[j],f[(j+1)%3])))
                edges.setdefault(e,[]).append(n)
    for (i,j),ns in edges.items():
        if len(ns)==1 or np.dot(ns[0],ns[1])<.9999:
            painter.line([tuple(lines[i]),tuple(lines[j])],fill=(109,220,215),width=2)
m=np.asarray(mask,dtype=bool)
iou=np.count_nonzero(m&target)/np.count_nonzero(m|target)
print('Full reference silhouette overlap',iou)
assert iou>.945,iou
for y in (192,400,610,695,810,1100,1235):
    borders=lambda row:np.flatnonzero(np.diff(row.astype(int),prepend=0,append=0))
    refrow=target[y]
    # One pixel alpha glints can create isolated false components.
    from scipy.ndimage import binary_closing,binary_opening
    goal=borders(binary_opening(binary_closing(refrow,structure=np.ones(3)),structure=np.ones(5)))
    actual=borders(m[y])
    print(y,goal.tolist(),actual.tolist())
    assert len(goal)==6 and len(actual)==6 and max(abs(goal-actual))<15,(goal,actual)
view.thumbnail((560,700));view.save(cand/'facet_overlay.png')
