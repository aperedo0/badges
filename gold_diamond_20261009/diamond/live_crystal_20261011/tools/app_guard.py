from pathlib import Path
import sys, json, hashlib, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
asset=Path('/Users/antonioperedo/Desktop/screen_time/ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModelDiamond.dataset/diamond_badge_mobile.usdz')
source=ROOT/'source/installed.usdz'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected=json.loads((ROOT/'sources.json').read_text())['installed']['sha256']
assert sha(source)==expected
if sys.argv[1]=='stage':
    assert sha(asset)==expected, 'Installed Diamond changed externally; do not replace it.'
    candidate=Path(sys.argv[2]);assert candidate.exists()
    assert sha(candidate)==json.loads((candidate.parent/'build.json').read_text())['sha256']
    shutil.copyfile(candidate,asset)
    print('Staged Diamond preview only.')
elif sys.argv[1]=='restore':
    shutil.copyfile(source,asset)
    assert sha(asset)==expected
    print('Original Diamond asset restored byte for byte.')
elif sys.argv[1]=='verify':
    repo=asset.parents[4]
    before=json.loads((ROOT/'repo_before.json').read_text())
    for key,args in {'head':['rev-parse','HEAD'],'branch':['branch','--show-current'],'status':['status','--porcelain']}.items():
        value=subprocess.check_output(['git','-C',str(repo),*args],text=True)
        assert value==before[key], key
    changed=[]
    for name,digest in before['files'].items():
        p=repo/name
        if not p.exists() or sha(p)!=digest:changed.append(name)
    assert not changed,changed
    result={'source_files_unchanged':True,'file_count':len(before['files']),'diamond_restored':sha(asset)==expected}
    (ROOT/'repo_verified.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)
else:raise ValueError(sys.argv[1])
