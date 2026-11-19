from pathlib import Path
import json,sys,subprocess
import numpy as np
R=Path(__file__).resolve().parent
slug,candidate=sys.argv[1:3];B=R/slug;C=B/candidate;M=json.loads((C/'parts.json').read_text());D=np.load(C/'parts.npz')
P=np.concatenate([D[p['name']+'_v'].reshape(-1,3) for p in M['parts']]);eye=np.array([0,1.8,23.]);axis=np.array([0,-2.35,-23.]);axis/=np.linalg.norm(axis);up=np.cross([1,0,0],axis);delta=P-eye;depth=delta@axis;xy=np.c_[603+1762.5*delta[:,0]/depth,633.3-1762.5*(delta@up)/depth]
build_box=[603,float(xy[:,1].min()),float(xy[:,1].max())]
boxes=dict(campfire_night=[621,84,1160],amber_owl=[626,22,1187],radiant_mountain=[626,64,1200],sapphire_teardrop=[626,138,1027])
regions=dict(campfire_night=[['moon and stars',-.28,0,.28,.3],['flame',-.26,.25,.26,.78],['left trees',-.49,.25,-.22,.7],['right trees',.22,.25,.49,.7],['logs and stones',-.4,.7,.4,1.01],['rim',-.53,.15,-.36,.8]],amber_owl=[['star and brow',-.38,.03,.38,.55],['eyes and beak',-.3,.4,.3,.73],['left wing',-.45,.58,-.12,.91],['right wing',.12,.58,.45,.91],['breast feathers',-.28,.68,.28,.99],['rim',-.51,.12,-.38,.8]],radiant_mountain=[['sun and rays',-.33,.03,.33,.4],['peaks',-.3,.23,.3,.63],['clouds',-.47,.25,.47,.45],['hills',-.42,.5,.42,.77],['laurel',-.42,.52,.42,.94],['bottom star',-.17,.79,.17,1.01]],sapphire_teardrop=[['upper point',-.18,0,.18,.3],['left facets',-.36,.25,0,.82],['right facets',0,.25,.36,.82],['central table',-.22,.32,.22,.8],['bottom facets',-.31,.72,.31,.98],['gold frame',-.4,.4,-.23,.85]])
gallery=json.loads((R/'gallery.json').read_text());row=next(q for q in gallery if q['slug']==slug)
poses={k:str(C/'app'/(k+'.png')) for k in ['early_turn','side_left','back','side_right'] if (C/'app'/(k+'.png')).exists()}
cfg=dict(name=row['name'],mockup=str(B/'reference.png'),mockup_box=boxes[slug],build_front=str(C/'app/front.png'),build_box=build_box,regions=regions[slug],poses=poses,intended=[])
(C/'review.json').write_text(json.dumps(cfg,indent=2)+'\n')
subprocess.run([sys.executable,'/Users/antonioperedo/.codex/skills/badge-fresh-review/scripts/review_pack.py',str(C/'review.json'),str(C/'review')],check=True)
files=['finish_full_size.png',*['finish_2x_'+str(i)+'.png' for i in range(1,5)],'finish_4x.png','turns.png']
(C/'review/finish_brief.md').write_text('Open all the listed pictures in one step. Review surface finish only. List every defect you see, including fine bright specks, jagged edges, mottling, seams and crawling edges in the turns. Do not rate reference closeness. Reply SHIPPABLE: yes or no, followed by all visible defects and locations.\n\n'+'\n'.join(str(C/'review'/f) for f in files)+'\n')
print(build_box)
