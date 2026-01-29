import os
import time
import json
import cv2
import numpy as np
from server import _analyze_photo_logic
from photo_quality_analyzer_core.analyzer import evaluate_photo_quality

def benchmark_latency(image_path, iterations=5):
    print(f"\n⏱️ Starting Latency Benchmark (N={iterations})...")
    times = []
    for i in range(iterations):
        start = time.time()
        _ = _analyze_photo_logic(image_path)
        end = time.time()
        times.append(end - start)
        print(f"  Iter {i+1}: {end-start:.3f}s")
    
    avg = sum(times) / len(times)
    print(f"✅ Avg Latency: {avg:.3f}s per image")
    return avg

def benchmark_stability(image_path):
    print(f"\n⚖️ Starting Stability Benchmark (Perturbation Test)...")
    
    # Original
    res_orig = _analyze_photo_logic(image_path)
    score_orig = res_orig["overallConfidence"]
    sharpness_orig = res_orig["metrics"]["sharpness"]["score"]
    
    # Perturbed: Rotate 1 degree
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), 1, 1.0)
    img_rot = cv2.warpAffine(img, M, (w, h))
    rot_path = image_path.replace(".png", "_rot.png")
    cv2.imwrite(rot_path, img_rot)
    
    res_rot = _analyze_photo_logic(rot_path)
    score_rot = res_rot["overallConfidence"]
    sharpness_rot = res_rot["metrics"]["sharpness"]["score"]
    
    os.remove(rot_path)
    
    diff_overall = abs(score_orig - score_rot)
    diff_sharpness = abs(sharpness_orig - sharpness_rot)
    
    print(f"  Original Score: {score_orig:.4f}")
    print(f"  Rotated (1°) Score: {score_rot:.4f}")
    print(f"  Delta: {diff_overall:.4f} ({(diff_overall/score_orig)*100:.2f}%)")
    
    if diff_overall < 0.05:
        print("✅ STABILITY TEST PASSED: Minimal variance under rotation.")
    else:
        print("⚠️ STABILITY WARNING: Variance exceeds 5%. Check anisotropic FFT sensitivity.")

if __name__ == "__main__":
    test_img = "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/sharp_portrait_test_1769658361256.png"
    benchmark_latency(test_img)
    benchmark_stability(test_img)
