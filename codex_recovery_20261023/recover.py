import collections
import datetime
import hashlib
import json
import pathlib
import shutil
import sqlite3
import zipfile


ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = pathlib.Path.home() / '.codex'
SNAPSHOT = pathlib.Path('/private/tmp/codex_recovery_20261023_snapshot')
SNAPSHOT.mkdir(exist_ok=True)


def snapshot(name):
    source = sqlite3.connect((SOURCE / name).as_uri() + '?mode=ro', uri=True)
    target = sqlite3.connect(SNAPSHOT / name)
    source.backup(target)
    assert target.execute('pragma quick_check').fetchone()[0] == 'ok'
    target.close()
    source.close()
    result = sqlite3.connect(SNAPSHOT / name)
    result.row_factory = sqlite3.Row
    return result


state = snapshot('state_5.sqlite')
history = snapshot('thread_history_1.sqlite')
for name in ('history.jsonl', 'session_index.jsonl'):
    shutil.copy2(SOURCE / name, SNAPSHOT / name)

prompts = collections.defaultdict(list)
for line in (SNAPSHOT / 'history.jsonl').read_text().splitlines():
    try:
        entry = json.loads(line)
        prompts[entry.get('session_id')].append(entry)
    except ValueError:
        continue

records = list(state.execute("select * from threads where source in ('cli','vscode','exec') order by created_at"))
manifest = []
for row in records:
    meta = dict(row)
    if pathlib.Path(row['rollout_path']).exists():
        continue
    thread_id = row['id']
    items = list(history.execute(
        'select * from thread_items where thread_id=? order by rollout_ordinal,created_at_ms,item_id',
        (thread_id,),
    ))
    turns = list(history.execute(
        'select * from thread_turns where thread_id=? order by rollout_ordinal', (thread_id,),
    ))
    kind = 'saved_content' if items else 'prompt_remnants'
    folder = ROOT / kind / thread_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'metadata.json').write_text(json.dumps(meta, indent=2) + '\n')
    (folder / 'turns.json').write_text(json.dumps([dict(t) for t in turns], indent=2) + '\n')
    (folder / 'prompt_history.json').write_text(json.dumps(prompts[thread_id], indent=2) + '\n')
    messages = []
    if items:
        with (folder / 'items.jsonl').open('w') as output:
            for item in items:
                output.write(json.dumps(dict(item)) + '\n')
                obj = json.loads(item['item_json'])
                if obj['type'] == 'userMessage':
                    text = '\n'.join(
                        c.get('text', '[Attachment reference retained in items.jsonl]')
                        for c in obj.get('content', [])
                    )
                    messages.append(('You', text))
                elif obj['type'] == 'agentMessage':
                    messages.append(('Codex', obj.get('text', '')))
    else:
        messages.append(('Opening prompt from the history index', row['first_user_message'] or row['title']))
        messages.extend(('Saved terminal prompt', p.get('text', '')) for p in prompts[thread_id])
    # Preserve recovered messages exactly. Only the surrounding report is new prose.
    text = [row['title'], '', 'Conversation ID: ' + thread_id, 'Working folder: ' + row['cwd'], '']
    if items:
        text.extend(['Saved conversation content exported from the Codex history database.',
                     'This export does not establish that every original message or attachment survived.', ''])
    else:
        text.extend(['Only prompt remnants survived in the sources checked.',
                     'No Codex replies were found for this conversation.', ''])
    for role, body in messages:
        text.extend([role.upper(), '', body, ''])
    (folder / 'conversation.txt').write_text('\n'.join(text))
    manifest.append({
        'id': thread_id, 'title': row['title'], 'cwd': row['cwd'],
        'source': row['source'], 'history_mode': row['history_mode'],
        'status': kind, 'items': len(items), 'turns': len(turns),
        'messages': len(messages), 'terminal_prompts': len(prompts[thread_id]),
        'folder': str(folder.relative_to(ROOT)),
    })

(ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
with zipfile.ZipFile(ROOT / 'history_backup.zip', 'w', zipfile.ZIP_DEFLATED) as output:
    for path in SNAPSHOT.iterdir():
        output.write(path, path.name)

counts = collections.Counter(r['status'] for r in manifest)
readme = [
    '# Codex conversation recovery', '',
    f"Saved content exported for {counts['saved_content']} conversations whose separate transcript files are absent.",
    f"Prompt remnants exported for {counts['prompt_remnants']} older conversations.", '',
    'Saved content may already be accessible by conversation ID through Codex. Missing separate files do not prove that a conversation was deleted.',
    'Prompt remnants contain opening prompts and any surviving terminal input. They do not contain recovered Codex replies.', '',
    'The history backup contains consistent copies of both history databases and the two history index files. Authentication files are excluded.',
    'The original Codex databases and conversation files were not changed by this script.', '',
    '## Conversations', '',
]
for record in manifest:
    label = 'Saved content' if record['status'] == 'saved_content' else 'Prompts only'
    title = ' '.join(record['title'].split())[:115].replace('[', '(').replace(']', ')')
    readme.append(f"* {label}: [{title}]({record['folder']}/conversation.txt)")
(ROOT / 'README.md').write_text('\n'.join(readme) + '\n')
print(json.dumps({'counts': counts, 'folder': str(ROOT), 'backup_bytes': (ROOT / 'history_backup.zip').stat().st_size}))
