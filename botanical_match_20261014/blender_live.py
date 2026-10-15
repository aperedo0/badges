"""Use the installed Blender add-on in the open application over localhost."""
import json, socket, sys
from pathlib import Path

def command(kind,params=None):
    with socket.create_connection(('127.0.0.1',9876),timeout=3) as connection:
        connection.settimeout(60)
        connection.sendall(json.dumps({'type':kind,'params':params or {}}).encode())
        data=b''
        while True:
            chunk=connection.recv(65536)
            if not chunk:raise RuntimeError('Blender closed the connection.')
            data+=chunk
            try:result=json.loads(data)
            except json.JSONDecodeError:continue
            if result.get('status')!='success':raise RuntimeError(result)
            return result['result']

if __name__=='__main__':
    kind=sys.argv[1]
    if kind=='code':result=command('execute_code',{'code':Path(sys.argv[2]).read_text()})
    elif kind=='viewport':result=command('get_viewport_screenshot',{'filepath':sys.argv[2],'max_size':1400})
    else:result=command(kind)
    print(json.dumps(result))
