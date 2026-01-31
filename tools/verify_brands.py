
import os
import json
import asyncio
import argparse
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def verify_directory(directory_path: str):
    server_params = StdioServerParameters(
        command="/Users/abhishekprasad/workspace/photographi/venv-stable/bin/python",
        args=["-m", "server"],
        env=None
    )
    
    print(f"🔬 Starting Multi-Brand Verification in: {directory_path}")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool("analyze_folder", arguments={
                "folder_path": directory_path,
                "enable_subject_detection": False
            })
            
            data = json.loads(result.content[0].text)
            
            print("\n--- Compatibility Report ---")
            results = data.get("results", {})
            for filename, info in results.items():
                status = "✅ PASS" if "error" not in info else f"❌ FAIL ({info['error']})"
                judgement = info.get('judgement', 'N/A')
                print(f"{filename: <25} | {status: <10} | {judgement}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Path to folder containing sample RAWs")
    args = parser.parse_args()
    
    asyncio.run(verify_directory(args.dir))
