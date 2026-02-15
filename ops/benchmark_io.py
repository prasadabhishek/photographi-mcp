import time
import os

NETWORK_FILE = "/Volumes/homes/abhishek_rw/Photos/Camera/A6000/Florida 19/10491217/DSC03476.JPG"
LOCAL_FILE = "/Volumes/Extended-1TB/Sony_Test_Sandbox/DSC00554.ARW"

def benchmark_read(filepath, label):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return 0, 0

    size = os.path.getsize(filepath) / (1024 * 1024) # MB
    print(f"📂 Reading {label} ({size:.2f} MB)...")
    
    # Warmup (OS caching check)
    # We consciously DO NOT drop caches to simulate real-world usage where OS might cache recent accesses,
    # BUT for a strict "network vs local" test, the first read is the most important for the "cold" experience.
    
    start = time.time()
    with open(filepath, 'rb') as f:
        _ = f.read()
    duration = time.time() - start
    
    speed = size / duration
    print(f"   ⏱️  Time: {duration:.4f}s")
    print(f"   🚀 Speed: {speed:.2f} MB/s")
    return duration, speed

print("=== 📊 Storage I/O Benchmark ===")
print("Comparing Local SSD vs Network Share (SMB)\n")

# 1. Local Benchmark
local_time, local_speed = benchmark_read(LOCAL_FILE, "Local SSD")

print("-" * 30)

# 2. Network Benchmark
net_time, net_speed = benchmark_read(NETWORK_FILE, "Network (NAS)")

print("\n=== 💡 Analysis ===")
if net_speed > 0:
    ratio = local_speed / net_speed
    print(f"Local storage is {ratio:.1f}x faster than Network.")
    
    # Estimate impact on pipeline
    # Average 24MP RAW is ~24MB.
    raw_size_mb = 24
    local_load_time = raw_size_mb / local_speed
    net_load_time = raw_size_mb / net_speed
    overhead = net_load_time - local_load_time
    
    print(f"\nEstimated Load Time used for 24MB RAW:")
    print(f"   Local:   {local_load_time*1000:.1f} ms")
    print(f"   Network: {net_load_time*1000:.1f} ms")
    print(f"   ⚠️  Network Overhead: +{overhead*1000:.1f} ms per image")
