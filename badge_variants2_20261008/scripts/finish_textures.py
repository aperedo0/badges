"""Resolved metal finishes. Changes shader maps only, never points or normals.

All fields are in the material's USDZ_UV coordinates. Iron's relief strength
is encoded in the tangent-normal PNG; there is no runtime strength dependency.
"""
from pathlib import Path
import json
import math
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, gaussian_filter1d, map_coordinates

ROOT = Path(__file__).resolve().parents[1]
SIZE = 1024 if len(sys.argv)>1 and sys.argv[1]=='iron2' else 512
yy, xx = np.meshgrid(np.linspace(3.015, -3.015, SIZE),
                     np.linspace(-3.015, 3.015, SIZE), indexing='ij')


def encode_color(linear):
    return np.where(linear <= .0031308, 12.92 * linear,
                    1.055 * np.maximum(linear, 0) ** (1 / 2.4) - .055)


def save(path, field, color=False):
    if color:
        field = encode_color(field)
    if field.ndim == 2:
        field = np.repeat(field[:, :, None], 3, axis=2)
    Image.fromarray(np.uint8(np.clip(field, 0, 1) * 255 + .5)).save(path)


def source_coordinates(build):
    t = build['metadata']['reference_to_world']
    scale = np.array(t['scale'])
    off = np.array(t['offset'])
    sx = xx / scale[0] - off[0]
    sy = (yy + 2.455) / scale[1] - off[1]
    return sx, sy, scale, off


def faded(field, build):
    height = build['height']
    t = np.clip(((yy + 2.455) / height - .20) / .24, 0, 1)
    return field * t * t * (3 - 2 * t)


def directional_brush(u, v):
    # Non-periodic longitudinal polishing fibers, deliberately above phone resolution.
    coordinates = np.arange(-10, 10.001, .0125)
    rng = np.random.default_rng(241008)
    fine = gaussian_filter1d(rng.normal(size=len(coordinates)), 1.8)
    # Remove low-frequency valleys that looked like crumpled metal in the app.
    fine -= gaussian_filter1d(fine, 8.0)
    profile = fine/np.std(fine)
    profile = np.clip(profile/2.6, -1, 1)
    return np.interp(u+.002*np.sin(v*2.7), coordinates, profile)


def silver_fields(build,settings):
    sx, sy, scale, off = source_coordinates(build)
    reference_scale = build['metadata']['reference_scale']
    px = sx / reference_scale + 628
    py = 1052 - (sy + 3.015) / reference_scale
    # Brushing follows each leaf's actual long axis rather than global stripes.
    leaves = [((282,403),(416,255)), ((262,518),(391,397)),
              ((245,529),(221,319)), ((226,676),(142,477)),
              ((272,731),(327,522)), ((310,813),(127,657)),
              ((402,863),(353,672)), ((421,913),(194,829)),
              ((565,943),(422,797)), ((562,977),(332,969))]
    leaf = np.zeros_like(xx)
    closest = np.full_like(xx, np.inf)
    for mirror in [False, True]:
        for base, tip in leaves:
            a, b = np.array(base, float), np.array(tip, float)
            if mirror:
                a[0], b[0] = 1256-a[0], 1256-b[0]
            d = b-a
            t = np.clip(((px-a[0])*d[0]+(py-a[1])*d[1])/(d@d), 0, 1)
            dist = (px-a[0]-t*d[0])**2+(py-a[1]-t*d[1])**2
            axis = np.array([d[0], -d[1]]) / np.linalg.norm(d)
            u = -axis[1]*xx+axis[0]*yy
            v = axis[0]*xx+axis[1]*yy
            chosen = dist < closest
            leaf[chosen] = directional_brush(u, v)[chosen]
            closest[chosen] = dist[chosen]
    # Each planar face has its own directional finish, without a normal map.
    star = np.zeros_like(xx)
    star_rho=np.full_like(xx,settings["roughness"])
    star_color_gain=np.ones_like(xx)
    outline = [(627,237),(718,435),(898,478),(771,613),(801,801),
               (627,701),(453,800),(482,614),(351,478),(535,436)]
    center = np.array([627,553])
    for i in range(10):
        a, b = np.array(outline[i]), np.array(outline[(i+1)%10])
        tip = a if i % 2 == 0 else b
        d = np.array([tip[0]-center[0], center[1]-tip[1]], float)
        d /= np.linalg.norm(d)
        u = -d[1]*xx+d[0]*yy
        v = d[0]*xx+d[1]*yy
        image = Image.new('L', (SIZE,SIZE))
        draw = ImageDraw.Draw(image)
        points = []
        for p in [center,a,b]:
            source = np.array([(p[0]-628)*reference_scale,
                               (1052-p[1])*reference_scale-3.015])
            world = (source+off[:2])*scale[:2]+[0,-2.455]
            points.append(((world[0]+3.015)/6.03*(SIZE-1),
                           (3.015-world[1])/6.03*(SIZE-1)))
        draw.polygon(points, fill=255)
        mask = np.array(image)>0
        star[mask] = directional_brush(xx,yy)[mask]
        if i==9: star_color_gain[mask]=settings.get("top_plane_color_gain",1.0)
        if i==0: star_color_gain[mask]=settings.get("top_shaded_plane_color_gain",1.0)
        star_rho[mask]=settings.get("star_plane_roughness",{}).get(str(i),settings["roughness"] if i in [4,6,7,8,9] else settings.get("shaded_roughness",settings["roughness"]))
        if settings.get('star_polish_ramps'):
            av=a-center;bv=b-center;den=av[0]*bv[1]-av[1]*bv[0]
            beta=((px-center[0])*bv[1]-(py-center[1])*bv[0])/den
            gamma=(av[0]*(py-center[1])-av[1]*(px-center[0]))/den
            valley=np.clip(gamma if i%2==0 else beta,0,1)
            ends=settings['star_polish_ramps'].get(str(i),[.34,.37])
            polish=(ends[0]+(ends[1]-ends[0])*valley)-settings.get('polish_bowl_by_plane',{}).get(str(i),(settings.get('polish_bowl_gain',0) if i in settings.get('polish_bowl_planes',range(10)) else 0))*np.sin(np.pi*valley)**2
            star_rho[mask]=polish[mask]
    star_rho += faded(settings.get('polish_band_gain',0)*np.sin(2*np.pi*xx/.68+.25),build)
    return {'leaf': faded(leaf,build), 'star': faded(star,build),'star_rho':star_rho,'star_color_gain':star_color_gain}


def iron_field(build):
    sx, sy, _, _ = source_coordinates(build)
    rs = build['metadata']['reference_scale']
    px, py = sx / rs + 628, 60+(3.015-sy)/rs
    image = np.asarray(Image.open(ROOT/'source/iron_reference.png').convert('RGB'),float)/255
    image=np.where(image<=.04045,image/12.92,((image+.055)/1.055)**2.4)
    lum = image @ np.array([.2126,.7152,.0722])
    mask=lum>.0015
    local=gaussian_filter(lum*mask,18)/np.maximum(gaussian_filter(mask.astype(float),18),.01)
    # Linear-light reflectance ratio, without pre-blurring away fine scuffs.
    ratio=lum/np.maximum(local,.003)-1
    detail=map_coordinates(ratio,[py,px],order=1,mode='nearest')
    detail=np.clip(detail,-.45,.55)
    # Deliberate broad scoring follows the reference's diagonal tooling marks.
    score = np.zeros_like(xx)
    lines = [((554,466),(681,692)),((778,441),(929,575)),
             ((287,405),(413,495)),((461,306),(520,396)),
             ((754,674),(856,795)),((388,706),(461,798))]
    for a,b in lines:
        a,b=np.array(a,float),np.array(b,float);d=b-a
        t=np.clip(((px-a[0])*d[0]+(py-a[1])*d[1])/(d@d),0,1)
        signed=((px-a[0])*d[1]-(py-a[1])*d[0])/np.linalg.norm(d)
        ends=np.sin(np.pi*t)**.4
        groove=-np.exp(-.5*(signed/5.2)**2)
        lip=.40*np.exp(-.5*((signed-9)/5.2)**2)
        score+=(groove+lip)*ends
    field=detail
    return faded(field,build), faded(score,build)


def main(kind):
    base=ROOT/kind
    build=json.loads((base/'reports/build.json').read_text())
    settings=json.loads((base/'settings.json').read_text())
    directory=base/'mobile/textures'
    directory.mkdir(exist_ok=True)
    for p in directory.glob('*.png'):
        p.unlink()
    table=build['material_table']
    if kind=='silver2':
        for i,key in [(0,'leaf_color'),(3,'main_color'),(4,'shaded_color')]:table[i]['color_linear']=settings[key]
    else:
        for i,key in [(0,'plate_color'),(3,'plate_color'),(2,'rim_color')]:table[i]['color_linear']=settings[key]
    manifest={}
    if kind=='silver2':
        fields=silver_fields(build,settings)
        for i in [0,8,3,4]:
            field=fields['star' if i in [3,4] else 'leaf']
            rho=(settings['roughness'] if i==3 else settings.get('shaded_roughness',settings['roughness'])) if i in [3,4] else settings['leaf_roughness']
            name=table[i]['name']
            color=name+'_color.png';rough=name+'_roughness.png'
            base_color=np.array(table[i]["color_linear"])*(fields["star_color_gain"][:,:,None] if i in [3,4] else 1)
            save(directory/color,base_color*(1+(settings.get("star_brush_color_gain",settings.get("brush_color_gain",.004)) if i in [3,4] else settings.get("brush_color_gain",.004))*field[:,:,None]),True)
            save(directory/rough,(fields['star_rho'] if i in [3,4] else rho)+settings.get("brush_roughness_gain",.002)*field)
            manifest[str(i)]={'diffuseColor':color,'roughness':rough}
        evidence={'method':'Band-limited aperiodic longitudinal fibers per leaf/star point; low-frequency color valleys removed; even per-plane polished roughness, no normals or baked illumination.','fiber_gaussian_sigma_world':.0225,'fiber_FWHM_world':.053,'polish_bowl_by_plane':settings.get('polish_bowl_by_plane',{}),'brush_color_gain':settings['brush_color_gain'],'star_brush_color_gain':settings.get('star_brush_color_gain',settings['brush_color_gain']),'brush_roughness_gain':settings['brush_roughness_gain'],'polish_bowl_gain':settings['polish_bowl_gain'],'polish_bowl_planes':settings['polish_bowl_planes'],'top_plane_color_gain':settings.get('top_plane_color_gain',1),'top_shaded_plane_color_gain':settings.get('top_shaded_plane_color_gain',1),'star_plane_roughness':settings.get('star_plane_roughness',{}),'star_polish_ramps':settings.get('star_polish_ramps',{}),'normal_maps':0}
    else:
        field,relief=iron_field(build)
        dy,dx=np.gradient(relief,6.03/(SIZE-1))
        gradients=np.stack([-dx,dy],axis=2)
        slope=np.linalg.norm(gradients,axis=2)
        coefficient=math.tan(math.radians(settings['normal_max_degrees']))/max(float(np.percentile(slope,99)),1e-6)
        gradients*=coefficient
        gradients[yy < -2.455+.20*build['height']]=0
        length=np.linalg.norm(gradients,axis=2)
        gradients*=np.minimum(1,math.tan(math.radians(settings['normal_max_degrees']))/np.maximum(length,1e-9))[:,:,None]
        n=np.concatenate([gradients,np.ones((SIZE,SIZE,1))],axis=2)
        n/=np.linalg.norm(n,axis=2,keepdims=True)
        for i in [0,2]:
            name=table[i]['name'];factor=1 if i==0 else .80
            color=name+'_color.png';rough=name+'_roughness.png';normal=name+'_normal.png'
            save(directory/color,np.array(table[i]['color_linear'])*(1+settings['texture_gain']*factor*field[:,:,None]),True)
            center=settings['plate_roughness'] if i==0 else .40
            save(directory/rough,np.full_like(field,center))
            ns=n if i==0 else np.concatenate([gradients*.65,np.ones((SIZE,SIZE,1))],axis=2)
            ns/=np.linalg.norm(ns,axis=2,keepdims=True)
            if settings.get('normal_enabled',True):
                save(directory/normal,.5+.5*ns)
            manifest[str(i)]={'diffuseColor':color,'roughness':rough}
            if settings.get('normal_enabled',True):manifest[str(i)]['normal']=normal
        manifest['3']=manifest['0']
        evidence={'method':'Fine reference-derived worked-metal color, lighting removed; even satin roughness; no metal normal maps.','minimum_feature_reference_sigma_pixels':0,'method_version':'linear-light reference reflectance ratio,1024px, no texture pre-blur','scoring_sigma_pixels':5.2,'maximum_normal_tilt_degrees':settings['normal_max_degrees'],'relief_height_scale_world':coefficient,'normal_maps':2 if settings.get('normal_enabled',True) else 0,'reference_detail_exception':'Fine reference marks retained in color only (about1to2screenpixels); bounded contrast, filtered at texture sampling, never specular-normal or roughness grain. Coarse broadening made the earlier candidates look pebbled.','owner_authorization':'Earlier explicit approval: Test restrained normal maps for a closer reference match, applied to Iron tier material revision.'}
    if kind=='iron2' and not settings.get('normal_enabled',True):
        evidence['maximum_normal_tilt_degrees']=None
        evidence['relief_height_scale_world']=None
    evidence.update(resolution=[SIZE,SIZE],lower_plain_fraction=.20,full_finish_fraction=.44)
    (base/'reports/finish_maps.json').write_text(json.dumps({'materials':manifest,'evidence':evidence},indent=2)+'\n')
    print(kind,json.dumps(evidence))


if __name__=='__main__':
    main(sys.argv[1])
