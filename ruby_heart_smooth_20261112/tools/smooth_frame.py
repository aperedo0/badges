from pathlib import Path
import importlib.util, numpy as np
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'ruby_heart_claude_20261107/candidate06'
spec=importlib.util.spec_from_file_location('original_frame',ROOT.parent/'ruby_heart_claude_20261107/tools/build_geometry.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
old_ring=b.ring

def smooth_ring(offset):
    q=old_ring(offset).copy()
    start=np.flatnonzero(q[:,0]<-.24)[0]
    end=np.flatnonzero(q[:,0]<-1.30)[0]
    # Match position, tangent and curvature at each end of the shoulder.
    # The middle is one smooth polynomial instead of an offset cusp.
    xa,xb=q[start,0],q[end,0]; dx=xb-xa
    constraints=[]
    for j in (start,end):
        lo,hi=(max(0,j-5),j+1) if j==start else (j,min(len(q),j+6))
        p=np.polynomial.Polynomial.fit(q[lo:hi,0],q[lo:hi,1],3).convert()
        constraints += [q[j,1],p.deriv()(q[j,0])*dx,p.deriv(2)(q[j,0])*dx*dx]
    A=np.array([[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,2,0,0,0],
                [1,1,1,1,1,1],[0,1,2,3,4,5],[0,0,2,6,12,20]],float)
    c=np.linalg.solve(A,constraints)
    xx=np.linspace(xa,xb,2000);tt=(xx-xa)/dx
    yy=np.polynomial.polynomial.polyval(tt,c)
    samples,_=b.resample(np.c_[xx,yy],end-start+1)
    q[start:end+1]=samples
    return q

def make():
    b.ring=smooth_ring
    v,n,u,t=b.frame();t=b.orient(v,n,t)
    d=dict(np.load(SOURCE/'geometry.npz'))
    d.update(frame_v=v,frame_n=n,frame_uv=u,frame_t=t)
    return d

if __name__=='__main__':
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    d=make();np.savez(ROOT/'candidate01/geometry.npz',**d)
    fig,ax=plt.subplots(figsize=(10,5))
    for o in [0,.1664,.26,.312,.3744,.39]:
        a=old_ring(o);q=smooth_ring(o)
        ax.plot(a[:,0],a[:,1],alpha=.4,linestyle='--');ax.plot(q[:,0],q[:,1])
    ax.set(xlim=(-1.5,-.1),ylim=(2.05,3.05));ax.set_aspect('equal');fig.savefig(ROOT/'candidate01/curve_comparison.png',dpi=180)
    seat=old_ring(.39);new=smooth_ring(.39)
    full=lambda q: np.vstack([q,q[-2:0:-1]*[-1,1]])
    oldpoly=Polygon(full(seat)).buffer(0);newpoly=Polygon(full(new)).buffer(0)
    print('new hole outside old seat area',newpoly.difference(oldpoly).area)
    old=dict(np.load(SOURCE/'geometry.npz'))
    print('max displacement',np.linalg.norm(d['frame_v']-old['frame_v'],axis=1).max())
    print('gem exact',all(np.array_equal(d[k],old[k]) for k in old if k.startswith('gem_')))
