import numpy as np
import cv2
import os
import json
from photo_quality_analyzer_core.analyzer import evaluate_photo_quality

TEST_DIR = "test_data"

def generate_test_images():
    os.makedirs(TEST_DIR, exist_ok=True)
    size = (512, 512)
    
    # 1. Pure Sharp Edges (Solid black background with white rectangle)
    img_sharp = np.zeros((*size, 3), dtype=np.uint8)
    cv2.rectangle(img_sharp, (100, 100), (412, 412), (255, 255, 255), -1)
    cv2.imwrite(os.path.join(TEST_DIR, "sharp_test.png"), img_sharp)
    
    # 2. Pure Blurry Edges (Gaussian Blur on Sharp)
    img_blurry = cv2.GaussianBlur(img_sharp, (21, 21), 0)
    cv2.imwrite(os.path.join(TEST_DIR, "blurry_test.png"), img_blurry)
    
    # 3. Pure Noise (Gaussian noise)
    img_noise = np.random.normal(128, 50, (*size, 3)).astype(np.uint8)
    cv2.imwrite(os.path.join(TEST_DIR, "noise_test.png"), img_noise)
    
    # 4. Blown Highlights (Pure white)
    img_white = np.ones((*size, 3), dtype=np.uint8) * 255
    cv2.imwrite(os.path.join(TEST_DIR, "white_test.png"), img_white)

def run_suite():
    print(f"Running automated validation suite...")
    results = {}
    
    images = [
        ("Sharp", "sharp_test.png"),
        ("Blurry", "blurry_test.png"),
        ("Noise", "noise_test.png"),
        ("White", "white_test.png")
    ]
    
    for label, filename in images:
        path = os.path.join(TEST_DIR, filename)
        print(f"Analyzing {label}...")
        try:
            res = evaluate_photo_quality(path)
            results[label] = {
                "Overall": res["overallConfidence"],
                "Sharpness": res["metrics"]["sharpness"]["score"],
                "Exposure": res["metrics"]["exposure"]["score"],
                "Noise": res["metrics"]["noise"]["score"]
            }
        except Exception as e:
            print(f"Error analyzing {label}: {e}")
            
    print("\n--- Validation Results ---")
    print(json.dumps(results, indent=2))
    
    # Simple Assertions for tuning
    if results.get("Blurry") and results["Blurry"]["Sharpness"] > 0.4:
        print("WARNING: Blurry image rated too sharp!")
    if results.get("Noise") and results["Noise"]["Sharpness"] > 0.4:
        print("WARNING: Noise rated too sharp (Noise/Sharpness confusion)!")
    if results.get("White") and results["White"]["Exposure"] > 0.3:
        print("WARNING: Blown highlights rated with good exposure!")

if __name__ == "__main__":
    generate_test_images()
    run_suite()
