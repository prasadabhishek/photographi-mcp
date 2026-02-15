import cv2
import numpy as np
import sys
import os
import time

# Add project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photo_quality_analyzer_core.analyzer import _detect_objects, ensure_yolo_initialized

IMAGE_PATH = "/Volumes/Extended-1TB/sony_test_bed/culled_photos/DSC03565.JPG"

def benchmark_multisubject():
    print(f"Loading {IMAGE_PATH}...")
    img = cv2.imread(IMAGE_PATH)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Init Model (One-time cost, not counted in per-image benchmark typically)
    ensure_yolo_initialized(model_size="nano")
    
    print("-" * 40)
    print("🚀 Starting Logic Benchmark...")
    start_time = time.time()
    
    # 1. Detect (Heavy Lift)
    detections = _detect_objects(img)
    print(f"   Found {len(detections)} objects.")
    
    # 2. Logic A: Current (Max Confidence)
    best_conf = max(detections, key=lambda x: x['conf'])
    x1, y1, x2, y2 = map(int, best_conf['box'])
    roi_current = gray[y1:y2, x1:x2]
    score_current = cv2.Laplacian(roi_current, cv2.CV_64F).var() / 800.0 if roi_current.size > 0 else 0
    print(f"   [Old Logic] Main Subject ({best_conf['name']} @ {best_conf['conf']:.2f}): Focus Score = {score_current:.3f}")
    
    # 3. Logic B: Multi-Subject Scan (Best Focus)
    best_focus_score = 0.0
    best_focus_subject = "None"
    
    for d in detections:
        # Ignore low confidence junk
        if d['conf'] < 0.5: continue
            
        x1, y1, x2, y2 = map(int, d['box'])
        roi = gray[y1:y2, x1:x2]
        if roi.size > 0:
            s = cv2.Laplacian(roi, cv2.CV_64F).var() / 800.0
            if s > best_focus_score:
                best_focus_score = s
                best_focus_subject = f"{d['name']} (Conf {d['conf']:.2f})"
                
    print(f"   [New Logic] Best Subject ({best_focus_subject}): Focus Score = {best_focus_score:.3f}")
    
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print("-" * 40)
    print(f"⚡ Total Execution Time: {duration:.2f} ms")
    print(f"   (Includes detection + cropping + {len(detections)}x Laplacian checks)")
    print("-" * 40)
    
    if best_focus_score > score_current + 0.05:
        print("✅ New logic SAVED the photo (found a sharper subject).")
    else:
        print("❌ Result Unchanged (All subjects are blurry).")

if __name__ == "__main__":
    benchmark_multisubject()
