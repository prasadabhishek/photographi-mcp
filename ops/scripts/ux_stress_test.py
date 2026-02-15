import subprocess
import json
import os
import time

# Configuration
COPILOT_CMD = "copilot"
PROJECT_DIR = "/Users/abhishekprasad/workspace/photographi"
VOLUME_PATH = os.path.join(PROJECT_DIR, "local_test_assets")
LOG_FILE = os.path.join(PROJECT_DIR, "tools/ux_report.json")

SCENARIOS = [
    {
        "id": "1",
        "name": "The Hero Selection",
        "prompt": f"Find the best shot in {VOLUME_PATH} and explain your technical reasoning.",
    },
    {
        "id": "2",
        "name": "Automated Culling",
        "prompt": f"Cull the low-quality photos in {VOLUME_PATH} using photographi_cull_photographs set to move mode.",
    },
    {
        "id": "3",
        "name": "Subject Aware Analysis",
        "prompt": f"Analyze {VOLUME_PATH}/DSC00504.ARW. Is the subject in focus?",
    },
    {
        "id": "4",
        "name": "Mood-board Extraction",
        "prompt": f"Extract a 5-color aesthetic palette from the best photo in {VOLUME_PATH}.",
    },
    {
        "id": "5",
        "name": "Technical Session Audit",
        "prompt": f"Audit {VOLUME_PATH} for any common technical issues like blur or noise.",
    },
    {
        "id": "6",
        "name": "Performance & Model Choice",
        "prompt": f"Analyze sharpness for {VOLUME_PATH}/DSC00505.ARW using the xlarge model.",
    }
]

def run_scenario(scenario):
    print(f"\n🚀 Running Scenario {scenario['id']}: {scenario['name']}")
    start_time = time.time()
    
    # Using --yolo to ensure all professional tools are allowed without manual confirmation
    cmd = [COPILOT_CMD, "-p", scenario['prompt'], "--yolo"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_DIR)
        duration = time.time() - start_time
        
        res = {
            "id": scenario['id'],
            "name": scenario['name'],
            "prompt": scenario['prompt'],
            "output": result.stdout,
            "error": result.stderr,
            "duration": round(duration, 2),
            "status": "PASS" if result.returncode == 0 else "FAIL"
        }
        
        # Incremental Save
        try:
            current_report = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    current_report = json.load(f)
            current_report.append(res)
            with open(LOG_FILE, "w") as f:
                json.dump(current_report, f, indent=2)
        except: pass
        
        return res
    except Exception as e:
        return {"id": scenario['id'], "status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    # Clear old report
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    for s in SCENARIOS:
        run_scenario(s)
        time.sleep(1)
    
    print(f"\n✅ UX Stress Test Complete. Total report at {LOG_FILE}")
