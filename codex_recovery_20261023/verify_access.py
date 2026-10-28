import json
import os
import pathlib
import select
import subprocess
import time


root = pathlib.Path(__file__).resolve().parent
manifest = json.loads((root / 'manifest.json').read_text())
process = subprocess.Popen(
    ['codex', 'app-server', 'proxy'], stdin=subprocess.PIPE,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0,
)
pending = bytearray()


def request(number, method, params):
    process.stdin.write((json.dumps({'jsonrpc': '2.0', 'id': number, 'method': method, 'params': params}) + '\n').encode())
    process.stdin.flush()
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if b'\n' in pending:
            line, _, rest = pending.partition(b'\n')
            pending[:] = rest
            obj = json.loads(line)
            if obj.get('id') == number:
                return obj
            continue
        if select.select([process.stdout], [], [], 0.5)[0]:
            chunk = os.read(process.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError(process.stderr.read()[:1500].decode(errors='replace'))
            pending.extend(chunk)
    raise TimeoutError(method)


try:
    reply = request(1, 'initialize', {
        'clientInfo': {'name': 'history_recovery_check', 'version': '1.0'},
        'capabilities': {'experimentalApi': True},
    })
    if 'error' in reply:
        raise RuntimeError(reply['error'])
    process.stdin.write((json.dumps({'jsonrpc': '2.0', 'method': 'initialized'}) + '\n').encode())
    process.stdin.flush()
    reply = request(2, 'thread/list', {
        'limit': 100, 'useStateDbOnly': True,
        'sourceKinds': ['cli', 'vscode', 'exec'], 'modelProviders': [],
    })
    if 'error' in reply:
        raise RuntimeError(reply['error'])
    visible = {t['id'] for t in reply['result']['data']}
    results = []
    for number, record in enumerate(manifest, start=3):
        if record['status'] != 'saved_content':
            continue
        reply = request(number, 'thread/turns/list', {
            'threadId': record['id'], 'limit': 1, 'itemsView': 'full',
        })
        result = {
            'id': record['id'], 'visible_in_list': record['id'] in visible,
            'readable': 'result' in reply,
            'turns_returned': len(reply.get('result', {}).get('data', [])),
        }
        if 'error' in reply:
            result['error'] = reply['error']
        results.append(result)
    (root / 'access_check.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({
        'listed': len(visible), 'checked': len(results),
        'readable': sum(r['readable'] for r in results),
        'visible': sum(r['visible_in_list'] for r in results),
        'errors': [r for r in results if not r['readable']],
    }))
finally:
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
