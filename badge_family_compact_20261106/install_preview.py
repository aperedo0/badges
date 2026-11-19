from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parent;rows=json.loads((ROOT/'manifest.json').read_text());results=json.loads((ROOT/'results.json').read_text());plan=[]
for row in rows:
 for alias in row['aliases']:
  allowed={row['source_sha256']}
  if results[row['key']].get('output_sha256'):allowed.add(results[row['key']]['output_sha256'])
  assert hashlib.sha256(Path(alias['path']).read_bytes()).hexdigest() in allowed,alias['path']
 if results[row['key']]['status']!='validated_candidate':continue
 c=ROOT/'badges'/row['slug']/'candidate01';assert (c/'blender_review.json').exists();assert (ROOT/'badges'/row['slug']/'baseline/loaded_model.json').exists()
 assert hashlib.sha256((c/'model.usdz').read_bytes()).hexdigest()==results[row['key']]['output_sha256']
 for alias in row['aliases']:
  item=dict(key=row['key'],title=row['title'],origin=alias['origin'],target=alias['path'],source=str(c/'model.usdz'),expected_original_sha256=row['source_sha256'],replacement_sha256=results[row['key']]['output_sha256']);plan.append(item)
  if alias['origin']=='preview':shutil.copyfile(c/'model.usdz',alias['path'])
(ROOT/'integration_plan.json').write_text(json.dumps(plan,indent=2)+'\n');print('29 private preview assets updated. Production files preserved.')
