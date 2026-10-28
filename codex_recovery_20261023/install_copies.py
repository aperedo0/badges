import hashlib
import json
import pathlib


root = pathlib.Path(__file__).resolve().parent
mapping = json.loads((root / 'resume_mapping.json').read_text())
allowed = pathlib.Path.home() / '.codex/sessions'
plan = []
for row in mapping:
    source = root / 'resume_copies' / row['file']
    target = pathlib.Path(row['native_destination'])
    assert target.is_relative_to(allowed)
    content = source.read_bytes()
    meta = json.loads(content.splitlines()[0])
    assert meta['type'] == 'session_meta'
    assert meta['payload']['id'] == row['recovered_id']
    if target.exists():
        assert target.read_bytes() == content, 'Existing destination differs. No files were written.'
    plan.append((target, content))

installed = []
for target, content in plan:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with target.open('xb') as output:
            output.write(content)
    assert target.read_bytes() == content
    installed.append({'path': str(target), 'sha256': hashlib.sha256(content).hexdigest()})
(root / 'installed_files.json').write_text(json.dumps(installed, indent=2) + '\n')
print(json.dumps({'installed': len(installed), 'originals_replaced': 0}))
