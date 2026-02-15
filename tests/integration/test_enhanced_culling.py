import os
import shutil
import json
from server import _cull_logic

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_DATA = os.path.join(BASE_DIR, "test_data")

def setup_test_dir(test_dir):
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Copy some images to the test dir from existing test_data
    src_images = [
        os.path.join(T_DATA, "sharp.png"),
        os.path.join(T_DATA, "blurry.png"),
        os.path.join(T_DATA, "noisy.png")
    ]
    
    for i, src in enumerate(src_images):
        if os.path.exists(src):
            dest = os.path.join(test_dir, f"img_{i}.png")
            shutil.copy(src, dest)
    return [f"img_{i}.png" for i in range(len(src_images))]

def test_move_mode():
    test_dir = os.path.join(BASE_DIR, "test_move")
    setup_test_dir(test_dir)
    
    print("\n🚚 Testing Move Mode: Threshold 0.8...")
    result = _cull_logic(test_dir, threshold=0.8, mode="move")
    print(json.dumps(result, indent=2))
    
    # Verify Physical Move
    culled_dir = os.path.join(test_dir, "culled_photos")
    if os.path.exists(culled_dir):
        culled_files = os.listdir(culled_dir)
        print(f"✅ Verified: {len(culled_files)} files moved to {culled_dir}")
    else:
        print("❌ Error: culled_photos directory not found!")

if __name__ == "__main__":
    test_move_mode()
