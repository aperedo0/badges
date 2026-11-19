from pathlib import Path
import json,numpy as np
from PIL import Image,ImageOps,ImageDraw
from scipy.ndimage import gaussian_filter
from scipy.signal import find_peaks,peak_widths
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;R=P.parents[1]
meta=json.loads((D/'comparison_geometry.json').read_text())
sources=[('reference',R/'reference.png',meta['reference_quad']),('layered_H',W/'baseline_cinema.png',meta['model_quad']),('current_P',D/'current_baseline.png',meta['model_quad'])]
stats={};images=[]
for name,path,quad in sources:
    im=Image.open(path).convert('RGB').transform((720,480),Image.Transform.QUAD,tuple(np.array(quad).ravel()),Image.Resampling.BICUBIC)
    im.save(D/(name+'_rectified.png'));images.append((name,im))
    a=np.asarray(im,float)/255;lum=a@np.array([.2126,.7152,.0722]);hh,ww=lum.shape
    y,x=np.mgrid[0:hh,0:ww];u=x/ww;v=y/hh
    safe=(u<.52+.65*v)&(v>.03)&(v<.97)&(u>.025)&(u<.97)
    core=((u-.48)/.21)**2+((v-.46)/.28)**2<1
    signal=np.log(np.maximum(lum,.005));signal-=gaussian_filter(signal,(hh*.09,ww*.08))
    gy,gx=np.gradient(gaussian_filter(signal,1.3));angle=(np.rad2deg(np.arctan2(gx,-gy))+90)%180-90
    weight=np.hypot(gx,gy);valid=safe&~core&(weight>np.percentile(weight[safe&~core],65))
    horizontal=float(np.sum(weight[valid&(abs(angle)<=25)])/np.sum(weight[valid]))
    profiles=[]
    for pos in [.08,.20,.30]:
        c=int(pos*ww);p=np.mean(signal[:,max(0,c-8):c+9],axis=1);p=gaussian_filter(p,1.1)
        peaks,props=find_peaks(-p,distance=hh*.024,prominence=.13*np.ptp(p))
        peaks=peaks[(peaks>hh*.04)&(peaks<hh*.96)]
        widths=peak_widths(-p,peaks,rel_height=.5)[0] if len(peaks) else []
        profiles.append(dict(column_fraction=pos,visible_dark_channel_count=len(peaks),spacing_fraction_of_region_height=(np.percentile(np.diff(peaks)/hh,[25,50,75]).tolist() if len(peaks)>1 else []),dark_channel_width_fraction_of_region_height=(np.percentile(np.asarray(widths)/hh,[25,50,75]).tolist() if len(widths) else [])))
    contrast=(gaussian_filter(lum,(hh*.04,ww*.04))-lum)/np.maximum(gaussian_filter(lum,(hh*.04,ww*.04)),.02)
    stats[name]=dict(profiles=profiles,weighted_grain_within_25_degrees_horizontal=horizontal,visible_dark_fraction=float(np.mean(contrast[safe]>.15)),limits='These are lit image proxies in the common lower wood region, not physical raised area, depth, roughness or intrinsic color.')
sheet=Image.new('RGB',(2160,518),'#202020')
for i,(name,im) in enumerate(images):sheet.paste(im,(i*720,38));ImageDraw.Draw(sheet).text((i*720+12,12),name,fill='white')
sheet.save(D/'evidence_comparison.jpg',quality=95)
(D/'image_measurements.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats))
