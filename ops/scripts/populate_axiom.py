import sys
import os
import random
import time
import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from analytics import AnalyticsManager

def populate_axiom(num_events=50):
    print(f"🚀 POPULATING AXIOM DASHBOARD ({num_events} events)")
    
    # Initialize a clean manager for simulation
    manager = AnalyticsManager()
    
    # We want to spoof the relay to see data
    print(f"📡 Target: {manager.endpoint}")
    
    cameras = [
        ("Sony", "ILCE-7M4", "FE 24-70mm F2.8 GM II"),
        ("Canon", "EOS R5", "RF 24-105mm F4 L IS USM"),
        ("Nikon", "Z9", "NIKKOR Z 24-70mm f/2.8 S"),
        ("Fujifilm", "X-T5", "XF 18-55mm F2.8-4 R LM OIS"),
        ("Apple", "iPhone 15 Pro", "Main Camera")
    ]
    
    formats = ["jpg", "arw", "cr3", "png", "tiff"]
    judgements = ["Excellent", "Good", "Acceptable", "Poor"]
    
    for i in range(num_events):
        # 1. Randomize State
        make, model, lens = random.choice(cameras)
        fmt = random.choice(formats)
        judgement = random.choice(judgements)
        
        # 2. Track Technical Metrics
        manager.track_analysis_results(
            judgement=judgement,
            format_ext=fmt,
            model_size=random.choice(["nano", "xlarge"]),
            technical_score=random.uniform(0.6, 0.95),
            aesthetic_score=random.uniform(0.5, 0.9),
            overall_score=random.uniform(0.5, 0.95),
            camera_make=make,
            camera_model=model,
            lens_model=lens,
            count=random.randint(1, 5) # Multi-image batches
        )
        
        # 3. Random Tool Usage
        tool = random.choice(["photographi_analyze_folder", "photographi_rank_photographs", "photographi_cull_photographs"])
        manager.track_tool_invocation(tool)
        
        # 4. Feature Hits
        if random.random() > 0.5: manager.track_feature_usage("subject_detection")
        if random.random() > 0.8: manager.track_feature_usage("xmp_sidecar")
        
        # 5. Performance jitter
        manager.track_performance(
            proc_time_ms=random.randint(200, 1500),
            load_time_ms=random.randint(50, 200)
        )
        
        # 6. Transmit
        print(f"   [{i+1}/{num_events}] Transmitting aggregate state... ", end="", flush=True)
        manager.transmit_telemetry()
        print("Done.")
        
        # Avoid rate limiting just in case, though Cloudflare/Axiom should handle this
        time.sleep(0.1)

    print("\n✅ Axiom population complete! Your dashboard should now have enough data to render.")

if __name__ == "__main__":
    populate_axiom()
