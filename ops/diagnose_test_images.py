import cv2
import numpy as np
import os

base_dir = "/Users/abhishekprasad/workspace/photo-quality-analyzer"
data_dir = os.path.join(base_dir, "tests", "data")

sharp_path = os.path.join(data_dir, "sharp_test.png")
blurry_path = os.path.join(data_dir, "blurry_test.png")

img_sharp = cv2.imread(sharp_path, cv2.IMREAD_GRAYSCALE)
img_blurry = cv2.imread(blurry_path, cv2.IMREAD_GRAYSCALE)

# Calculate raw Tenengrad energy
def calc_energy(img):
    gx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    mag_sq = gx**2 + gy**2
    return np.mean(mag_sq)

sharp_energy = calc_energy(img_sharp)
blurry_energy = calc_energy(img_blurry)

print(f"Sharp image:")
print(f"  Shape: {img_sharp.shape}")
print(f"  Raw Energy: {sharp_energy:.2f}")
print(f"  Normalized (/ 800): {sharp_energy / 800:.4f}")
print()
print(f"Blurry image:")
print(f"  Shape: {img_blurry.shape}")
print(f"  Raw Energy: {blurry_energy:.2f}")
print(f"  Normalized (/ 800): {blurry_energy / 800:.4f}")
print()
print(f"Difference: {sharp_energy - blurry_energy:.2f}")
print(f"Ratio: {sharp_energy / blurry_energy:.2f}x")
