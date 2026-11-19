"""Talk to the Blender MCP add-on already running in the open Blender (port 9876)."""
import json, socket, sys
from pathlib import Path

def command(kind, params=None, timeout=300):
    with socket.create_connection(('127.0.0.1', 9876), timeout=5) as c:
        c.settimeout(timeout)
        c.sendall(json.dumps({'type': kind, 'params': params or {}}).encode())
        data = b''
        while True:
            chunk = c.recv(65536)
            if not chunk:
                raise RuntimeError('Blender closed the connection')
            data += chunk
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                continue
            if result.get('status') != 'success':
                raise RuntimeError(result)
            return result['result']

if __name__ == '__main__':
    kind = sys.argv[1]
    if kind == 'code':
        r = command('execute_code', {'code': Path(sys.argv[2]).read_text()})
    elif kind == 'viewport':
        r = command('get_viewport_screenshot', {'filepath': sys.argv[2], 'max_size': int(sys.argv[3]) if len(sys.argv) > 3 else 1200})
    else:
        r = command(kind)
    print(json.dumps(r)[:3000])
