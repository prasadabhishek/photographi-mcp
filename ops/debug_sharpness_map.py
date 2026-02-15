import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

IMAGE_PATH = "/Volumes/Extended-1TB/sony_test_bed/DSC03594.JPG"
OUTPUT_PLOT = "/Users/abhishekprasad/workspace/photographi/debug_sharpness_map.png"

def plot_gradient_energy(image_path, output_path):
    print(f"Loading {image_path}...")
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Failed to load image.")
        return

    # Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calculate Gradients (Sobel)
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # Gradient Magnitude Squared (Energy)
    mag_sq = gx**2 + gy**2
    
    # Normalize for visualization (0-255)
    mag_norm = cv2.normalize(mag_sq, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Also calculate the raw numeric score to verify
    mean_energy = np.mean(mag_sq)
    base_score = min(mean_energy / 800.0, 1.0)
    print(f"🧮 Mean Energy: {mean_energy:.2f}")
    print(f"🧮 Raw Tenengrad Score: {base_score:.4f}")

    # Plot
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.title("Original Image")
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title("Gradient Energy (Where is it Sharp?)")
    # Using 'hot' colormap to highlight energy peaks
    plt.imshow(mag_norm, cmap='hot')
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"✅ Sharpness Map saved to {output_path}")

if __name__ == "__main__":
    plot_gradient_energy(IMAGE_PATH, OUTPUT_PLOT)
