import time
import os
import sys
import glob
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photo_quality_analyzer_core.analyzer import evaluate_photo_quality

TEST_FOLDER = "/Volumes/Extended-1TB/sony_test_bed"

def process_image(img_path):
    try:
        # We don't need the result, just the timing of the analysis
        # In a real rank_photographs, we would collect scores.
        evaluate_photo_quality(img_path)
        return True
    except Exception as e:
        print(f"❌ Failed {os.path.basename(img_path)}: {e}")
        return False

def run_full_benchmark():
    print(f"📂 Scanning {TEST_FOLDER}...")
    images = glob.glob(os.path.join(TEST_FOLDER, "*.[jJ][pP][gG]")) + \
             glob.glob(os.path.join(TEST_FOLDER, "*.[aA][rR][wW]"))
             
    count = len(images)
    if count == 0:
        print("❌ No images found!")
        return

    print(f"🚀 Starting Rank/Analyze benchmark on {count} images...")
    print(f"   (Simulating 'photographi_rank_photographs' workload)")
    
    start_time = time.time()
    
    # The server typically processes sequentially or with limited parallelism.
    # We will simulate sequential processing to be conservative and match the tool's behavior 
    # (unless the tool uses ThreadPool, which it currently does NOT for safety).
    
    processed = 0
    for i, img in enumerate(images):
        if process_image(img):
            processed += 1
        if (i+1) % 10 == 0:
            elapsed = time.time() - start_time
            print(f"   ... processed {i+1}/{count} ({elapsed:.1f}s)")

    end_time = time.time()
    total_duration = end_time - start_time
    avg_per_image = total_duration / count

    print("\n" + "="*40)
    print(f"⏱️  Total Time:    {total_duration:.2f} seconds")
    print(f"⚡ Avg Per Image: {avg_per_image*1000:.1f} ms")
    print(f"📊 Throughput:    {count / total_duration:.2f} images/sec")
    print("="*40)

if __name__ == "__main__":
    run_full_benchmark()
