"""Correct measured brow overlaps, feather tips and sky arc instead of hiding shape misses in color maps."""
from pathlib import Path
import json,copy,sys,numpy as np,shapely
from shapely.geometry import Polygon
sys.path.insert(0,str(Path(__file__).resolve().parent));from designs import path,shape,mirror,stroke,ellipse
R=Path(__file__).resolve().parent;B=R/'amber_owl';C=B/'candidate07';assert not (C/'parts.npz').exists();C.mkdir(exist_ok=True);spec=json.loads((B/'PIECES.json').read_text());original={p['name']:p for p in spec['pieces']};pieces=spec['pieces']
opening=ellipse(626,604.5,586,582.5).buffer(-54)
# Measured points from the actual upper gold wire, with the star hiding its center.
arc=np.c_[626+441.227873*np.cos(np.linspace(np.pi*1.18,np.pi*1.82,220)),626.285226+441.227873*np.sin(np.linspace(np.pi*1.18,np.pi*1.82,220))]
original['upper_star_arc']['outline']=shape(stroke(arc,7))
# The original model ended these feathers in the gold band, below their reference tips.
outer=path('M 432 763 C 382 787 353 836 365 887 C 375 925 394 950 415 978 C 404 914 418 845 451 796 Z')
inner=path('M 507 783 C 464 798 428 829 420 877 C 412 936 468 982 615 1090 C 553 1008 503 922 515 814 Z')
center=path('M 626 785 C 572 779 518 827 512 894 C 502 970 548 1051 626 1126 C 704 1051 750 970 740 894 C 734 827 680 779 626 785 Z')
for name,g in [('outer_left_feather',outer),('outer_right_feather',mirror(outer)),('inner_left_feather',inner),('inner_right_feather',mirror(inner)),('central_cream_breast',center)]:
 p=original[name];p['outline']=shape(g)
 for cell in p.get('cells',[]):cell['shape']=shape(g)
# A broad ear with a cream outer cell sits beneath a separate sweeping cream brow.
from scipy.interpolate import CubicSpline
def cubic(a,b,c,d,n=100):
 t=np.linspace(0,1,n)[:,None];return (1-t)**3*np.array(a)+3*(1-t)**2*t*np.array(b)+3*(1-t)*t*t*np.array(c)+t**3*np.array(d)
# Gold ridge centers measured directly in vertical image profiles, with the outer edge3px above.
measured=np.array([[368,346],[380,350],[400,357.5],[420,365],[440,374.5],[460,385.5],[480,398],[500,413],[520,430.5],[540,453],[550,465],[560,480],[570,498],[580,518],[590,548],[600,577],[610,612],[620,635],[626,642]],float)
spline=CubicSpline(measured[:,0],measured[:,1]-3,bc_type='natural');xs=np.linspace(368,626,260);upper=np.c_[xs,spline(xs)]
ear=Polygon(np.concatenate([cubic([256,210],[252,274],[281,302],[368,343]),upper[1:],[[383,476]],cubic([383,476],[309,467],[258,453],[229,429])[1:],cubic([229,429],[194,390],[214,281],[256,210])[1:]]))
assert ear.is_valid
cream=path('M 256 210 C 244 246 239 270 248 300 C 252 340 270 378 296 403 C 322 437 350 459 383 476 C 309 467 258 453 229 429 C 194 390 214 281 256 210 Z').intersection(ear)
brow=path('M 320 418 C 365 447 399 455 447 469 C 530 491 595 540 626 640 L 586 700 C 576 648 550 596 501 565 C 455 536 411 521 371 484 C 343 457 328 436 320 418 Z')
new=[]
for side,eg,cg,bg in [('left',ear,cream,brow),('right',mirror(ear),mirror(cream),mirror(brow))]:
 base=copy.deepcopy(original[side+'_cream_brow_blade']);base['name']=side+'_amber_ear_with_cream_edge';base['outline']=shape(eg);base['cells']=[dict(material='EnamelOwlCream',shape=shape(cg)),dict(material='EnamelOwlAmber',shape=shape(eg.difference(cg)))];base['lines']=dict(width=4,height=.015,material='Gold');base['bevel']=dict(width=4,height=.016);base['rim']=dict(width=2,height=0,material='Gold');base.pop('base',None);new.append(base)
 leaf=copy.deepcopy(base);leaf['name']=side+'_sweeping_cream_brow';leaf['outline']=shape(bg);leaf['cells']=[dict(material='EnamelOwlCream',shape=shape(bg))];leaf.pop('lines',None);leaf['top']=dict(kind='flat',height=.045,dome=0);new.append(leaf)
ring=original['outer_gold_setting'];ring['outline']=shape(ellipse(626,604.5,586,582.5).difference(opening));ring['base']=.09
pieces=[p for p in pieces if p['name'] not in ['outer_gold_setting','left_cream_brow_blade','right_cream_brow_blade']]
# Metal frame is behind the ear tips. Other bird parts end at the measured opening.
pieces.insert(1,ring)
for p in pieces:
 n=p['name']
 if n in ['left_amber_wing','right_amber_wing']:
  g=shapely.union_all([Polygon(a['exterior'],a.get('holes',[])) for a in p['outline']]).intersection(opening.buffer(2));p['outline']=shape(g)
  for cell in p.get('cells',[]):cell['shape']=shape(g)
 if n.endswith('_dark_pupil'):p['top']['dome']=.085
 if n=='blue_enamel_backplate':role='EnamelOwlBlue'
 elif n=='top_four_point_star':role='EnamelOwlLemon'
 elif any(k in n for k in ['amber','beak']):role='EnamelOwlAmber'
 else:role='EnamelOwlCream'
 for cell in p.get('cells',[]):
  if cell['material']=='Enamel':cell['material']=role
 if p.get('material')=='Enamel':p['material']=role
idx=next(i for i,p in enumerate(pieces) if p['name']=='central_gold_beak');pieces[idx:idx]=new
for piece in pieces:
 if piece['name'] in ['blue_enamel_backplate','head_amber_disc','cream_face_mask']:piece['no_clip']=True
 if piece['name'].endswith('amber_ear_with_cream_edge'):piece['base']=.3868233072528889
 if piece['name'].endswith('sweeping_cream_brow'):piece['base']=.4381456269911629
spec['pieces']=pieces;spec['validate_order']=[p['name'] for p in pieces];(C/'PIECES.json').write_text(json.dumps(spec,indent=1)+'\n');cfg=json.loads((B/'candidate06/enamel_config.json').read_text());(C/'enamel_config.json').write_text(json.dumps(cfg,indent=2)+'\n')
(C/'shape_changes.json').write_text(json.dumps(dict(measured_sky_arc_center_y=626.285226,measured_sky_arc_radius=441.227873,old_arc_center_y=636,old_arc_radius=426,main_feather_tip_from=1162,main_feather_tip_to=1126,inner_feather_tips='Finish underneath the central breast rather than protruding into the gold border',brows='Measured broad amber ear with cream outer cell, plus independent sweeping cream brow on top, both mirrored',frame='54 pixel measured band behind the ear tips, with fixed base0.09 and body contours inside its opening',reference_overlay_review_pending=True),indent=2)+'\n');print('Prepared measured Owl07 with',len(pieces),'stacked pieces')
