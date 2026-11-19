"""Capture one settled measured pose, checkpointing each successful view."""
from pathlib import Path
import sys,subprocess,json,hashlib,os
from native_pose import header_y,stable_shot,reset,AXE,UDID
from native_identity import verify
R=Path(__file__).resolve().parent;slug,mode,pose=sys.argv[1:4];baseline=os.environ.get('BADGE_BASELINE')=='1';V=R/slug/mode/('review_baseline' if baseline else 'review');V.mkdir(exist_ok=True);model=R/slug/mode/('mobile/'+slug+'_badge_mobile.usdz' if baseline else 'model.usdz');row=next(x for x in json.loads((R/'gallery.json').read_text()) if x['slug']==slug)
subprocess.run([sys.executable,str(R/'work_guard.py'),'120','single native badge pose',slug],check=True)
poses=dict(front=0,early_turn=68,side_left=94.2528,back=132.5056,side_right=170.7583,full_turn=200);delta=poses[pose];alignment_file=V/'pose_alignment.json';checks=json.loads(alignment_file.read_text()) if alignment_file.exists() else {}
try:
 verify(slug,V/(pose+'_identity_before.json'))
 reset(V/'rest_for_pose.png');rest=header_y(V/'rest_for_pose.png')
 if pose=='front':stable_shot(V/'front.png');checks['front']=dict(actual_header_y=header_y(V/'front.png'),reference_header_y=rest)
 else:
  reference=checks.get('front',{}).get('actual_header_y',rest);target=reference-delta*3
  subprocess.run([AXE,'swipe','--start-x','200','--start-y','600','--end-x','200','--end-y',str(600-delta-10),'--duration','1','--delta','2','--udid',UDID],check=True,capture_output=True,timeout=25)
  stable_shot(V/(pose+'.png'));history=[]
  for _ in range(8):
   actual=header_y(V/(pose+'.png'));history.append(actual)
   if abs(actual-target)<=1.5:break
   correction=(actual-target)/3;correction+=10 if correction>0 else -10
   subprocess.run([AXE,'swipe','--start-x','200','--start-y','600','--end-x','200','--end-y',str(600-correction),'--duration','1','--delta','1','--udid',UDID],check=True,capture_output=True,timeout=25);stable_shot(V/(pose+'.png'))
  else:raise RuntimeError(('Pose did not align',pose,target,history))
  checks[pose]=dict(target_header_y=target,actual_header_y=actual,history=history)
 verify(slug,V/(pose+'_identity_after.json'))
 alignment_file.write_text(json.dumps(checks,indent=2)+'\n')
 container=Path(subprocess.check_output(['xcrun','simctl','get_app_container',UDID,'com.antonioperedo.badgestudio.preview','data'],text=True).strip());cached=container/'tmp'/(row['dataset']+('Baseline' if baseline else '')+'.usdz');assert cached.read_bytes()==model.read_bytes(),'Actual model cache differs'
 status=dict(actual_model_verified=True,visible_gallery_heading_verified=True,expected_badge=row['name'],capture_version=5,sha256=hashlib.sha256(model.read_bytes()).hexdigest(),completed_poses=[p for p in poses if p in checks],all_six_measured_poses_complete=all(p in checks for p in poses))
 (V/'pose_capture_status.json').write_text(json.dumps(status,indent=2)+'\n')
 if status['all_six_measured_poses_complete']:(V/'loaded_model.json').write_text(json.dumps(status,indent=2)+'\n')
 print(slug,mode,pose,'settled and actual cached model verified')
except (subprocess.CalledProcessError,subprocess.TimeoutExpired) as error:
 (V/'last_capture_error.json').write_text(json.dumps(dict(pose=pose,error=str(error),stdout=str(error.stdout),stderr=str(error.stderr)),indent=2));raise
