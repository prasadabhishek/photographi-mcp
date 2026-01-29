import asyncio
import os
import json
from server import _analyze_photo_logic

async def main():
    test_images = [
        ("Sharp Portrait", "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/sharp_portrait_test_1769658361256.png"),
        ("Intentional Blur", "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/blurry_motion_test_1769658374290.png"),
        ("Low Light / Noise", "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/low_light_noise_test_1769658387670.png"),
        ("Blown Highlights", "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/blown_highlights_test_1769658402319.png"),
        ("Sharp Landscape", "/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/sharp_landscape_1769657003579.png")
    ]
    
    print("🚀 Running Batch MCP Quality Validation...")
    final_results = []
    
    for label, path in test_images:
        print(f"\n--- [Testing: {label}] ---")
        if not os.path.exists(path):
            print(f"❌ Error: Image not found at {path}")
            continue
            
        try:
            result = _analyze_photo_logic(path)
            summary = {
                "Case": label,
                "Judgement": result["judgement"],
                "Score": round(result["overallConfidence"], 2),
                "Sharpness": round(result["metrics"]["sharpness"]["score"], 2),
                "Exposure": round(result["metrics"]["exposure"]["score"], 2),
                "Noise": round(result["metrics"]["noise"]["score"], 2),
                "Summary": result["judgementDescription"]
            }
            final_results.append(summary)
            print(f"✅ Result: {summary['Judgement']} ({summary['Score']})")
        except Exception as e:
            print(f"❌ Error analyzing {label}: {e}")
            
    print("\n" + "="*50)
    print("Final Batch Summary:")
    print(json.dumps(final_results, indent=2))
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
