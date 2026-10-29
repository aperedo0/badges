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
