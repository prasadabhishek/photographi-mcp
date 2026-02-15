import cv2
import numpy as np
import sys
import os
import time

# Add project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photo_quality_analyzer_core.analyzer import _detect_objects, ensure_yolo_initialized

IMAGE_PATH = "/Volumes/Extended-1TB/sony_test_bed/culled_photos/DSC03565.JPG"

def benchmark_overhead():
    print(f"Loading {IMAGE_PATH}...")
    img = cv2.imread(IMAGE_PATH)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    ensure_yolo_initialized(model_size="nano")
    
    # 1. Pre-Run Detection (Common Cost)
    print("Running Detections (Common Cost)...")
    detections = _detect_objects(img)
    print(f"Found {len(detections)} objects.")
    
    # 2. Measure OLD Logic (Single Check)
    start_old = time.perf_counter()
    best_conf = max(detections, key=lambda x: x['conf'])
    x1, y1, x2, y2 = map(int, best_conf['box'])
    roi = gray[y1:y2, x1:x2]
    if roi.size > 0:
        _ = cv2.Laplacian(roi, cv2.CV_64F).var()
    end_old = time.perf_counter()
    duration_old = (end_old - start_old) * 1000
    
    # 3. Measure NEW Logic (Loop Check of 7 objects)
    start_new = time.perf_counter()
    for d in detections:
        if d['conf'] < 0.5: continue
        x1, y1, x2, y2 = map(int, d['box'])
        roi = gray[y1:y2, x1:x2]
        if roi.size > 0:
            _ = cv2.Laplacian(roi, cv2.CV_64F).var()
    end_new = time.perf_counter()
    duration_new = (end_new - start_new) * 1000
    
    print("\n" + "="*40)
    print("⏱️  PERFORMANCE HIT ANALYSIS")
    print("="*40)
    print(f"Old Logic (1 Person):  {duration_old:.4f} ms")
    print(f"New Logic (7 People):  {duration_new:.4f} ms")
    print("-" * 40)
    print(f"🛑 Added Latency:      +{duration_new - duration_old:.4f} ms")
    print("="*40)

if __name__ == "__main__":
    benchmark_overhead()
