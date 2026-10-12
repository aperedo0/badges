import sys,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[1];number=int(sys.argv[1]);d=r/f'iterations/{number:02d}'
assert 1<=number<=8 and not d.exists(),d
d.mkdir()
for name in ['scripts','source']:
 shutil.copytree(r/name,d/name,ignore=shutil.ignore_patterns('__pycache__'))
for name in ['scenes','reports','proof/renders','mobile/textures','work','logs']:(d/name).mkdir(parents=True,exist_ok=True)
# Relative scripts locate their own package; frozen v3 and references are read-only links.
(d/'previous').symlink_to(r/'previous',target_is_directory=True)
(d/'app_reference').symlink_to(r/'app_reference',target_is_directory=True)
(d/'work/analysis_env').symlink_to(r/'work/analysis_env',target_is_directory=True)
for name in ['original_checksums.json','v3_archive.json']:
 shutil.copy2(r/'reports'/name,d/'reports'/name)
print(d)
