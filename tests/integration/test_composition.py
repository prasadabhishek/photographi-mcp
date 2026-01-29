import json
from server import _analyze_photo_logic

def test_composition():
    # Test images for composition
    test_images = [
        ("Centered Subject", "/Users/abhishekprasad/workspace/photographi/test_culling/good_image.png")
    ]
    
    print("\n📐 Testing Composition Analysis...")
    for label, path in test_images:
        print(f"\n--- [Testing: {label}] ---")
        try:
            result = _analyze_photo_logic(path)
            comp = result["metrics"]["composition"]
            print(f"Score: {comp['score']:.2f}")
            print(f"Explanation: {comp['explanation']}")
            print(f"Overall Judgement: {result['judgement']}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_composition()
