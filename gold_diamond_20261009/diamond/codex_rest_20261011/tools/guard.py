from pathlib import Path
import sys, shutil, json, hashlib, subprocess
ROOT=Path(__file__).resolve().parents[1]
REPO=Path("/Users/antonioperedo/Desktop/screen_time")
FILES=["ScreenTime/Sources/App/Features/Badges/BadgeGemSurface.metal","ScreenTime/Sources/App/Features/Badges/BadgeHeroCard.swift","ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModelDiamond.dataset/diamond_badge_mobile.usdz","ScreenTime.xcodeproj/project.pbxproj"]
PROJECT_BEFORE=ROOT/'project_before_build.pbxproj'
OWNED_STAGE=ROOT/'owned_stage.json'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def project_semantics(path):
    data=json.loads(subprocess.check_output(['plutil','-convert','json','-o','-',str(path)]))
    def normalized(value):
        if isinstance(value,dict):
            return {k:sorted(v) if k in ['children','files'] and isinstance(v,list) else normalized(v) for k,v in value.items()}
        if isinstance(value,list): return [normalized(v) for v in value]
        return value
    return normalized(data)
def restore():
    owned=json.loads(OWNED_STAGE.read_text()) if OWNED_STAGE.exists() else {}
    for name in FILES[:3]:
        src=ROOT/"original"/name; dst=REPO/name
        if src.read_bytes()!=dst.read_bytes():
            if digest(dst)!=owned.get(name):
                raise RuntimeError('External Diamond edit detected; preserved without overwriting: '+name)
            shutil.copy2(src,dst)
    if PROJECT_BEFORE.exists():
        project=REPO/FILES[3]
        if project_semantics(project)==project_semantics(PROJECT_BEFORE):
            if project.read_bytes()!=PROJECT_BEFORE.read_bytes(): shutil.copy2(PROJECT_BEFORE,project)
        else: print('Concurrent project semantics changed; preserved current project.')
        PROJECT_BEFORE.unlink()
    if OWNED_STAGE.exists(): OWNED_STAGE.unlink()
if sys.argv[1]=="restore": restore(); print("original bytes restored")
elif sys.argv[1]=="stage":
    restore()
    shutil.copy2(REPO/FILES[3],PROJECT_BEFORE)
    candidate=Path(sys.argv[2])
    for name in FILES[:3]:
        src=candidate/Path(name).name
        if src.exists(): shutil.copy2(src,REPO/name)
    OWNED_STAGE.write_text(json.dumps({name:digest(REPO/name) for name in FILES[:3]},indent=2))
    print("staged",candidate)
elif sys.argv[1]=="verify":
    d=json.loads((ROOT/"repo_before.json").read_text())
    paths={}
    for p in REPO.rglob("*"):
        if p.is_file() and ".git" not in p.relative_to(REPO).parts:
            paths[str(p.relative_to(REPO))]=hashlib.sha256(p.read_bytes()).hexdigest()
    errors=[]
    external_additions=[".claude/plans/2026-10-11-extension-icon-catalog.md"]
    for k in set(paths)|set(d["files"]):
        if k in external_additions and k not in d["files"]: continue
        if paths.get(k)!=d["files"].get(k): errors.append(k)
    for key,cmd in [("head",["git","rev-parse","HEAD"]),("branch",["git","branch","--show-current"]),("status",["git","status","--porcelain=v1"] )]:
        if subprocess.check_output(cmd,cwd=REPO,text=True)!=d[key]: errors.append(key)
    print(json.dumps({"files":len(paths),"original_files_verified":len(d["files"]),"differences":errors,"external_additions_preserved":[k for k in external_additions if k in paths]},indent=2))
    assert not errors
