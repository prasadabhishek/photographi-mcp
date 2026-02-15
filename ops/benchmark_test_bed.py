import time
import os
import sys
import glob

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photo_quality_analyzer_core.analyzer import evaluate_photo_quality

TEST_FOLDER = "/Volumes/Extended-1TB/sony_test_bed"

def run_benchmark():
    print(f"📂 Scanning {TEST_FOLDER}...")
    images = glob.glob(os.path.join(TEST_FOLDER, "*.[jJ][pP][gG]")) + \
             glob.glob(os.path.join(TEST_FOLDER, "*.[aA][rR][wW]"))
             
    if not images:
        print("❌ No images found!")
        return

    # Take first 10 images
    subset = images[:10]
    print(f"🚀 Benchmarking {len(subset)} images...")
    
    total_time = 0
    
    for i, img_path in enumerate(subset):
        start = time.time()
        try:
            evaluate_photo_quality(img_path)
            duration = time.time() - start
            print(f"[{i+1}/{len(subset)}] {os.path.basename(img_path)}: {duration*1000:.1f} ms")
            total_time += duration
        except Exception as e:
            print(f"❌ Failed {img_path}: {e}")

    avg_time = total_time / len(subset)
    print("\n" + "="*30)
    print(f"⚡ Average Processing Time: {avg_time*1000:.1f} ms")
    print("="*30)

if __name__ == "__main__":
    run_benchmark()
