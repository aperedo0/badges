"""Closed leaf relief with outlines measured on the owner's crown image."""
import numpy as np
from sculpted_gold import leaf

CIRCLET=[
 ([[749,857],[708,764],[636,735],[564,777]],[[749,857],[708,785],[631,754],[564,777]],.12,.025),
 ([[564,777],[499,811],[457,846],[365,827]],[[564,777],[509,841],[457,846],[365,827]],.10,.015),
 ([[705,793],[657,758],[611,754],[601,790]],[[705,793],[660,775],[622,766],[601,790]],.13,.045),
 ([[675,775],[625,751],[553,757],[570,806]],[[675,775],[623,765],[573,777],[570,806]],.12,.065),
 ([[595,764],[550,776],[523,821],[550,834]],[[595,764],[556,793],[536,821],[550,834]],.11,.035),
 ([[550,834],[556,834],[562,829],[561,825]],[[550,834],[555,829],[557,829],[561,825]],.045,.035),
 ([[716,809],[665,757],[626,773],[650,810]],[[716,809],[668,786],[646,786],[650,810]],.12,.055),
 ([[730,829],[710,795],[687,794],[681,811]],[[730,829],[706,807],[690,804],[681,811]],.09,.075),
]
ARCH=[
 ([[402,523],[351,453],[347,381],[493,312]],[[402,523],[365,452],[361,389],[493,312]],.065,.012),
 ([[399,509],[410,450],[432,440],[438,496]],[[399,509],[419,455],[430,461],[438,496]],.08,.025),
 ([[372,449],[348,411],[353,375],[375,383]],[[372,449],[366,409],[367,385],[375,383]],.09,.045),
 ([[377,469],[383,420],[425,414],[411,444]],[[377,469],[397,432],[413,427],[411,444]],.10,.035),
 ([[371,438],[388,389],[447,368],[423,410]],[[371,438],[405,388],[427,393],[423,410]],.11,.05),
 ([[375,421],[389,370],[460,362],[442,342]],[[375,421],[420,372],[439,376],[442,342]],.10,.035),
 ([[393,373],[405,343],[457,329],[449,346]],[[393,373],[421,342],[449,336],[449,346]],.09,.055),
 ([[414,354],[431,330],[468,338],[467,326]],[[414,354],[450,330],[468,333],[467,326]],.075,.045),
 ([[445,331],[465,307],[492,303],[515,297]],[[445,331],[485,314],[505,305],[515,297]],.07,.025),
]

def circlet_leaves():
 for aa,bb,height,layer in CIRCLET:
  yield leaf(aa,bb,height,layer,N=40,M=10,camber=.40)

def arch_leaves():
 for aa,bb,height,layer in ARCH:
  yield leaf(aa,bb,height,layer,N=36,M=9,camber=.38)

def map_arch(p,profile,pts,normals,across,radius,base,hub,side_sign):
 # Closest point on the measured band centerline supplies arc distance and
 # crosswise distance. Only relief geometry is derived from the image.
 screen=np.c_[768-profile[:,0]/(radius*1.01)*347,286+(hub+.055-profile[:,1])/(hub+.055-base-.25)*426]
 edge=np.diff(screen,axis=0);den=(edge*edge).sum(1)
 relative=p[:,None,:2]-screen[None,:-1,:]
 fraction=np.clip((relative*edge[None,:,:]).sum(2)/den[None,:],0,1)
 nearest=screen[None,:-1,:]+fraction[:,:,None]*edge[None,:,:]
 distance=((p[:,None,:2]-nearest)**2).sum(2);segments=distance.argmin(1);w=fraction[np.arange(len(p)),segments]
 tangents=edge[segments]/np.sqrt(den[segments,None]);cross=np.c_[-tangents[:,1],tangents[:,0]]
 offset=((p[:,:2]-nearest[np.arange(len(p)),segments])*cross).sum(1)
 def interp(a):return a[segments]*(1-w[:,None])+a[segments+1]*w[:,None]
 result=interp(pts)+interp(across)*offset[:,None]*.0047*side_sign+interp(normals)*(p[:,2,None]+.063)
 return result
