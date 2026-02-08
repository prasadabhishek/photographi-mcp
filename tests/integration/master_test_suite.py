import os
import shutil
import json
import time
from server import (
    _analyze_photo_logic, 
    _analyze_folder_logic, 
    _rank_folder_logic, 
    _cull_folder_logic
)
from photo_quality_analyzer_core.analyzer import generate_color_palette as get_color_palette

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEST_DIR = os.path.join(BASE_DIR, "master_test_env")
# Using images from existing test folders within the repo
RAW_IMAGE = os.path.join(BASE_DIR, "tests", "assets", "good_image.png") 
S_IMAGE = os.path.join(BASE_DIR, "tests", "assets", "sharp_test.png")
B_IMAGE = os.path.join(BASE_DIR, "tests", "assets", "blurry_test.png")
N_IMAGE = os.path.join(BASE_DIR, "tests", "assets", "noise_test.png")

def setup_env():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    # Populate with various images
    shutil.copy(S_IMAGE, os.path.join(TEST_DIR, "img_sharp.png"))
    shutil.copy(B_IMAGE, os.path.join(TEST_DIR, "img_blurry.png"))
    shutil.copy(N_IMAGE, os.path.join(TEST_DIR, "img_noise.png"))

def run_test(name, func, *args, **kwargs):
    print(f"\n🚀 [TESTING: {name}]")
    start = time.time()
    try:
        res = func(*args, **kwargs)
        duration = time.time() - start
        print(f"⏱️  Duration: {duration:.2f}s")
        # Print a concise summary of the result
        if "error" in res:
            print(f"❌ Error: {res['error']}")
        else:
            print(f"✅ Success")
            if "overallConfidence" in res:
                 print(f"   Score: {res['overallConfidence']:.2f} ({res['judgement']})")
            if "culledCount" in res:
                 total = res.get('totalImagesScanned', res.get('totalImages', 0))
                 print(f"   Culled: {res['culledCount']}/{total}")
    except Exception as e:
        print(f"🔥 Crash: {e}")

def test_all_combinations():
    setup_env()
    
    # 1. Single Photo: Full AI
    run_test("Single Photo (Full AI)", _analyze_photo_logic, os.path.join(TEST_DIR, "img_sharp.png"))
    
    # 2. Single Photo: Selective Metrics (No AI)
    run_test("Single Photo (Metrics only, No AI)", _analyze_photo_logic, 
             os.path.join(TEST_DIR, "img_sharp.png"), metrics=["sharpness", "exposure"], enable_subject_detection=False)
    
    # 3. Single Photo: Subject Detection Toggle OFF
    run_test("Single Photo (Subject Detection OFF)", _analyze_photo_logic, 
             os.path.join(TEST_DIR, "img_sharp.png"), enable_subject_detection=False)

    # 4. Folder Analysis
    run_test("Folder Analysis (Full)", _analyze_folder_logic, TEST_DIR)
    
    # 5. Ranking
    run_test("Rank Folder (Top 1)", _rank_folder_logic, TEST_DIR, top_n=1)

    # 6. Culling: Threshold + XMP
    run_test("Culling (Threshold 0.6 + XMP)", _cull_folder_logic, TEST_DIR, threshold=0.6, mode="xmp")
    
    # 7. Culling: Quantity + Move
    # Re-setup to ensure files exist
    setup_env()
    run_test("Culling (Keep Best 1 + Move)", _cull_folder_logic, TEST_DIR, keep_best_n=1, mode="move")

    # 8. Culling: Combinations (No Subject Detection + Both Actions)
    setup_env()
    run_test("Culling (Fast Tech + Both Actions)", _cull_folder_logic, 
             TEST_DIR, threshold=0.5, mode="both", enable_subject_detection=False)

    # 9. Aesthetic Tools
    setup_env()
    from photo_quality_analyzer_core.analyzer import generate_color_palette
    run_test("Color Palette", generate_color_palette, os.path.join(TEST_DIR, "img_sharp.png"), num_colors=3)

    # 10. Edge Case: Missing File
    run_test("Edge Case: Missing File", _analyze_photo_logic, "non_existent.jpg")

    # 11. Edge Case: Empty Folder
    empty_dir = os.path.join(TEST_DIR, "empty")
    os.makedirs(empty_dir)
    run_test("Edge Case: Empty Folder", _analyze_folder_logic, empty_dir)

if __name__ == "__main__":
    test_all_combinations()
