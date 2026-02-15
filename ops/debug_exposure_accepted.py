import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

IMAGE_PATH = "/Volumes/Extended-1TB/sony_test_bed/DSC03681.JPG"
OUTPUT_PLOT = "/Users/abhishekprasad/workspace/photographi/debug_histogram_accepted.png"

def plot_zones(image_path, output_path):
    print(f"Loading {image_path}...")
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Failed to load image.")
        return

    # Convert to Grayscale (Luminance)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calculate Histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    
    # Calculate % of pixels in Zone 0 (0-25)
    total_pixels = gray.size
    pixels_in_zone_0 = np.sum(hist[0:26])
    percentage_zone_0 = (pixels_in_zone_0 / total_pixels) * 100
    
    pixels_in_zone_1 = np.sum(hist[26:51])
    percentage_zone_1 = (pixels_in_zone_1 / total_pixels) * 100

    print(f"📊 Zone 0 (0-25): {percentage_zone_0:.2f}% (Deep Blacks)")
    print(f"📊 Zone 1 (26-50): {percentage_zone_1:.2f}% (Context)")
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.title(f"ACCEPTED Image Histogram (Zone 0: {percentage_zone_0:.1f}%)")
    plt.xlabel("Pixel Value (0-255)")
    plt.ylabel("Frequency")
    
    # Plot histogram line
    plt.plot(hist, color='green') # Green for accepted
    plt.xlim([0, 256])
    
    # Shade Zone 0 (Danger Zone)
    plt.axvspan(0, 25, color='red', alpha=0.1, label='Zone 0')
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(output_path)
    print(f"✅ Plot saved to {output_path}")

if __name__ == "__main__":
    plot_zones(IMAGE_PATH, OUTPUT_PLOT)
