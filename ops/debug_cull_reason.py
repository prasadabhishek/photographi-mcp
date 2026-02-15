import sys
import os
import logging
import cv2

# Reduce logging noise
logging.basicConfig(level=logging.WARNING)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photo_quality_analyzer_core.analyzer import evaluate_photo_quality

IMAGE_PATH = "/Volumes/Extended-1TB/sony_test_bed/culled_photos/DSC03573.JPG"

def analyze():
    print(f"🔎 Analyzing {os.path.basename(IMAGE_PATH)}...")
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ File not found: {IMAGE_PATH}")
        return

    try:
        # Load and analyze
        result = evaluate_photo_quality(IMAGE_PATH, enable_subject_detection=True)
        
        print("\n" + "="*40)
        print(f"📷 Final Score: {result['overallConfidence']:.3f} (Threshold: 0.40)")
        print("="*40)
        
        print(f"Technical: {result['technicalScore']:.3f}")
        print(f"Aesthetic: {result['aestheticScore']:.3f}")
        
        print("-" * 20)
        print("METRIC BREAKDOWN:")
        for metric, data in result['metrics'].items():
            score = data.get('score', 0)
            expl = data.get('explanation', '')
            print(f"• {metric.capitalize():<10}: {score:.3f} | {expl}")
            
        print("-" * 20)
        print(f"Objects: {result['detectedObjects']}")
        print(f"Judgement: {result['judgementDescription']}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze()
