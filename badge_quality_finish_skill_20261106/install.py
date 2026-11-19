"""Install only the four reviewed skill files, guarding against concurrent edits."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parent;manifest=json.loads((ROOT/'manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
for entry in manifest:
 target=Path(entry['target']);current=sha(target.read_bytes()) if target.exists() else None
 assert current in [entry['old_sha256'],entry['new_sha256'],entry.get('previously_installed_sha256')],('Skill changed since review',str(target))
 assert sha((ROOT/entry['proposed']).read_bytes())==entry['new_sha256']
for entry in manifest:
 target=Path(entry['target']);data=(ROOT/entry['proposed']).read_bytes();target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and sha(target.read_bytes())==entry['new_sha256']:continue
 temp=target.with_name(target.name+'.badge_finish_update.tmp');temp.write_bytes(data);os.replace(temp,target)
for entry in manifest:assert sha(Path(entry['target']).read_bytes())==entry['new_sha256']
(ROOT/'validation.json').write_text(json.dumps(dict(installed=True,files_verified=len(manifest),originals_preserved_in='previous',new_run_started=False),indent=2)+'\n');print('Installed and verified four skill files.')
