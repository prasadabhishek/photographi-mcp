
import json
import subprocess
import os
import time

def diagnose():
    config = {
        "command": "/Users/abhishekprasad/workspace/photographi/venv/bin/python",
        "args": ["-m", "server"],
        "cwd": "/Users/abhishekprasad/workspace/photographi",
        "env": {
            "PYTHONPATH": "/Users/abhishekprasad/workspace/photographi:/Users/abhishekprasad/workspace/photo-quality-analyzer",
            **os.environ
        }
    }
    
    print(f"--- Proper MCP Handshake Diagnosis ---")
    
    try:
        process = subprocess.Popen(
            [config['command']] + config['args'],
            cwd=config['cwd'],
            env=config['env'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        def send_req(method, params, req_id):
            req = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
            process.stdin.write(json.dumps(req) + "\n")
            process.stdin.flush()
            
        def send_notif(method, params):
            notif = {"jsonrpc": "2.0", "method": method, "params": params}
            process.stdin.write(json.dumps(notif) + "\n")
            process.stdin.flush()

        # 1. Initialize
        print("-> Sending 'initialize'...")
        send_req("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "diagnose-script", "version": "1.0"}
        }, 1)
        
        # Read response (might get multiple lines of logs first)
        while True:
            line = process.stdout.readline()
            if not line: break
            if "jsonrpc" in line:
                res = json.loads(line)
                if res.get("id") == 1:
                    print("✅ Initialized.")
                    break
        
        # 2. Notif initialized
        print("-> Sending 'notifications/initialized'...")
        send_notif("notifications/initialized", {})
        
        # 3. List Tools
        print("-> Sending 'tools/list'...")
        send_req("tools/list", {}, 2)
        
        while True:
            line = process.stdout.readline()
            if not line: break
            if "jsonrpc" in line:
                res = json.loads(line)
                if res.get("id") == 2:
                    tools = res.get("result", {}).get("tools", [])
                    print(f"✅ Received {len(tools)} tools.")
                    print(json.dumps(res, indent=2)) # Print full response
                    break
        
        process.terminate()
            
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")

if __name__ == "__main__":
    diagnose()
