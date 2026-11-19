"""Explicit private preview fallback while XcodeBuildMCP transport is closed."""
from pathlib import Path
import sys,subprocess,json,time,plistlib,os,hashlib
R=Path(__file__).resolve().parent;U='C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8';BUNDLE='com.antonioperedo.badgestudio.preview';PROJECT=R.parent/'emerald_trophy_20261025/preview/ScreenTime.xcodeproj';DERIVED=Path('/tmp/forge_tide_derived_20261103');APP=DERIVED/'Build/Products/Debug-iphonesimulator/ScreenTimeUI.app'
action,slug,mode=sys.argv[1:4];baseline=os.environ.get('BADGE_BASELINE')=='1';V=R/slug/mode/('review_baseline' if baseline else 'review');V.mkdir(exist_ok=True);row=next(x for x in json.loads((R/'gallery.json').read_text()) if x['slug']==slug)
subprocess.run([sys.executable,str(R/'work_guard.py'),'240' if action=='build' else '120','private native preview fallback',slug],check=True)
if action=='build':
 log=V/('native_build_'+str(int(time.time()))+'.log');args=['xcodebuild','-project',str(PROJECT),'-scheme','ScreenTime-UIOnly','-configuration','Debug','-destination','id='+U,'-derivedDataPath',str(DERIVED),'-disableAutomaticPackageResolution','build']
 with log.open('w') as f:result=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 if result.returncode:print(log.read_text()[-12000:]);raise SystemExit(result.returncode)
 assert plistlib.loads((APP/'Info.plist').read_bytes())['CFBundleIdentifier']==BUNDLE
 subprocess.run(['xcrun','simctl','install',U,str(APP)],check=True)
 (V/'native_build_context.json').write_text(json.dumps(dict(project=str(PROJECT),scheme='ScreenTime-UIOnly',simulator=U,bundle=BUNDLE,derived_data=str(DERIVED),reason='XcodeBuildMCP transport closed',log=str(log),production_untouched=True),indent=2))
 print('Private preview build and install succeeded',flush=True)
# The intentionally persistent console helper follows this preview app, as the
# disconnected official tool did. Its identity is saved for the next launch.
log=V/('native_runtime_'+str(int(time.time()))+'.log');args=['xcrun','simctl','launch','--console-pty','--terminate-running-process',U,BUNDLE,'-hasCompletedOnboarding','YES','-CoinBadgePreview',row['key'],'-BadgePreviewBaseline','YES' if baseline else 'NO','-BadgePreviewClothFinish','NO']
with log.open('w') as handle:console=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=handle,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.5)
if console.poll() is not None and console.returncode!=0:raise RuntimeError(log.read_text())
metadata=dict(log=str(log),console_helper_pid=console.pid,bundle=BUNDLE,simulator=U,selected_badge=row['key'],candidate=mode,cloth_finish_helper=False,method='native fallback while tool transport is closed')
(V/'native_launch.json').write_text(json.dumps(metadata,indent=2));(R/'native_console.json').write_text(json.dumps(metadata,indent=2));print(json.dumps(metadata),flush=True)
subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',str(R/'check_native_gems.py'),slug,mode,str(log)],check=True)
subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',str(R/'native_identity.py'),slug,str(V/'launch_visible_identity.json')],check=True)
container=Path(subprocess.check_output(['xcrun','simctl','get_app_container',U,BUNDLE,'data'],text=True).strip())
cached=container/'tmp'/(row['dataset']+('Baseline' if baseline else '')+'.usdz');model=R/slug/mode/('mobile/'+slug+'_badge_mobile.usdz' if baseline else 'model.usdz')
assert cached.read_bytes()==model.read_bytes(),'Native precheck loaded a different model from the intended candidate'
(V/'native_precheck_model.json').write_text(json.dumps(dict(actual_cached_model_verified=True,candidate=mode,sha256=hashlib.sha256(model.read_bytes()).hexdigest(),cached_model=str(cached)),indent=2))
subprocess.run(['xcrun','simctl','io',U,'screenshot',str(V/'native_front_precheck.png')],check=True,capture_output=True)
subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',str(R/'reference_comparison.py'),slug],env=dict(os.environ,BADGE_CANDIDATE=mode),check=True)
