"""Build the reference's complete dark forged hexagon, hammer, flame and anvil."""
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter,distance_transform_edt
import meshlib as m
from pace import work
work(2)
R=Path(__file__).resolve().parent/'ember_forge';m.setup(R,627,32,1203)
outer=np.array([(627,32),(1117,336),(1119,872),(628,1203),(125,874),(125,340)])
inner=np.array([(627,102),(1066,370),(1066,843),(628,1135),(179,844),(179,373)])
m.band('Hammered hexagonal steel case',inner,outer,.15,.31,'metal')
trim_outer=inner.copy();trim_inner=np.array([627,617])+(inner-np.array([627,617]))*.934
m.band('Continuous inset copper hexagon',trim_inner,trim_outer,.20,.25,'copper')
m.solid('Dark forged recessed hexagonal field',trim_inner,.075,.095,'field',inset=.01)
# Two lower ember channels follow the exact slanted sides of the inner frame.
for name,p in [('Left ember channel',[(218,804),(627,1077),(627,1105),(218,836)]),('Right ember channel',[(627,1077),(1025,804),(1025,836),(627,1105)])]:
 m.solid(name,p,.115,.14,'flame',inset=.02)
# Five asymmetric flame tongues, with valleys and hooked tips taken from the picture.
flame=[(470,676),(382,581),(348,548),(345,507),(359,461),(402,402),(393,445),(405,475),(449,508),(429,446),(431,387),(454,331),(495,293),(549,264),(528,309),(531,346),(553,379),(599,339),(659,291),(699,252),(697,218),(741,252),(768,299),(778,346),(765,393),(771,428),(785,453),(811,418),(815,390),(807,363),(856,406),(880,454),(894,498),(894,546),(879,570),(786,674)]
curve=m.smooth_loop(flame,300);mask=m.poly(curve);p,t=m.triangulate_mask(mask,12);dist=gaussian_filter(distance_transform_edt(mask),4)
z=.18+.055*(1-np.exp(-m.map_coordinates(dist,[p[:,1],p[:,0]],order=1)/22))
m.relief('Five carved ember flame tongues',p,t,z,'flame',side_role='ember_side')
# Cylindrical handle, two bright spiral turns and a faceted top cap.
theta=np.linspace(0,2*np.pi,32,endpoint=False);heights=np.linspace(170,508,24);points=[]
for y in heights:
 for a in theta:points.append(m.world([[630+40*np.cos(a),y]],40*m.S*np.sin(a))[0])
faces=[]
for j in range(len(heights)-1):
 for i in range(32):a=j*32+i;b=j*32+(i+1)%32;c=(j+1)*32+i;d=(j+1)*32+(i+1)%32;faces.extend([[a,b,d],[a,d,c]])
faces.extend([[0,i+1,i] for i in range(1,31)]);last=(len(heights)-1)*32;faces.extend([[last,last+i,last+i+1] for i in range(1,31)])
points=np.array(points)
handle_uv=np.c_[((points[:,0]/m.S)+m.CX)/m.W,1-(m.TOP+(3.015-points[:,1])/m.S)/m.H]
m.add('Continuous cylindrical hammer grip',points,np.array(faces),'metal',handle_uv,smooth=True)
# Raised diagonal copper ribbons wrap around the real handle, front and back.
angles=np.linspace(-np.pi/2,6.5*np.pi,224);ribbon=[];ribbon_uv=[]
for a in angles:
 y=186+305*(a+np.pi/2)/(7*np.pi)
 for radius,offset in [(40,0),(43,0),(43,16),(40,16)]:
  xy=[630+radius*np.cos(a),y+offset];ribbon.append(m.world([xy],radius*m.S*np.sin(a))[0]);ribbon_uv.append(m.uv(np.array([xy]))[0])
faces=[]
for j in range(len(angles)-1):
 for i in range(4):a=4*j+i;b=4*j+(i+1)%4;c=a+4;d=b+4;faces.extend([[a,b,d],[a,d,c]])
faces.extend([[0,2,1],[0,3,2]]);n=4*(len(angles)-1);faces.extend([[n,n+1,n+2],[n,n+2,n+3]])
m.add('Continuous raised copper spiral wrapping the handle',np.array(ribbon),faces,'copper',np.array(ribbon_uv),True)
m.solid('Hexagonal hammer pommel',[(596,121),(657,121),(681,137),(681,173),(659,190),(596,190),(575,175),(575,137)],.24,.36,'metal',inset=.11)
m.solid('Hammer neck collar',[(591,491),(661,491),(681,518),(573,518)],.25,.40,'metal',inset=.10)
m.solid('Broad forged hammer head',[(508,515),(749,515),(792,545),(792,640),(774,670),(491,670),(466,643),(466,548)],.56,.65,'metal',inset=.095)
# The horn, waist cutouts and two feet are one coherent anvil silhouette.
anvil=[(242,688),(1001,688),(984,718),(936,746),(846,773),(803,798),(773,836),(757,883),(765,925),(841,925),(857,979),(399,979),(404,929),(433,925),(451,886),(447,840),(431,811),(397,790),(321,764),(273,734)]
m.solid('Single anvil with twin curved waists and feet',anvil,.39,.48,'metal',inset=.04)
for i,p in enumerate([[(257,552),(282,528),(449,659)],[(318,651),(330,628),(434,672)],[(805,660),(971,528),(995,554)],[(818,673),(932,630),(942,653)]]):m.solid('Tapered flying copper spark '+str(i+1),p,.17,.24,'copper',inset=.10)
bezel_outer=np.array([(628,815),(734,932),(628,1066),(522,932)]);bezel_inner=np.array([(628,858),(704,937),(628,1028),(551,937)])
m.band('Lower raised copper diamond surround',bezel_inner,bezel_outer,.49,.64,'copper',ridge=True)
m.solid('Faceted glowing forged ember inset',[(628,890),(705,957),(628,1047),(550,957)],.55,.62,'flame',inset=.015)
# A narrow vertical ridge divides the lower inset into two real planes.
m.solid('Copper ridge on lower inset',[(627,892),(631,896),(631,1044),(627,1047)],.62,.65,'copper',inset=.01)
m.save(dict(name='Ember Forge',selection='emberForge',bounds=[125,32,1119,1203],textured_roles=['metal','copper','field','flame'],metal_roles=['metal','copper'],desired_colors={'metal':[.21,.17,.14],'copper':[.36,.16,.045]},roughness={'metal':.39,'copper':.32,'field':.65,'flame':.6},side_color=[.065,.041,.027],side_roughness=.55,method='Physical beveled hexagon, cut hammer and anvil, curled flame relief, wrapped handle and matching sculpted rear'))
