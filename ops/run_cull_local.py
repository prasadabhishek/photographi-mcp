import sys
import os
import shutil
import glob
import logging

# Reduce logging noise
logging.basicConfig(level=logging.WARNING)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photo_quality_analyzer_core.analyzer import evaluate_photo_quality

FOLDER = "/Volumes/Extended-1TB/sony_test_bed"
CULLED_DIR = os.path.join(FOLDER, "culled_photos")
THRESHOLD = 0.4

def cull_images():
    if not os.path.exists(CULLED_DIR):
        os.makedirs(CULLED_DIR)
        print(f"📂 Created {CULLED_DIR}")
        
    # Find images
    extensions = ["*.jpg", "*.JPG", "*.arw", "*.ARW"]
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(FOLDER, ext)))
        
    total = len(images)
    if total == 0:
        print("❌ No images found.")
        return

    print(f"🚀 Processing {total} images with NEW Logic (Focus Veto)...")
    print(f"   Threshold: {THRESHOLD}")
    
    culled_count = 0
    kept_count = 0
    
    # Track specific files of interest
    watch_files = ["DSC03594.JPG", "DSC03664.JPG", "DSC03681.JPG"]
    
    for i, img_path in enumerate(images):
        fname = os.path.basename(img_path)
        try:
            # Enable Subject Detection for Focus Veto
            res = evaluate_photo_quality(img_path, enable_subject_detection=True)
            score = res['overallConfidence']
            
            # Watch list reporting
            if fname in watch_files:
                print(f"   👀 WATCH: {fname} = {score:.3f} [{'KEEP' if score >= THRESHOLD else 'CULL'}]")
            
            if score < THRESHOLD:
                shutil.move(img_path, os.path.join(CULLED_DIR, fname))
                culled_count += 1
                # print(f"   ❌ Culled {fname} ({score:.2f})")
            else:
                kept_count += 1
                
        except Exception as e:
            print(f"   ⚠️ Error {fname}: {e}")
            
        if (i+1) % 20 == 0:
            print(f"   ... {i+1}/{total}")

    print("\n" + "="*40)
    print(f"✅ Finished.")
    print(f"🗑️  Culled: {culled_count}")
    print(f"💾 Kept:   {kept_count}")
    print(f"📂 Check folder: {CULLED_DIR}")
    print("="*40)

if __name__ == "__main__":
    cull_images()
