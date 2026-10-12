"""Temporary Silver-slot preview. Always restore after build/install, even on failure.
Only the existing USDZ file may be changed. No app source changes.
"""
from pathlib import Path
import subprocess,json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
APP=Path('/Users/antonioperedo/Desktop/screen_time')
ASSETS={}
for kind,tier in [('diamond','Silver'),('gold','Copper')]:
    ds=APP/('ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModel'+tier+'.dataset')
    filename=json.loads((ds/'Contents.json').read_text())['data'][0]['filename']
    ASSETS[kind]=ds/filename
BACKUP=ROOT/'source/app_asset_before.usdz'
BEFORE=ROOT/'source/app_repo_before.json'
ACTIVE=ROOT/'source/active_trial.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=APP)
def snapshot():
    paths=git('ls-files','-z').decode().split('\0')
    return dict(head=git('rev-parse','HEAD').decode().strip(),branch=git('branch','--show-current').decode().strip(),status=git('status','--porcelain=v1','--untracked-files=all').decode(),files={p:sha(APP/p) for p in paths if p and (APP/p).is_file()})
action=sys.argv[1]
if action=='stage':
    assert not ACTIVE.exists(),'Restore the active test first.'
    folders={kind:ROOT/kind/(sys.argv[3] if kind=='diamond' and len(sys.argv)>3 else sys.argv[2]) for kind in ASSETS}
    if not BEFORE.exists():
        BEFORE.write_text(json.dumps(snapshot(),indent=2)+'\n')
        for kind,asset in ASSETS.items():shutil.copy2(asset,ROOT/'source'/f'{kind}_asset_before.usdz')
    for kind,asset in ASSETS.items():
        assert sha(asset)==sha(ROOT/'source'/f'{kind}_asset_before.usdz'),'Dataset changed externally.'
    ACTIVE.write_text(json.dumps({k:str(v) for k,v in folders.items()}))
    try:
        for kind,asset in ASSETS.items():shutil.copy2(folders[kind]/'badge.usdz',asset)
    except BaseException:
        for kind,asset in ASSETS.items():shutil.copy2(ROOT/'source'/f'{kind}_asset_before.usdz',asset)
        ACTIVE.unlink(missing_ok=True)
        raise
    print('STAGED',folders)
elif action=='restore':
    folders=json.loads(ACTIVE.read_text()) if ACTIVE.exists() else {'proof':str(ROOT/'proof')}
    for kind,asset in ASSETS.items():
        backup=ROOT/'source'/f'{kind}_asset_before.usdz'
        if sha(asset)!=sha(backup):shutil.copy2(backup,asset)
        assert asset.read_bytes()==backup.read_bytes()
    baseline=json.loads(BEFORE.read_text());after=snapshot()
    assert baseline==after,'App repository changed; inspect before and after snapshots.'
    report={'restored_byte_for_byte':True,'all_tracked_file_hashes_unchanged':True,'tracked_files':len(after['files']),'head':after['head'],'branch':after['branch'],'status':after['status'],'asset_hashes':{kind:sha(asset) for kind,asset in ASSETS.items()}}
    for trial in folders.values():
        folder=Path(trial);folder.mkdir(exist_ok=True);(folder/'app_restore_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    ACTIVE.unlink(missing_ok=True)
    print('RESTORED: both assets and',len(after['files']),'tracked files are byte-for-byte unchanged')
