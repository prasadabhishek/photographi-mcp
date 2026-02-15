import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photo_quality_analyzer_core.analyzer import evaluate_photo_quality

IMAGE_PATH = "/Volumes/Extended-1TB/sony_test_bed/DSC03594.JPG"

def verify():
    print(f"🕵️ Analyzing {os.path.basename(IMAGE_PATH)} with UPDATED Logic...")
    
    try:
        # Run analysis (Subject Detection Enabled)
        result = evaluate_photo_quality(IMAGE_PATH, enable_subject_detection=True)
        
        print("\n" + "="*40)
        print(f"📸 Final Score: {result['overallConfidence']:.4f}")
        print("="*40)
        print(f"Technicals: {result['technicalScore']:.4f}")
        print(f"Aesthetics: {result['aestheticScore']:.4f}")
        print("-" * 20)
        print(f"🔪 Sharpness: {result['metrics']['sharpness']['score']:.4f} {result['metrics']['sharpness']['explanation']}")
        print(f"🎯 Focus:     {result['metrics']['focus']['score']:.4f}")
        print(f"☀️ Exposure:  {result['metrics']['exposure']['score']:.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify()
