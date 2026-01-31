import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import json

async def test_mcp_fuji():
    server_params = StdioServerParameters(
        command="/Users/abhishekprasad/workspace/photographi/venv-stable/bin/python",
        args=["-m", "server"],
        env=None
    )
    
    test_folder = "/Volumes/X100Vi/PHOTOGRAPH_STRESS/safe_batch"
    print(f"🚀 Connecting to photographi-mcp server for Fujifilm Stress Test...")
    print(f"📁 Target Folder: {test_folder}")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Analyze Folder
            print("\n📊 Running 'analyze_folder' (Fast Mode)...")
            result = await session.call_tool("analyze_folder", arguments={
                "folder_path": test_folder, 
                "enable_subject_detection": False
            })
            
            raw_text = result.content[0].text
            print(f"DEBUG: Raw Response: {raw_text[:500]}...")
            data = json.loads(raw_text)
            
            if "error" in data:
                print(f"❌ Server Error: {data['error']}")
                return

            print(f"✅ Batch Analysis Complete")
            print(f"   Total Images: {data['totalImages']}")
            print(f"   Average Confidence: {data['averageConfidence']:.2f}")
            
            # 2. Check individual RAF vs JPG success
            results = data.get("results", {})
            raf_count = sum(1 for f in results if f.lower().endswith(".raf"))
            jpg_count = sum(1 for f in results if f.lower().endswith(".jpg"))
            errors = sum(1 for f in results.values() if "error" in f)
            
            print(f"   RAF Analyzed: {raf_count}")
            print(f"   JPG Analyzed: {jpg_count}")
            print(f"   Errors: {errors}")
            
            if errors > 0:
                print("\n❌ Error Details:")
                for filename, res in results.items():
                    if "error" in res:
                        print(f"   - {filename}: {res['error']}")

if __name__ == "__main__":
    asyncio.run(test_mcp_fuji())
