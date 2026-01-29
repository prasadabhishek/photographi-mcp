import asyncio
import os
import json
from server import _analyze_photo_logic
from unittest.mock import patch

# Mock function for _extract_metadata
def mock_extract_metadata(path):
    return {
        "shutter_speed": 1/15, # Slow shutter
        "iso": 100,
        "aperture": 2.8,
        "status": "present"
    }

async def main():
    path = "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/blurry_motion_test_1769658374290.png"
    
    print("🧪 Testing Context-Aware Scaling (Mock EXIF)...")
    
    with patch('photo_quality_analyzer_core.analyzer._extract_metadata', side_effect=mock_extract_metadata):
        result = _analyze_photo_logic(path)
        print(f"\n--- [Testing: Intentional Blur w/ EXIF] ---")
        print(f"Judgement: {result['judgement']}")
        print(f"Overall Confidence: {result['overallConfidence']:.2f}")
        print(f"Sharpness Score: {result['metrics']['sharpness']['score']:.2f}")
        print(f"Sharpness Explanation: {result['metrics']['sharpness']['explanation']}")
        print(f"Judgement Description: {result['judgementDescription']}")

if __name__ == "__main__":
    asyncio.run(main())
