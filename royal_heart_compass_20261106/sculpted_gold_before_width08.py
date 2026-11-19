"""Closed gold settings and separately layered leaves from measured outlines."""
import numpy as np

def frame(outer,inner,height=.19):
 outer=np.asarray(outer,float);inner=np.asarray(inner,float);assert outer.shape==inner.shape
 N=len(outer);p=[]
 profile=[(0,-.055),(0,.012),(.13,.06),(.40,.105),(.65,.10),(.88,.075),(1,.035),(1,-.055)]
 for weight,z in profile:
  xy=outer*(1-weight)+inner*weight;p.extend(np.c_[xy,np.full(N,z)])
 t=[]
 for ring in range(len(profile)):
  for j in range(N):
   a=ring*N+j;b=ring*N+(j+1)%N;c=((ring+1)%len(profile))*N+(j+1)%N;d=((ring+1)%len(profile))*N+j;t.extend([[a,b,c],[a,c,d]])
 return orient(np.array(p),np.array(t))

def bez(control,s):
 a,b,c,d=np.asarray(control,float);s=s[:,None];return (1-s)**3*a+3*(1-s)**2*s*b+3*(1-s)*s*s*c+s**3*d

def leaf(edge_a,edge_b,height=.14,layer=0,N=48,M=14):
 s=np.linspace(0,1,N);a=bez(edge_a,s);b=bez(edge_b,s)
 # A closed smooth shell with a broad curved face and a subtle raised midrib.
 p=[]
 for back in [False,True]:
  for j in range(N):
   for u in np.linspace(0,1,M):
    xy=a[j]*(1-u)+b[j]*u;dome=np.sin(np.pi*u)**.8*np.sin(np.pi*s[j])**.65
    z=layer+(.025+height*dome if not back else -.055-.025*dome)
    p.append([*xy,z])
 t=[];K=N*M
 for j in range(N-1):
  for k in range(M-1):
   aa=j*M+k;bb=aa+1;cc=aa+M+1;dd=aa+M;t.extend([[aa,bb,cc],[aa,cc,dd],[aa+K,cc+K,bb+K],[aa+K,dd+K,cc+K]])
 boundary=list(range(M))+[j*M+M-1 for j in range(1,N)]+list(range(K-2,K-M-1,-1))+[j*M for j in range(N-2,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):t.extend([[a,b+K,b],[a,a+K,b+K]])
 # Coincident root and tip edges are welded geometrically before export.
 p=np.array(p);t=np.array(t);unique,inv=np.unique(np.round(p,9),axis=0,return_inverse=True);t=inv[t];valid=(t[:,0]!=t[:,1])&(t[:,1]!=t[:,2])&(t[:,2]!=t[:,0]);t=t[valid]
 return orient(unique,t)

def orient(p,t):
 # Inputs are reference pixels with downward Y. The caller reverses Y.
 v=np.sum(np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])))/6
 if v>0:t=t[:,::-1]
 return p,t

def central_leaves():
 return [
  ([[730,690],[710,592],[686,507],[594,521]],[[730,690],[690,590],[633,580],[594,521]],.16,.04),
  ([[729,691],[656,535],[521,515],[552,650]],[[729,691],[685,618],[593,574],[552,650]],.22,.00),
  ([[728,684],[710,713],[630,717],[588,711]],[[728,684],[705,690],[635,708],[588,711]],.10,.035),
  ([[588,711],[669,711],[699,678],[682,653]],[[588,711],[660,706],[678,683],[682,653]],.08,.06),
 ]

def top_leaves():
 return [
  ([[754,275],[721,206],[615,183],[562,252]],[[754,275],[713,218],[610,207],[562,252]],.15,.015),
  ([[751,272],[724,195],[648,165],[601,197]],[[751,272],[724,223],[657,189],[601,197]],.13,-.05),
  ([[747,276],[695,209],[611,207],[616,269]],[[747,276],[705,231],[625,225],[616,269]],.13,.06),
 ]
