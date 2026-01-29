import asyncio
from server import _analyze_photo_logic
import os
import json

async def main():
    # Paths to generated images
    sharp_img = "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/sharp_landscape_1769657003579.png"
    blurry_img = "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/blurry_motion_photo_1769657015344.png"
    
    print("Testing photographi logic with generated images...")
    
    for label, path in [("SHARP PHOTO", sharp_img), ("BLURRY PHOTO", blurry_img)]:
        print(f"\n--- Analyzing {label} ---")
        if not os.path.exists(path):
            print(f"Error: Test image not found at {path}")
            continue
            
        try:
            result = _analyze_photo_logic(path)
            print(f"Judgement: {result.get('judgement')}")
            print(f"Overall Confidence: {result.get('overall_confidence'):.2f}")
            print("Full Result Data:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error during analysis: {e}")

if __name__ == "__main__":
    asyncio.run(main())
