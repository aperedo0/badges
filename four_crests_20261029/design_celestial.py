"""Measured geometry for the opposed crescent celestial dial."""
from design_shapes import ROOT,ellipse,tick,setting
import json,math
r=ROOT/'celestial_orbit';gems=[]
for name,cx,cy,rad,spikes in [('North crystal',627,145,32,{0:55,8:84,16:55,24:107}),('West crystal',176,578,35,{0:88,8:56,16:104,24:56}),('East crystal',1072,578,35,{0:107,8:56,16:88,24:56}),('South crystal',627,1008,35,{0:56,8:110,16:56,24:88})]:
 gems.append({'name':name,'center':[cx,cy],'outline':ellipse(cx,cy,rad,rad,32),'seat':.31,'crest':.46,'lens':True,'bezel':{'outline':setting(cx,cy,53,spikes),'seat':.18,'crest':.29,'inner_height':.30,'ridge_fraction':.84}})
star=[[627,458],[670,548],[757,578],[670,620],[627,700],[584,620],[497,578],[584,546]]
frame=[[627,183],[640,434],[677,530],[770,565],[1036,578],[770,591],[677,626],[640,722],[627,973],[614,722],[577,626],[484,591],[212,578],[484,565],[577,530],[614,434]]
gems.append({'name':'Four point faceted star crystal','center':[627,578],'outline':star,'seat':.44,'crest':.68,'bezel':{'outline':frame,'seat':.23,'crest':.40,'inner_height':.43,'ridge_fraction':.86}})
ornaments=[]
for i in range(60):ornaments.append({'outline':tick(627,578,404,i*6-90,31 if i%5==0 else 14,5 if i%5==0 else 2),'seat':.18,'crest':.195})
for cx,cy in [(799,306),(407,538),(447,828)]:ornaments.append({'outline':ellipse(cx,cy,20,20,24),'seat':.24,'crest':.35})
for i in range(16):
 a=2*math.pi*i/16;cx=627+140*math.cos(a);cy=578+140*math.sin(a);ornaments.append({'outline':tick(627,578,154,i*22.5,47,6),'seat':.18,'crest':.20})
regions=[{'outline':ellipse(612,527,296,264),'holes':[ellipse(675,495,263,245)],'seat':.19,'rise':.09,'width':14},{'outline':ellipse(638,574,277,301),'holes':[ellipse(578,529,251,286)],'seat':.21,'rise':.10,'width':14}]
cfg={'name':'Celestial Orbit','threshold':.16,'blue_threshold':.28,'bounds':[72,38,1180,1118],'disc':[627,594,522,510],'min_component':100,'fill_holes':100,'close_iterations':1,'contour_smoothing':.8,'field':True,'keep_support_texture':True,'nonmetal_blue':True,'metal_hue':'silver','regions':regions,'rings':[{'ellipse':[627,594,518,505],'band':.018,'rise':.10},{'ellipse':[627,578,438,423],'band':.028,'rise':.11},{'ellipse':[627,578,214,223],'band':.022,'rise':.09},{'ellipse':[627,578,147,150],'band':.025,'rise':.08}],'gems':gems,'ornaments':ornaments,'facets':[],'gem_texture_size':1024,'details':['Opposed pale blue and deep blue crescent forms','Tall four point faceted crystal in a long silver compass frame','Four independent blue cardinal lens gems and metal settings','Nested silver orbit rings and blue starfield outer band','Raised minute ticks, radial sun marks and three rounded metal studs','Complete matching reverse and continuous silver edge']}
(r/'design.json').write_text(json.dumps(cfg,indent=2)+'\n')
