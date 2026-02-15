import time
import os
import cv2
import numpy as np
import scipy.fft
import scipy.stats
from tqdm import tqdm
from photo_quality_analyzer_core.analyzer import SUPPORTED_EXTENSIONS

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"

def benchmark_sharpness_math():
    files = sorted([os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(SUPPORTED_EXTENSIONS)])[:15]
    
    results = {
        "Scipy FFT (Baseline)": {"times": [], "scores": []},
        "Numpy FFT": {"times": [], "scores": []},
        "CV2 DFT": {"times": [], "scores": []},
        "Laplacian Var": {"times": [], "scores": []},
        "Tenengrad (Sobel)": {"times": [], "scores": []},
    }
    
    print(f"🧮 Benchmarking Sharpness Math on {len(files)} images...")
    
    for path in tqdm(files):
        try:
            # Prepare Gray Image (1.0 scale)
            # Use rawpy? Or just read thumb for speed? 
            # We need full res to match the problem description.
            import rawpy
            with rawpy.imread(path) as raw:
                rgb = raw.postprocess(use_camera_wb=True, demosaic_algorithm=rawpy.DemosaicAlgorithm.PPG, half_size=False)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            h, w = gray.shape
            
            # 1. Scipy FFT (Baseline)
            start = time.time()
            f = scipy.fft.fft2(gray)
            fshift = scipy.fft.fftshift(f)
            mag = np.abs(fshift)
            # Simple metric: mean of log magnitude
            score_scipy = np.mean(mag)
            results["Scipy FFT (Baseline)"]["times"].append((time.time() - start) * 1000)
            results["Scipy FFT (Baseline)"]["scores"].append(score_scipy)
            
            # 2. Numpy FFT
            start = time.time()
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            mag = np.abs(fshift)
            score_numpy = np.mean(mag)
            results["Numpy FFT"]["times"].append((time.time() - start) * 1000)
            results["Numpy FFT"]["scores"].append(score_numpy)
            
            # 3. CV2 DFT (Optimized)
            start = time.time()
            # dft needs float32
            gray_float = gray.astype(np.float32)
            dft = cv2.dft(gray_float, flags=cv2.DFT_COMPLEX_OUTPUT)
            dft_shift = np.fft.fftshift(dft)
            mag = cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1])
            score_cv = np.mean(mag)
            results["CV2 DFT"]["times"].append((time.time() - start) * 1000)
            results["CV2 DFT"]["scores"].append(score_cv)
            
            # 4. Laplacian Variance (Spatial)
            start = time.time()
            score_lap = cv2.Laplacian(gray, cv2.CV_64F).var()
            results["Laplacian Var"]["times"].append((time.time() - start) * 1000)
            results["Laplacian Var"]["scores"].append(score_lap)

            # 5. Tenengrad (Sobel Gradient Magnitude)
            start = time.time()
            gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            mag = cv2.magnitude(gx, gy)
            score_ten = np.mean(mag * mag) # Energy
            results["Tenengrad (Sobel)"]["times"].append((time.time() - start) * 1000)
            results["Tenengrad (Sobel)"]["scores"].append(score_ten)
            
        except Exception as e:
            print(f"Skipping {path}: {e}")

    print("\n📈 Results:")
    print(f"{'Method':<20} | {'Avg Time':<10} | {'Speedup':<8} | {'Corr (Tau)':<10}")
    print("-" * 60)
    
    baseline_scores = results["Scipy FFT (Baseline)"]["scores"]
    baseline_time = np.mean(results["Scipy FFT (Baseline)"]["times"])
    
    for name, data in results.items():
        avg_time = np.mean(data["times"])
        speedup = baseline_time / avg_time
        scores = data["scores"]
        
        if name == "Scipy FFT (Baseline)":
            corr = 1.0
        else:
            corr, _ = scipy.stats.kendalltau(baseline_scores, scores)
            
        print(f"{name:<20} | {avg_time:6.2f} ms | {speedup:5.2f}x | {corr:.4f}")

if __name__ == "__main__":
    benchmark_sharpness_math()
