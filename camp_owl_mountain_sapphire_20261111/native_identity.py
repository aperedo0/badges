"""Check the actual gallery heading, independently of cached model files."""
from pathlib import Path
import json,re,subprocess,time
R=Path(__file__).resolve().parent
AXE='/Users/antonioperedo/.npm/_npx/99336612077b7094/node_modules/xcodebuildmcp/bundled/axe'
UDID='C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8'
def verify(slug,output=None):
 row=next(x for x in json.loads((R/'gallery.json').read_text()) if x['slug']==slug)
 source=R.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift'
 line=next(s for s in source.read_text().splitlines() if 'static let items:' in s)
 names={name for key,name in re.findall(r'"([^"]+)":"([^"]+)"',line)}
 result=subprocess.run([AXE,'describe-ui','--udid',UDID],capture_output=True,text=True,timeout=35,check=True)
 tree=json.loads(result.stdout);headings=[]
 def visit(node):
  if isinstance(node,list):
   for item in node:visit(item)
  elif isinstance(node,dict):
   if node.get('role')=='AXStaticText' and node.get('AXLabel') in names and node.get('frame',{}).get('height',0)>=28:
    headings.append(dict(name=node['AXLabel'],frame=node.get('frame')))
   for child in node.get('children',[]):visit(child)
 visit(tree)
 report=dict(expected=row['name'],observed=headings,epoch=time.time(),visible_gallery_heading_verified=len(headings)==1 and headings[0]['name']==row['name'])
 if output:Path(output).write_text(json.dumps(report,indent=2))
 assert report['visible_gallery_heading_verified'],report
 return report
if __name__=='__main__':
 import sys
 print(json.dumps(verify(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)))
