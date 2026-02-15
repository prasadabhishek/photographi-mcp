import time
import os
import gc
from pathlib import Path
import numpy as np
import cv2
from server import _analyze_photo_logic, _analyze_folder_logic

def run_benchmarks():
    print("\n" + "="*50)
    print(" PHOTOGRAPHI MCP PERFORMANCE BENCHMARK ")
    print("="*50)
    
    # Setup temporary benchmark assets
    bench_dir = Path("bench_assets")
    bench_dir.mkdir(exist_ok=True)
    
    # Create 20 test images
    img = np.zeros((1024, 1024, 3), dtype=np.uint8)
    cv2.rectangle(img, (200, 200), (824, 824), (255, 255, 255), -1)
    for i in range(20):
        cv2.imwrite(str(bench_dir / f"bench_{i:02d}.jpg"), img)
    
    test_img = str(bench_dir / "bench_00.jpg")
    
    # 1. Warm-up & Model Load
    print("\n[1/3] Measuring Model Initialization...")
    start = time.perf_counter()
    _analyze_photo_logic(test_img, model_size="nano")
    nano_load = (time.perf_counter() - start) * 1000
    print(f"Nano Model first run (load + analysis): {nano_load:.2f}ms")
    
    # 2. Single Image Latency (after warm up)
    print("\n[2/3] Measuring Single Image Latency...")
    latencies = []
    for _ in range(10):
        start = time.perf_counter()
        _analyze_photo_logic(test_img, model_size="nano")
        latencies.append((time.perf_counter() - start) * 1000)
    
    avg_lat = sum(latencies) / len(latencies)
    print(f"Average Latency (Nano): {avg_lat:.2f}ms")
    
    # 3. Batch Throughput
    print("\n[3/3] Measuring Batch Throughput (20 images)...")
    start = time.perf_counter()
    _analyze_folder_logic(str(bench_dir), model_size="nano")
    total_time = time.perf_counter() - start
    
    throughput = 20 / total_time
    img_per_hr = throughput * 3600
    
    print(f"Batch Time: {total_time:.2f}s")
    print(f"Throughput: {throughput:.2f} images/sec")
    print(f"Estimated: {img_per_hr:,.0f} images/hour")
    
    print("\n" + "="*50)
    print(" BENCHMARK COMPLETE ")
    print("="*50)
    
    # Cleanup
    for f in bench_dir.glob("*"):
        f.unlink()
    bench_dir.rmdir()

if __name__ == "__main__":
    run_benchmarks()
