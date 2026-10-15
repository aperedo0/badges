"""Clean reference profiles for Blender's native lathed hourglass parts."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/achievement_coin_mpl')
import json
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.spatial import Delaunay
from matplotlib.path import Path as Polygon
from collections import Counter

ROOT = Path(__file__).resolve().parent

def bezier(start, sections, count=40):
    points = [np.array(start, float)]
    for a, b, end in sections:
        p = points[-1]
        for t in np.linspace(0, 1, count + 1)[1:]:
            points.append((1-t)**3*p + 3*(1-t)**2*t*np.array(a) + 3*(1-t)*t*t*np.array(b) + t**3*np.array(end))
    return np.array(points)

for name in ['hourglass_teal', 'hourglass_gold']:
    root = ROOT / name
    meta = json.loads((root/'design.json').read_text())
    loaded = np.load(root/'reliefs.npz')
    arrays = {key: loaded[key] for key in loaded.files}
    cx, cy, radius = meta['circle']
    scale = 3.015/radius
    def world(points):
        return (np.asarray(points)-[cx, cy])*[scale, -scale]
    # One continuous turned profile per support, with deliberate terminal
    # collars and a single center joint instead of rippling stacked bulges.
    y = np.array([307,312,318,324,331,340,379,422,461,490,509,531,552,560,566,575,584,593,601,612,637,662,681,706,747,793,826,843,850,856,866,875,879],float)
    r = np.array([12,23,28,26,17,15,11,13,20,26,25,18,12,12,21,29,29,23,16,16,22,27,26,18,12,11,14,18,24,29,29,23,12],float)
    dense = np.linspace(y.min(), y.max(), 110)
    radii = PchipInterpolator(y, r)(dense)
    for i, x in [(4,428),(5,817)]:
        definition = meta['features'][i]['blender_lathe']
        definition['profile'] = np.c_[(cy-dense)*scale, np.full(len(dense),(x-cx)*scale), radii*scale][::-1].tolist()
    # The glass silhouette follows the same smooth frame curve rather than
    # the row-by-row pixel mask used by the first version.
    boundary = np.asarray(meta['features'][1]['blender_curve']['points'])
    rows = np.linspace(boundary[:,1].min()+.003, boundary[:,1].max()-.003, 120)
    centers=[]; widths=[]
    for row in rows:
        hits=[]
        for a,b in zip(boundary,np.roll(boundary,-1,axis=0)):
            if (a[1]<=row<b[1]) or (b[1]<=row<a[1]):
                hits.append(a[0]+(b[0]-a[0])*(row-a[1])/(b[1]-a[1]))
        centers.append((min(hits)+max(hits))/2)
        widths.append((max(hits)-min(hits))/2)
    centers=np.asarray(centers); widths=np.asarray(widths)
    meta['features'][0]['blender_lathe']['profile']=np.c_[rows,centers,widths].tolist()
    dr=np.gradient(widths,rows);dc=np.gradient(centers,rows)
    def glass_surface(xy):
        center=np.interp(xy[:,1],rows,centers)
        width=np.interp(xy[:,1],rows,widths)
        q=np.clip((xy[:,0]-center)/width,-.998,.998)
        root=np.sqrt(1-q*q)
        z=.09+.48*width*root
        dx=-.48*q/root
        dy=.48*(np.interp(xy[:,1],rows,dr)+q*np.interp(xy[:,1],rows,dc))/root
        normal=np.c_[-dx,-dy,np.ones(len(xy))]
        return z,normal/np.linalg.norm(normal,axis=1,keepdims=True)
    def sand(i, image_boundary):
        edge=world(image_boundary)
        if np.cross(edge,np.roll(edge,-1,axis=0)).sum()<0:edge=edge[::-1]
        poly=Polygon(edge)
        lo=edge.min(0);hi=edge.max(0)
        yy,xx=np.meshgrid(np.arange(lo[1]+.02,hi[1],.055),np.arange(lo[0]+.02,hi[0],.055))
        grid=np.c_[xx.ravel(),yy.ravel()];grid=grid[poly.contains_points(grid,radius=-.005)]
        xy=np.r_[edge,grid];tri=Delaunay(xy).simplices
        keep=poly.contains_points(xy[tri].mean(1),radius=.00001)
        for a,b in [(0,1),(1,2),(2,0)]:keep&=poly.contains_points((xy[tri[:,a]]+xy[tri[:,b]])/2,radius=.00001)
        tri=tri[keep]
        area=np.cross(xy[tri[:,1]]-xy[tri[:,0]],xy[tri[:,2]]-xy[tri[:,0]])
        tri[area<0]=tri[area<0][:,[0,2,1]]
        z,n=glass_surface(xy);p=np.c_[xy,z+.018]
        counts=Counter(tuple(sorted(e)) for t in tri for e in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])])
        edges=[(a,b) for t in tri for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])] if counts[tuple(sorted((a,b)))]==1]
        rear=p.copy();rear[:,2]-=.023;count=len(p)
        walls=np.array([(a,count+a,count+b) for a,b in edges]+[(a,count+b,b) for a,b in edges])
        points=np.r_[p,rear];triangles=np.r_[tri,walls]
        normals=np.r_[n[tri],n[walls%count]]
        arrays[f'{i}_points']=points;arrays[f'{i}_triangles']=triangles;arrays[f'{i}_normals']=normals
        meta['features'][i]['front_count']=len(tri);meta['features'][i]['triangles']=len(triangles)
    upper=bezier((494,425),[
        ((581,416),(691,418),(762,409)),((744,466),(689,509),(650,550)),
        ((632,571),(629,593),(626,610)),((622,576),(610,550),(591,530)),
        ((550,497),(512,462),(494,425))])
    lower=bezier((490,831),[
        ((544,812),(586,777),(625,729)),((665,776),(717,812),(762,832)),
        ((684,848),(562,848),(490,831))])
    sand(6,upper);sand(7,lower)
    sand(8,np.array([[624.3,586],[627.7,586],[627.7,743],[624.3,743]]))
    np.savez_compressed(root/'reliefs.npz',**arrays)
    (root/'design.json').write_text(json.dumps(meta,indent=2))
    print(name,'prepared clean glass, supports, sloped sand surface and higher pile')
