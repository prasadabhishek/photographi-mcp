import cv2
import numpy as np
import time

IMAGE_PATH = "/Volumes/Extended-1TB/sony_test_bed/DSC03594.JPG"

def calc_fft_sharpness(gray):
    # Old Method: FFT Frequency Analysis
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)
    # Calculate mean magnitude of high frequencies
    h, w = gray.shape
    center_y, center_x = h // 2, w // 2
    # simple high-pass checking
    return np.mean(magnitude_spectrum)

def calc_tenengrad_sharpness(gray):
    # New Method: Sobel Energy
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    mag = gx**2 + gy**2
    return np.mean(mag)

def benchmark():
    print(f"Loading {IMAGE_PATH}...")
    img = cv2.imread(IMAGE_PATH)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. FFT (Old)
    start = time.time()
    fft_score = calc_fft_sharpness(gray)
    fft_time = (time.time() - start) * 1000
    
    # 2. Tenengrad (New)
    start = time.time()
    ten_score = calc_tenengrad_sharpness(gray)
    ten_time = (time.time() - start) * 1000
    
    print("\n" + "="*40)
    print(f"📊 Comparison on 'Gravel/Leaves' Image")
    print("="*40)
    print(f"Old Algorithm (FFT):       Score={fft_score:.2f}  Time={fft_time:.1f}ms")
    print(f"New Algorithm (Tenengrad): Score={ten_score:.2f}  Time={ten_time:.1f}ms")
    print("-" * 40)
    
    # Calibration Context involves checking against baselines, but the raw values
    # tell us if they both react strongly to texture.
    print("Interpretation:")
    print("If BOTH scores are high, the issue is Global Analysis (Background).")
    print("If FFT is low and Tenengrad is high, then Tenengrad is the problem.")

if __name__ == "__main__":
    benchmark()
