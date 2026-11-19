"""Write the existing profile18 optical integrator for live Blender OSL development."""
from pathlib import Path
import numpy as np,json,sys
R=Path(__file__).resolve().parent;C=R/'sapphire_teardrop'/sys.argv[1];D=np.load(C/'parts.npz');V=D['gem_v'];N=D['gem_n'][:,0];offset=(N*V[:,0]).sum(1);raw=np.c_[N,offset];raw=np.unique(np.round(raw,6),axis=0)
# Merge only numerically coplanar triangles, not neighboring real facet planes.
planes=[]
for row in raw:
 if not any(np.linalg.norm(row[:3]-p[:3])<.00001 and abs(row[3]-p[3])<.00001 for p in planes):planes.append(row)
planes=np.asarray(planes);assert 4<=len(planes)<=256
z=V[...,2];density=min(8,max(.5,1/float(z.max()-z.min())))
F=C/'blender/optics';F.mkdir(exist_ok=True,parents=True)
s=(R/'tools/gem_development.osl').read_text();s=s.replace('SHARP_FILE',str(R/'optics_fit/studio_mip1.exr')).replace('TENT_FILE',str(R/'optics_fit/studio_mip8.exr')).replace('DENSITY_VALUE',format(density,'.10g')).replace('PLANE_COUNT',str(len(planes))).replace('PLANE_VECTORS',','.join('vector('+','.join(format(float(a),'.10g') for a in p[:3])+')' for p in planes)).replace('PLANE_OFFSETS',','.join(format(float(p[3]),'.10g') for p in planes));(F/'sapphire_profile18.osl').write_text(s);np.savez(F/'planes.npz',planes=planes)
(F/'profile.json').write_text(json.dumps(dict(planes=len(planes),density=density,internal_hits=3,exposure=.28,absorption=[8,4.3503597,.2],lighting_only_maps=True,no_reference_or_appearance_image=True,native_parity_review_pending=True),indent=2)+'\n');print('Prepared real ray traced development material',C.name,len(planes),'planes',density)
