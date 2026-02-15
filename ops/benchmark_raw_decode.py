import time
import os
import cv2
import numpy as np
import rawpy
import scipy.stats
from tqdm import tqdm
from photo_quality_analyzer_core.analyzer import _calculate_sharpness, SUPPORTED_EXTENSIONS

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"

def benchmark_demosaic():
    files = sorted([os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(SUPPORTED_EXTENSIONS)])[:10]
    if not files:
        print("No RAW files found.")
        return

    # Strategies to test
    strategies = [
        ("AHD (Default)", rawpy.DemosaicAlgorithm.AHD),
        ("Linear (Fast)", rawpy.DemosaicAlgorithm.LINEAR),
        ("PPG (Fast)", rawpy.DemosaicAlgorithm.PPG),
        ("VNG (Slow)", rawpy.DemosaicAlgorithm.VNG),
    ]

    results = {name: {"times": [], "scores": []} for name, _ in strategies}
    
    print(f"📊 Benchmarking RAW Decode Strategies on {len(files)} images...")
    
    for path in tqdm(files):
        try:
            with rawpy.imread(path) as raw:
                # Baseline (AHD) for sharpness ground truth
                # We need to extract scores to check correlation
                pass 
                
            # Test each strategy
            for name, algo in strategies:
                start = time.time()
                with rawpy.imread(path) as raw:
                    # use_camera_wb=True is standard
                    # no_auto_scale=False is standard
                    rgb = raw.postprocess(use_camera_wb=True, demosaic_algorithm=algo)
                
                dt = (time.time() - start) * 1000
                results[name]["times"].append(dt)
                
                # Calculate Sharpness
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                # metadata mock
                score, _ = _calculate_sharpness(gray, {"iso": 100})
                results[name]["scores"].append(score)
                
        except Exception as e:
            print(f"Error {path}: {e}")

    print("\n📈 Results Summary:")
    print(f"{'Algorithm':<20} | {'Avg Time':<10} | {'Speedup':<8} | {'Sharpness Corr (Tau)':<20}")
    print("-" * 70)
    
    baseline_scores = results["AHD (Default)"]["scores"]
    baseline_time = np.mean(results["AHD (Default)"]["times"])
    
    for name, _ in strategies:
        avg_time = np.mean(results[name]["times"])
        speedup = baseline_time / avg_time
        scores = results[name]["scores"]
        
        if name == "AHD (Default)":
            corr = 1.0
        else:
            corr, _ = scipy.stats.kendalltau(baseline_scores, scores)
            
        print(f"{name:<20} | {avg_time:6.2f} ms | {speedup:5.2f}x | {corr:.4f}")

if __name__ == "__main__":
    benchmark_demosaic()
