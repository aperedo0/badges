import datetime
import json
import pathlib
import uuid


root = pathlib.Path(__file__).resolve().parent
manifest = json.loads((root / 'manifest.json').read_text())
destination = root / 'resume_copies'
destination.mkdir(exist_ok=True)
if (root / 'resume_mapping.json').exists():
    for old in json.loads((root / 'resume_mapping.json').read_text()):
        (destination / pathlib.Path(old['file']).name).unlink(missing_ok=True)
mapping = []
now = datetime.datetime.now(datetime.timezone.utc)
stamp = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
for record in manifest:
    if record['status'] != 'saved_content':
        continue
    source = root / record['folder']
    meta = json.loads((source / 'metadata.json').read_text())
    new_id = str(uuid.uuid7())
    filename = 'rollout-' + now.strftime('%Y-%m-%dT%H-%M-%S') + '-' + new_id + '.jsonl'
    path = destination / filename
    title = 'Recovered: ' + ' '.join(record['title'].split())[:140]
    original_id = record['id']
    notice = (
        'This is a recovered copy of an older conversation. Original ID: ' + original_id + '. '
        'The user and assistant text below was recovered from the local Codex history database. '
        'The original model context, compaction summaries, and tool call state could not be restored. '
        'Do not assume that omitted attachments or tool results are available. '
        'Detailed saved item records are preserved at ' + str(source / 'items.jsonl') + '. '
        'Continue only when the user sends a new instruction.'
    )
    events = [{
        'timestamp': stamp,
        'type': 'session_meta',
        'payload': {
            'id': new_id, 'timestamp': stamp, 'cwd': record['cwd'],
            'originator': 'codex_cli_rs', 'cli_version': '0.162.1',
            'source': 'cli', 'thread_source': 'user', 'model_provider': 'openai',
            'base_instructions': {'text': notice},
        },
    }]
    active_turn = None
    last_agent_text = None
    def start_turn():
        turn = str(uuid.uuid7())
        events.append({'timestamp': stamp, 'type': 'event_msg', 'payload': {
            'type': 'task_started', 'turn_id': turn, 'started_at': int(now.timestamp()),
        }})
        return turn
    def end_turn(turn, last_text):
        if turn:
            events.append({'timestamp': stamp, 'type': 'event_msg', 'payload': {
                'type': 'task_complete', 'turn_id': turn, 'last_agent_message': last_text,
                'completed_at': int(now.timestamp()),
            }})
    def message(role, text, phase=None):
        if not text.strip():
            return
        events.append({
            'timestamp': stamp, 'type': 'response_item',
            'payload': {
                'type': 'message', 'role': role,
                'content': [{'type': 'output_text' if role == 'assistant' else 'input_text', 'text': text}],
            },
        })
        if role == 'user':
            events.append({'timestamp': stamp, 'type': 'event_msg', 'payload': {
                'type': 'user_message', 'message': text, 'images': [], 'local_images': [], 'text_elements': [],
            }})
        elif role == 'assistant':
            if phase:
                events[-1]['payload']['phase'] = phase
            events.append({'timestamp': stamp, 'type': 'event_msg', 'payload': {
                'type': 'agent_message', 'message': text, 'phase': phase,
            }})
    message('developer', notice)
    active_turn = start_turn()
    message('user', title + '\n\n' + notice)
    message('assistant', 'Recovered conversation messages follow.', 'final_answer')
    end_turn(active_turn, 'Recovered conversation messages follow.')
    active_turn = None
    source_turn = None
    messages = 0
    for line in (source / 'items.jsonl').open():
        raw = json.loads(line)
        item = json.loads(raw['item_json'])
        if item['type'] not in ('userMessage', 'agentMessage'):
            continue
        if raw['turn_id'] != source_turn:
            end_turn(active_turn, last_agent_text)
            active_turn = start_turn()
            source_turn = raw['turn_id']
            last_agent_text = None
        if item['type'] == 'userMessage':
            text = '\n'.join(c.get('text', '[Attachment reference retained in the raw item records.]') for c in item.get('content', []))
            message('user', text)
            messages += 1
        elif item['type'] == 'agentMessage':
            message('assistant', item.get('text', ''), item.get('phase'))
            last_agent_text = item.get('text', '')
            messages += 1
    message('assistant', 'End of recovered conversation text. Send a new instruction to continue this recovered copy.')
    end_turn(active_turn, 'End of recovered conversation text. Send a new instruction to continue this recovered copy.')
    with path.open('x') as output:
        for event in events:
            output.write(json.dumps(event) + '\n')
    mapping.append({
        'original_id': original_id, 'recovered_id': new_id, 'title': title,
        'cwd': record['cwd'], 'file': filename, 'messages': messages,
        'native_destination': str(pathlib.Path.home() / '.codex/sessions' / now.strftime('%Y/%m/%d') / filename),
    })
(root / 'resume_mapping.json').write_text(json.dumps(mapping, indent=2) + '\n')
print(json.dumps({'created_copies': len(mapping), 'total_bytes': sum(p.stat().st_size for p in destination.iterdir())}))
