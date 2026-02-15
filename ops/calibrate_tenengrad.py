import os
import cv2
import numpy as np
import rawpy
from tqdm import tqdm
from photo_quality_analyzer_core.analyzer import SUPPORTED_EXTENSIONS

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"

def calibrate_tenengrad():
    files = sorted([os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(SUPPORTED_EXTENSIONS)])[:30]
    
    scores = []
    
    print(f"Calibrating Tenengrad on {len(files)} images...")
    
    for path in tqdm(files):
        try:
            with rawpy.imread(path) as raw:
                # Use PPG (Fast)
                rgb = raw.postprocess(use_camera_wb=True, demosaic_algorithm=rawpy.DemosaicAlgorithm.PPG, half_size=False)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            
            # Tenengrad
            gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            mag_sq = gx**2 + gy**2
            # Handle image size
            mean_energy = np.mean(mag_sq)
            scores.append(mean_energy)
            
        except Exception as e:
            print(f"Skipping {path}: {e}")

    scores = np.array(scores)
    print("\n📊 Statistics:")
    print(f"   Min: {scores.min():.2f}")
    print(f"   Max: {scores.max():.2f}")
    print(f"   Mean: {scores.mean():.2f}")
    print(f"   Median: {np.median(scores):.2f}")
    print(f"   StdDev: {scores.std():.2f}")

if __name__ == "__main__":
    calibrate_tenengrad()
