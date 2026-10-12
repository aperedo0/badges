"""Padded affine texture islands prevent color leakage at real planar edges."""
from pathlib import Path
import json,numpy as np
SIZE=512;CELL=128;PAD=12;CORE=CELL-2*PAD

def island_bounds(points):
    p=np.array(points)[:,:2];return p.min(0),p.max(0)

def uv_for_plane(points,plane,triangle):
    low,high=island_bounds(triangle);p=np.array(points)[:,:2]
    grid=(p-low)/(high-low)
    col,row=plane%4,plane//4
    pixel=np.array([col*CELL+PAD,row*CELL+PAD])+grid*[CORE,-CORE]+[0,CORE]
    return np.stack([pixel[:,0]/(SIZE-1),1-pixel[:,1]/(SIZE-1)],axis=1)

def encode_color(linear):
    return np.where(linear<=.0031308,linear*12.92,1.055*np.maximum(linear,0)**(1/2.4)-.055)

def write_atlas(base):
    from PIL import Image
    from scipy.ndimage import gaussian_filter1d
    build=json.loads((base/'reports/build.json').read_text());s=json.loads((base/'settings.json').read_text());geom=json.loads((base/'reports/Star_geometry.json').read_text())
    transform=build['metadata']['reference_to_world'];scale=np.array(transform['scale']);off=np.array(transform['offset']);rs=build['metadata']['reference_scale']
    outline=np.array([(627,237),(718,435),(898,478),(771,613),(801,801),(627,701),(453,800),(482,614),(351,478),(535,436)],float);center=np.array([627,553]);evidence=[]
    coords=np.arange(-10,10.001,.0125);rng=np.random.default_rng(241008);fine=gaussian_filter1d(rng.normal(size=len(coords)),1.8);fine-=gaussian_filter1d(fine,8);profile=np.clip(fine/np.std(fine)/2.6,-1,1)
    for material,key in [(3,'main_color'),(4,'shaded_color')]:
        rgb=np.ones((SIZE,SIZE,3),float)*np.array(s[key]);rho=np.ones((SIZE,SIZE))*s['roughness' if material==3 else 'shaded_roughness']
        for plane,face in enumerate(geom['subsets']['front']):
            tri=np.array(geom['points'])[np.array(geom['indices'])[face]];low,high=island_bounds(tri);row,col=plane//4,plane%4
            ty,tx=np.meshgrid(np.arange(CELL),np.arange(CELL),indexing='ij')
            worldx=low[0]+(tx-PAD)/CORE*(high[0]-low[0]);worldy=low[1]+(CELL-PAD-ty)/CORE*(high[1]-low[1])
            sx=worldx/scale[0]-off[0];sy=(worldy+2.455)/scale[1]-off[1];px=sx/rs+628;py=1052-(sy+3.015)/rs
            angle=np.deg2rad(s.get('star_ramp_angles',{}).get(str(plane),(plane%3-1)*10));keydir=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])@([-1/np.sqrt(2)]*2)
            projections=np.array([center,outline[plane],outline[(plane+1)%10]])@keydir
            q=(px*keydir[0]+py*keydir[1]-projections.min())/np.ptp(projections)
            factor=(s.get('top_plane_color_gain',1) if plane==9 else s.get('top_shaded_plane_color_gain',1) if plane==0 else 1)*s.get('star_plane_color_gain',{}).get(str(plane),1)
            gain=factor*(1+s['star_color_ramp']*(2*q-1))
            fade=np.clip(((worldy+2.455)/build['height']-.20)/.24,0,1);fade=fade*fade*(3-2*fade)
            brush=np.interp(worldx+.002*np.sin(worldy*2.7),coords,profile)*fade
            plane_rgb=np.array(s['main_color' if material==3 else 'shaded_color'])*gain[:,:,None]*(1+s['star_brush_color_gain']*brush[:,:,None])
            rgb[row*CELL:(row+1)*CELL,col*CELL:(col+1)*CELL]=plane_rgb
            rough=s.get('star_plane_roughness',{}).get(str(plane),s['roughness'] if plane in [4,6,7,8,9] else s['shaded_roughness'])
            rho[row*CELL:(row+1)*CELL,col*CELL:(col+1)*CELL]=rough+s['brush_roughness_gain']*brush
            if (material==3)==(plane in [4,6,7,8,9]):
                quant=np.uint8(np.clip(encode_color(plane_rgb),0,1)*255+.5)
                av=tri[1,:2]-tri[0,:2];bv=tri[2,:2]-tri[0,:2];den=av[0]*bv[1]-av[1]*bv[0]
                bx=((worldx-tri[0,0])*bv[1]-(worldy-tri[0,1])*bv[0])/den
                by=(av[0]*(worldy-tri[0,1])-av[1]*(worldx-tri[0,0]))/den
                inside=(bx>=0)&(by>=0)&(bx+by<=1)
                evidence.append({'plane':plane,'affine_gradient_curvature_source':0,'float64_source':True,'padded_island_pixels':PAD,'quantized_core_red_levels':len(np.unique(quant[:,:,0][inside])),'core_min_max_linear': [float(plane_rgb[inside].min()),float(plane_rgb[inside].max())]})
        np.savez_compressed(base/'reports'/f'star_high_precision_source_material{material}.npz',linear_color_float64=rgb,roughness_float64=rho)
        name=build['material_table'][material]['name']
        Image.fromarray(np.uint8(np.clip(encode_color(rgb),0,1)*255+.5)).save(base/'mobile/textures'/f'{name}_color.png')
        Image.fromarray(np.uint8(np.repeat(np.clip(rho,0,1)[:,:,None],3,axis=2)*255+.5)).save(base/'mobile/textures'/f'{name}_roughness.png')
    (base/'reports/atlas_precision.json').write_text(json.dumps({'method':'one affine projection per flat face; independent padded UV islands, no interpolation across plane edges; plain side/back island','planes':evidence,'normal_maps':0},indent=2)+'\n')
