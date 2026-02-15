import time
import os
import cv2
import numpy as np
import rawpy
from skimage.restoration import estimate_sigma

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"
# Find a RAW file
files = [os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith('.arw')]
if not files: exit(1)
path = files[0]

print(f"📊 Benchmarking Noise Algorithms on: {os.path.basename(path)}")

# Load Image
with rawpy.imread(path) as raw:
    rgb = raw.postprocess(use_camera_wb=True)
img_full = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
gray_full = cv2.cvtColor(img_full, cv2.COLOR_BGR2GRAY)

# Downsampled versions
h, w = img_full.shape[:2]
target = 1024
scale = target / max(h, w)
dim = (int(w * scale), int(h * scale))
gray_small = cv2.resize(gray_full, dim, interpolation=cv2.INTER_AREA)

print(f"Full Size: {gray_full.shape}")
print(f"Small Size: {gray_small.shape}")

# --- 1. Current Method: Multi-Patch Variance (Luma + Chroma) ---
def current_noise_algo(img, gray):
    h, w = gray.shape
    grid_size = 12
    patch_h, patch_w = h // grid_size, w // grid_size
    
    luma_variances = []
    chroma_variances = []
    
    for i in range(grid_size):
        for j in range(grid_size):
            # Luma
            patch = gray[i*patch_h:(i+1)*patch_h, j*patch_w:(j+1)*patch_w]
            luma_variances.append(np.var(patch))
            
            # Chroma (Expensive part!)
            patch_bgr = img[i*patch_h:(i+1)*patch_h, j*patch_w:(j+1)*patch_w]
            if patch_bgr.size > 0:
                patch_lab = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2Lab)
                l, a, b = cv2.split(patch_lab)
                chroma_variances.append(np.var(a) + np.var(b))
                
    luma_variances.sort()
    return np.mean(luma_variances[:len(luma_variances)//5])

start = time.time()
score_current = current_noise_algo(img_full, gray_full)
t_current = (time.time() - start) * 1000
print(f"\n[1] Current Method (Full - Luma+Chroma): {t_current:.2f} ms | Score: {score_current:.2f}")

# --- 2. Current Method (Downsampled) ---
# Resize color image too
start = time.time()
img_small = cv2.resize(img_full, dim, interpolation=cv2.INTER_AREA)

start_calc = time.time()
score_current_small = current_noise_algo(img_small, gray_small)
t_current_small = (time.time() - start) * 1000 # Include resize time
print(f"[2] Current Method (Small - Luma+Chroma):  {t_current_small:.2f} ms | Score: {score_current_small:.2f}")

# --- 3. Scikit-Image Estimate Sigma (Full) ---
# estimate_sigma uses Median Absolute Deviation of Wavelet coefficients
start = time.time()
# channel_axis=None because grayscale
sigma_full = estimate_sigma(gray_full, channel_axis=None)
t_sk_full = (time.time() - start) * 1000
print(f"[3] Skimage Sigma (Full):      {t_sk_full:.2f} ms | Sigma: {sigma_full:.4f}")

# --- 4. Scikit-Image Estimate Sigma (Small) ---
start = time.time()
sigma_small = estimate_sigma(gray_small, channel_axis=None)
t_sk_small = (time.time() - start) * 1000
print(f"[4] Skimage Sigma (Small):     {t_sk_small:.2f} ms | Sigma: {sigma_small:.4f}")

# --- 5. OpenCV Gaussian Difference (Fast Approximation) ---
def cv2_gaussian_diff(gray):
    # Blur to remove noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Difference is mostly noise (and edges)
    diff = cv2.absdiff(gray, blurred)
    # We want the variance of this difference, but robust to edges.
    # Simple mean of diff? Or Std Dev?
    # Estimate standard deviation
    return np.std(diff)

start = time.time()
sigma_cv_full = cv2_gaussian_diff(gray_full)
t_cv_full = (time.time() - start) * 1000
print(f"[5] CV2 GaussDiff (Full):      {t_cv_full:.2f} ms | Sigma: {sigma_cv_full:.4f}")

start = time.time()
sigma_cv_small = cv2_gaussian_diff(gray_small)
t_cv_small = (time.time() - start) * 1000
print(f"[6] CV2 GaussDiff (Small):     {t_cv_small:.2f} ms | Sigma: {sigma_cv_small:.4f}")

print("-" * 30)
