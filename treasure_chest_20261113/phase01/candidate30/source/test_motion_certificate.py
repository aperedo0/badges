from pathlib import Path
import ast,math,json,numpy as np
source=Path(__file__).with_name('certify_motion26_live.py').read_text();tree=ast.parse(source);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='tri_bound')
ns={'np':np,'Vector':lambda p:p,'guard':lambda:None};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual tri_bound source>','exec'),ns)
class Plane:
 def find_nearest(self,p):return np.array([p[0],p[1],0]),None,None,abs(float(p[2]))
class Sphere:
 def __init__(self,c,r):self.c=np.array(c);self.r=r
 def find_nearest(self,p):
  q=p-self.c;d=np.linalg.norm(q);return self.c+q/d*self.r,None,None,abs(d-self.r)
results={};ns['static']=Plane()
a=np.array([[-.5,0,.2],[.5,0,.2],[0,.5,.2]])
v=ns['tri_bound'](a,.05);assert v is not None and .05<v<=.2;results['clear_plane_triangle_certified']=v
cross=np.array([[-.1,0,-.1],[.1,0,.1],[0,.1,0]])
assert ns['tri_bound'](cross,.001) is None;results['triangle_crossing_plane_rejected']=True
thin=np.array([[-.5,0,.02],[.5,0,.02],[0,.001,.02]])
v=ns['tri_bound'](thin,.004);assert v is not None and .004<v<=.02;results['long_thin_clear_triangle_certified']=v
ns['static']=Sphere([math.cos(math.pi/6),math.sin(math.pi/6),0],.05)
tri=np.array([[1,0,-.0001],[1,.0001,.0001],[1,-.0001,.0001]])
need=2*1.001*math.sin(math.pi/12)+.00001
end=tri@np.array([[.5,-math.sqrt(3)/2,0],[math.sqrt(3)/2,.5,0],[0,0,1]]).T
assert not (ns['tri_bound'](tri,need) is not None and ns['tri_bound'](end,need) is not None)
results['arc_with_clear_endpoints_and_hidden_middle_obstacle_not_certified']=True
p=Path(__file__).parents[1]/'candidate26/certificate_validation.json';p.write_text(json.dumps({'actual_source_function_tested':True,'tests':results},indent=2));print(results)
