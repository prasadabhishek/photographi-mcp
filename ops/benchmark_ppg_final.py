import time
import os
import cv2
import numpy as np
import rawpy
import scipy.stats
from tqdm import tqdm
from photo_quality_analyzer_core.analyzer import _calculate_sharpness, SUPPORTED_EXTENSIONS

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"

def benchmark_ppg_consistency():
    files = sorted([os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(SUPPORTED_EXTENSIONS)])[:50]
    
    ahd_scores = []
    ppg_scores = []
    
    print(f"Versus Benchmarking: AHD vs PPG on {len(files)} images...")
    
    for path in tqdm(files):
        try:
            # 1. AHD (Baseline)
            with rawpy.imread(path) as raw:
                rgb_ahd = raw.postprocess(use_camera_wb=True, demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD)
            gray_ahd = cv2.cvtColor(rgb_ahd, cv2.COLOR_RGB2GRAY)
            score_ahd, _ = _calculate_sharpness(gray_ahd, {"iso": 100})
            ahd_scores.append(score_ahd)
            
            # 2. PPG (Candidate)
            with rawpy.imread(path) as raw:
                rgb_ppg = raw.postprocess(use_camera_wb=True, demosaic_algorithm=rawpy.DemosaicAlgorithm.PPG)
            gray_ppg = cv2.cvtColor(rgb_ppg, cv2.COLOR_RGB2GRAY)
            score_ppg, _ = _calculate_sharpness(gray_ppg, {"iso": 100})
            ppg_scores.append(score_ppg)
            
        except Exception as e:
            print(f"Skipping {path}: {e}")
            
    tau, _ = scipy.stats.kendalltau(ahd_scores, ppg_scores)
    pearson, _ = scipy.stats.pearsonr(ahd_scores, ppg_scores)
    
    print("\n📈 Correlation Results (PPG vs AHD):")
    print(f"   Kendall's Tau: {tau:.4f}")
    print(f"   Pearson: {pearson:.4f}")
    
    if tau > 0.95:
        print("✅ Safe to switch.")
    else:
        print("⚠️ Significant deviation detected.")

if __name__ == "__main__":
    benchmark_ppg_consistency()
