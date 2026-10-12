from pathlib import Path
import json,sys,shutil,hashlib,datetime
r=Path(__file__).resolve().parents[1];tier,pose=sys.argv[1:];p=r/'inspection_models/updated'/tier/pose
build=json.loads((p/'build.json').read_text());num=build['changes'][0]['source_candidate']
w=Path(json.loads((r/'manifest.json').read_text())[tier]['work']);out=w/'candidates'/num/'inspection';out.mkdir(exist_ok=True)
shutil.copyfile(p/'app.png',out/(pose+'.png'))
(out/(pose+'_capture.json')).write_text(json.dumps({'candidate':num,'inspection_package_sha256':build['sha256'],'screenshot_sha256':hashlib.sha256((p/'app.png').read_bytes()).hexdigest(),'captured_at':datetime.datetime.now().astimezone().isoformat()},indent=2)+'\n')
