"""Fit measured front landmarks under the fixed native camera."""
import numpy as np
class CrownReference:
 def __init__(self,data,groups,image_center_x,base_width_pixels,base_bottom_y):
  self.cx=image_center_x;self.y0=base_bottom_y
  direction=np.array([0.,2.35,23.]);self.distance=float(np.linalg.norm(direction));self.sine=direction[1]/self.distance;self.cosine=direction[2]/self.distance
  points=np.vstack([data[f'{i}_points'] for i,g in enumerate(groups) if g['name']=='Rolled polished gold crown rim'])
  q=self.project(points);self.k=float(np.ptp(q[:,0])/base_width_pixels);self.bottom=float(q[:,1].min())
 def project(self,p):
  y=p[:,1]+.55;z=p[:,2];depth=self.distance-self.sine*y-self.cosine*z
  return np.c_[p[:,0]/depth,(self.cosine*y-self.sine*z)/depth]
 def pixel(self,p):
  q=self.project(np.asarray(p));return np.c_[self.cx+q[:,0]/self.k,self.y0-(q[:,1]-self.bottom)/self.k]
 def surface(self,p,radius=2.75):
  qx=(p[:,0]-self.cx)*self.k;qy=(self.y0-p[:,1])*self.k+self.bottom
  x=qx*self.distance
  for _ in range(12):
   z=np.sqrt(np.maximum(radius*radius-x*x,.10))+.035+p[:,2]
   y=(qy*self.distance+(self.sine-qy*self.cosine)*z)/(self.cosine+qy*self.sine)
   depth=self.distance-self.sine*y-self.cosine*z;x=qx*depth
  y-=.55
  result=np.c_[x,y,z];error=np.max(abs(self.pixel(result)-p[:,:2]));assert error<.002,error
  return result
 def inverse(self,p,z):
  p=np.asarray(p,float);z=np.broadcast_to(z,(len(p),)).astype(float)
  qx=(p[:,0]-self.cx)*self.k;qy=(self.y0-p[:,1])*self.k+self.bottom
  y=(qy*self.distance+(self.sine-qy*self.cosine)*z)/(self.cosine+qy*self.sine)
  depth=self.distance-self.sine*y-self.cosine*z
  return np.c_[qx*depth,y-.55,z]
 def plane_surface(self,p,plane):
  z=np.full(len(p),plane[2]);result=None
  for _ in range(12):
   result=self.inverse(p[:,:2],z);z=result[:,:2]@plane[:2]+plane[2]+p[:,2]
  result=self.inverse(p[:,:2],z)
  assert np.max(abs(self.pixel(result)-p[:,:2]))<.002
  return result
