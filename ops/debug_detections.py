import cv2
import numpy as np
import sys
import os

# Add project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photo_quality_analyzer_core.analyzer import _detect_objects, ensure_yolo_initialized

IMAGE_PATH = "/Volumes/Extended-1TB/sony_test_bed/culled_photos/DSC03573.JPG"
OUTPUT_PATH = "/Users/abhishekprasad/workspace/photographi/debug_detections.jpg"

def draw_detections():
    print(f"Loading {IMAGE_PATH}...")
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print("Failed to load image.")
        return

    # Initialize YOLO
    ensure_yolo_initialized(model_size="nano")
    
    # Run Detection
    detections = _detect_objects(img)
    print(f"Found {len(detections)} objects.")
    
    # Calculate Laplacian variance for each detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Find "Main" subject by Confidence (Current Logic)
    if detections:
        main_det = max(detections, key=lambda x: x['conf'])
        print(f"🏆 Current 'Main' Subject: {main_det['name']} (Conf: {main_det['conf']:.2f})")
    
    for d in detections:
        x1, y1, x2, y2 = map(int, d['box'])
        label = d['name']
        conf = d['conf']
        
        # Crop and measure focus
        roi = gray[y1:y2, x1:x2]
        focus_score = 0.0
        if roi.size > 0:
            lap_var = cv2.Laplacian(roi, cv2.CV_64F).var()
            focus_score = min(lap_var / 800.0, 1.0) # Approx normalization
            
        # Color: Green if Main, Red if others
        color = (0, 255, 0) if d == main_det else (0, 0, 255)
        
        # Draw Box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Draw Label
        text = f"{label}: {conf:.2f} | Focus: {focus_score:.2f}"
        cv2.putText(img, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        print(f"   - {label} @ [{x1}:{x2}, {y1}:{y2}] | Conf: {conf:.2f} | Focus: {focus_score:.2f}")

    cv2.imwrite(OUTPUT_PATH, img)
    print(f"✅ Saved detection map to {OUTPUT_PATH}")

if __name__ == "__main__":
    draw_detections()
