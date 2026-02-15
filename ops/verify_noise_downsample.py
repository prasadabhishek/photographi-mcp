import time
import os
import cv2
import numpy as np
import rawpy
import scipy.stats
from tqdm import tqdm
from photo_quality_analyzer_core.analyzer import SUPPORTED_EXTENSIONS

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"

def noise_algo(img, gray):
    # Simplified copy of the analyzer logic
    h, w = gray.shape
    grid_size = 12
    patch_h, patch_w = h // grid_size, w // grid_size
    luma_vars = []
    
    if patch_h < 5 or patch_w < 5: return 0.0
    
    for i in range(grid_size):
        for j in range(grid_size):
            patch = gray[i*patch_h:(i+1)*patch_h, j*patch_w:(j+1)*patch_w]
            luma_vars.append(np.var(patch))
            
    luma_vars.sort()
    # Bottom 20%
    return np.mean(luma_vars[:max(1, len(luma_vars)//5)])

def run_noise_correlation():
    print("🔬 Verifying 'Downsampled Noise' Correlation")
    
    files = sorted([os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(SUPPORTED_EXTENSIONS)])[:20]
    
    full_vals = []
    small_vals = []
    
    for path in tqdm(files):
        try:
            with rawpy.imread(path) as raw:
                rgb = raw.postprocess(use_camera_wb=True)
            img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Full
            v_full = noise_algo(img, gray)
            full_vals.append(v_full)
            
            # Small
            h, w = img.shape[:2]
            target = 1024
            scale = target / max(h, w)
            dim = (int(w * scale), int(h * scale))
            img_small = cv2.resize(img, dim, interpolation=cv2.INTER_AREA) # INTER_AREA reduces noise!
            gray_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)
            
            v_small = noise_algo(img_small, gray_small)
            small_vals.append(v_small)
            
        except Exception as e:
            print(e)
            
    tau, _ = scipy.stats.kendalltau(full_vals, small_vals)
    pearson, _ = scipy.stats.pearsonr(full_vals, small_vals)
    
    print("\n📈 Results:")
    print(f"   Kendall's Tau: {tau:.4f}")
    print(f"   Pearson: {pearson:.4f}")
    
    # Calculate Scaling Factor (Linear Regression)
    # y = mx + c
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(small_vals, full_vals)
    print(f"\n📏 Calibration:")
    print(f"   Full_Noise ≈ {slope:.2f} * Small_Noise + {intercept:.2f}")
    print(f"   R-squared: {r_value**2:.4f}")

if __name__ == "__main__":
    run_noise_correlation()
