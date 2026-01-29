import json
from server import _analyze_photo_logic

def test_granular_metrics():
    test_img = "/Users/abhishekprasad/workspace/photographi/test_culling/good_image.png"
    
    print("\n🎯 Testing Selective Metrics: ['sharpness', 'exposure']...")
    result_fast = _analyze_photo_logic(test_img, metrics=["sharpness", "exposure"])
    print(f"Metrics count: {len(result_fast['metrics'])}")
    print(f"Metrics returned: {list(result_fast['metrics'].keys())}")
    
    if "focus" not in result_fast['metrics'] and "composition" not in result_fast['metrics']:
        print("✅ Success: Focus and Composition skipped.")
    else:
        print("❌ Error: Extra metrics returned.")

    print("\n🎯 Testing All Metrics (Default)...")
    result_all = _analyze_photo_logic(test_img)
    print(f"Metrics count: {len(result_all['metrics'])}")
    
    if len(result_all['metrics']) >= 7:
        print("✅ Success: All metrics returned by default.")
    else:
        print(f"❌ Error: Not all metrics returned. Found: {list(result_all['metrics'].keys())}")

if __name__ == "__main__":
    test_granular_metrics()
