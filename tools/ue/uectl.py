#!/usr/bin/env python3
"""Drive the UE editor through the UE-MCP bridge. Runs ON the pod.
  uectl.py <method> ['<json-params>']
  uectl.py py <file.py>       # execute a python file in the editor
"""
import json, sys, websocket

PORT = json.load(open("/workspace/projects/DCGoGoFest/Saved/UE_MCP_Bridge/port.json"))["port"]
ws = websocket.create_connection(f"ws://127.0.0.1:{PORT}/", timeout=600,
                                 suppress_origin=True)

def rpc(method, params=None, _id=[0]):
    _id[0] += 1
    ws.send(json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method,
                        "params": params or {}}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == _id[0]:
            return m

if sys.argv[1] == "py":
    src = open(sys.argv[2]).read()
    r = rpc("execute_python", {"code": src})
else:
    r = rpc(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
print(json.dumps(r, indent=2)[:6000])
