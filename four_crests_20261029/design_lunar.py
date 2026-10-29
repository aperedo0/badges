"""Reference measured lunar rings, lens gems, crescent and raised clock marks."""
from pathlib import Path
import math,json
ROOT=Path(__file__).resolve().parent

def ellipse(cx,cy,rx,ry,n=96):return [[round(cx+rx*math.cos(2*math.pi*i/n),3),round(cy+ry*math.sin(2*math.pi*i/n),3)] for i in range(n)]
def tick(cx,cy,r,angle,length,width):
 a=math.radians(angle);u=(math.cos(a),math.sin(a));v=(-u[1],u[0]);return [[cx+u[0]*rr+v[0]*w,cy+u[1]*rr+v[1]*w] for rr,w in [(r-length/2,-width/2),(r+length/2,-width/2),(r+length/2,width/2),(r-length/2,width/2)]]
def setting(cx,cy,base,spikes):
 out=[]
 for i in range(32):
  a=2*math.pi*i/32;radius=spikes.get(i,base);out.append([cx+radius*math.cos(a),cy+radius*math.sin(a)])
 return out
r=ROOT/'lunar_compass';gems=[]
for name,cx,cy,radius,base,spikes in [('North sapphire',627,112,39,69,{0:73,8:138,16:73,24:86}),('West sapphire',144,575,42,67,{0:128,8:72,16:102,24:72}),('East sapphire',1109,575,42,67,{0:101,8:72,16:128,24:72}),('South sapphire',627,1060,43,69,{0:73,8:104,16:73,24:128})]:
 gems.append({'name':name,'center':[cx,cy],'outline':ellipse(cx,cy,radius,radius,32),'seat':.31,'crest':.46,'lens':True,'bezel':{'outline':setting(cx,cy,base,spikes),'seat':.19,'crest':.29,'ridge_fraction':.83,'inner_height':.30}})
star=[[715,318],[738,530],[819,473],[760,551],[939,574],[759,597],[817,678],[738,617],[715,812],[692,618],[612,677],[670,597],[489,574],[671,551],[612,474],[692,530]]
gems.append({'name':'Center sapphire and compass','center':[715,574],'outline':ellipse(715,574,44,44,32),'seat':.43,'crest':.59,'lens':True,'bezel':{'outline':star,'seat':.25,'crest':.40,'ridge_fraction':.78,'inner_height':.42}})
ornaments=[]
for i in range(60):
 a=i*6-90;major=i%5==0
 ornaments.append({'outline':tick(627,580,405,a,29 if major else 15,5 if major else 2),'seat':.19,'crest':.205})
for angle in [-112,-68,-22,22,68,112,158,202]:
 a=math.radians(angle);cx=627+367*math.cos(a);cy=580+367*math.sin(a);ornaments.append({'outline':ellipse(cx,cy,9,9,16),'seat':.18,'crest':.26})
for cx,cy in [(309,271),(945,271),(309,880),(945,880)]:
 outline=[[cx,cy-45],[cx+12,cy-12],[cx+45,cy],[cx+12,cy+12],[cx,cy+45],[cx-12,cy+12],[cx-45,cy],[cx-12,cy-12]];ornaments.append({'outline':outline,'seat':.22,'crest':.40})
moon={'outline':ellipse(627,571,334,307),'holes':[ellipse(696,568,260,261)],'seat':.21,'rise':.10,'width':16}
cfg={'name':'Lunar Compass','threshold':.16,'blue_threshold':.27,'bounds':[42,26,1210,1164],'disc':[627,594,544,529],'min_component':100,'fill_holes':100,'close_iterations':1,'contour_smoothing':.8,'field':True,'keep_support_texture':True,'nonmetal_blue':True,'metal_hue':'silver','regions':[moon],'rings':[{'ellipse':[627,594,539,524],'band':.018,'rise':.10},{'ellipse':[627,584,455,437],'band':.038,'rise':.12},{'ellipse':[627,571,331,305],'band':.025,'rise':.10}],'gems':gems,'ornaments':ornaments,'facets':[],'gem_texture_size':1024,'details':['Raised concentric silver rings around a blue constellation band','Five independent closed faceted sapphire lenses and sculpted settings','Raised silver crescent with the reference lunar surface','Long compass points and diagonal rays around the central sapphire','Sixty separate clock ticks, raised studs and four diagonal ornaments','Complete matching reverse and continuous silver side walls']}
(r/'design.json').write_text(json.dumps(cfg,indent=2)+'\n')
