import time
import os
import cv2
import numpy as np
import rawpy
import scipy.stats
import scipy.fft
from tqdm import tqdm
from photo_quality_analyzer_core.analyzer import SUPPORTED_EXTENSIONS

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"

def verify_tenengrad_consistency():
    files = sorted([os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(SUPPORTED_EXTENSIONS)])[:50]
    
    fft_scores = []
    tenengrad_scores = []
    
    print(f"Versus Benchmarking: FFT vs Tenengrad on {len(files)} images...")
    
    for path in tqdm(files):
        try:
            # Use PPG as we decided it's the standard now
            with rawpy.imread(path) as raw:
                rgb = raw.postprocess(use_camera_wb=True, demosaic_algorithm=rawpy.DemosaicAlgorithm.PPG, half_size=False)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            h, w = gray.shape
            
            # 1. FFT (Current Logic simulation)
            f = scipy.fft.fft2(gray)
            fshift = scipy.fft.fftshift(f)
            mag = np.abs(fshift)
            
            # Mask High Frequency
            cy, cx = h / 2.0, w / 2.0
            r_outer = min(h, w) * 0.4
            r_inner = min(h, w) * 0.1
            y, x = np.ogrid[:h, :w]
            dist = np.sqrt((x - cx)**2 + (y - cy)**2)
            mask = (dist >= r_inner) & (dist <= r_outer)
            fft_score = np.mean(mag[mask])
            fft_scores.append(fft_score)
            
            # 2. Tenengrad (Candidate)
            gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_mag = cv2.magnitude(gx, gy)
            ten_score = np.mean(grad_mag * grad_mag)
            tenengrad_scores.append(ten_score)
            
        except Exception as e:
            print(f"Skipping {path}: {e}")
            
    tau, _ = scipy.stats.kendalltau(fft_scores, tenengrad_scores)
    pearson, _ = scipy.stats.pearsonr(fft_scores, tenengrad_scores)
    
    print("\n📈 Correlation Results (Tenengrad vs FFT):")
    print(f"   Kendall's Tau: {tau:.4f}")
    print(f"   Pearson: {pearson:.4f}")

    # Linear Regression for Calibration
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(tenengrad_scores, fft_scores)
    print(f"\n📏 Calibration:")
    print(f"   FFT_Score ≈ {slope:.6f} * Tenengrad + {intercept:.2f}")

if __name__ == "__main__":
    verify_tenengrad_consistency()
