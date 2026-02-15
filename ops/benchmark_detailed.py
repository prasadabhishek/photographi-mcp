import time
import os
import cv2
import numpy as np
import rawpy
from photo_quality_analyzer_core.analyzer import (
    _calculate_sharpness,
    _calculate_exposure,
    _calculate_noise,
    _calculate_color_balance,
    _detect_objects,
    _extract_metadata,
    ensure_yolo_initialized,
    SUPPORTED_EXTENSIONS
)

# Setup
FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"
# Find a RAW file
files = [os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(tuple(SUPPORTED_EXTENSIONS))]
if not files:
    print("No images found.")
    exit(1)
    
path = files[0] # DSC00554.ARW typically
print(f"📊 Benchmarking on: {os.path.basename(path)}")

timings = {}

# 1. Metadata
start = time.time()
metadata = _extract_metadata(path)
timings["Metadata Extraction"] = (time.time() - start) * 1000

# 2. Raw Loading & Processing
start = time.time()
with rawpy.imread(path) as raw:
    # Optimized: PPG + Full Res (half_size=False)
    rgb = raw.postprocess(
        use_camera_wb=True, 
        no_auto_bright=False, 
        bright=1.0, 
        half_size=False,
        demosaic_algorithm=rawpy.DemosaicAlgorithm.PPG
    )
timings["RAW Decode (Optimized PPG)"] = (time.time() - start) * 1000

# Convert to BGR/Gray for OpenCV
img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 3. YOLO Inference (Object Detection)
# Ensure model loaded first (cold start)
ensure_yolo_initialized()
start = time.time()
detections = _detect_objects(img)
timings["YOLO Inference (Subject Detection)"] = (time.time() - start) * 1000

# Pre-calculate small image (Simulating evaluate_photo_quality)
h, w = gray.shape
target = 1024
if max(h, w) > target:
    scale = target / max(h, w)
    small_img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    small_gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
else:
    small_img = img
    small_gray = gray

# 4. Sharpness (FFT) - Still Full Res
start = time.time()
_calculate_sharpness(gray, metadata)
timings["Sharpness (Tenengrad + Sobel)"] = (time.time() - start) * 1000

# 5. Noise (Variance Patching) - Optimized!
start = time.time()
_calculate_noise(small_img, small_gray, metadata)
timings["Noise Analysis"] = (time.time() - start) * 1000

# 6. Exposure (Zone System)
start = time.time()
_calculate_exposure(gray, metadata, detections)
timings["Exposure (Zone System)"] = (time.time() - start) * 1000

# 7. Color Balance - Optimized!
start = time.time()
_calculate_color_balance(small_img)
timings["Color Balance"] = (time.time() - start) * 1000

print("\n⏱️  Detailed Breakdown:")
print("-" * 40)
total_compute = 0
for task, ms in timings.items():
    print(f"{task:<35} : {ms:.2f} ms")
    total_compute += ms
print("-" * 40)
print(f"Total Analysis Time                  : {total_compute:.2f} ms")
