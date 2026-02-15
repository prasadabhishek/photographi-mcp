import time
import os
import cv2
import numpy as np
import rawpy
from photo_quality_analyzer_core.analyzer import (
    _calculate_color_balance,
    SUPPORTED_EXTENSIONS
)

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"
# Find a RAW file
files = [os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(tuple(SUPPORTED_EXTENSIONS))]
path = files[0]

print(f"Testing Color Balance Optimization on {os.path.basename(path)}")

# Load Image
with rawpy.imread(path) as raw:
    rgb = raw.postprocess(use_camera_wb=True)
img_full = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

# 1. Full Res Benchmark
start = time.time()
score_full, expl_full = _calculate_color_balance(img_full)
t_full = (time.time() - start) * 1000

print(f"\n[1] Full Resolution ({img_full.shape})")
print(f"    Time: {t_full:.2f} ms")
print(f"    Score: {score_full:.4f}")

# 2. Resized Benchmark (1024px)
h, w = img_full.shape[:2]
target = 1024
scale = target / max(h, w)
dim = (int(w * scale), int(h * scale))

start = time.time()
img_small = cv2.resize(img_full, dim, interpolation=cv2.INTER_AREA)
t_resize = (time.time() - start) * 1000

start = time.time()
score_small, expl_small = _calculate_color_balance(img_small)
t_small = (time.time() - start) * 1000

print(f"\n[2] Resized 1024px ({img_small.shape})")
print(f"    Resize Overhead: {t_resize:.2f} ms")
print(f"    Calc Time: {t_small:.2f} ms")
print(f"    Total Time: {t_resize + t_small:.2f} ms")
print(f"    Score: {score_small:.4f}")

diff = abs(score_full - score_small)
print(f"\nDifference: {diff:.4f}")

if diff < 0.05:
    print("✅ Optimization Verified: Safe to use.")
else:
    print("❌ Score divergence too high.")
