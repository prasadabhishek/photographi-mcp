
import os
import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_sony_arw():
    server_params = StdioServerParameters(
        command="/Users/abhishekprasad/workspace/photographi/venv-stable/bin/python",
        args=["-m", "server"],
        env=None
    )
    
    test_path = "/Volumes/Sony/DCIM/100MSDCF/DSC00504.ARW"
    print(f"🚀 Testing Sony ARW: {test_path}")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool("analyze_photo", arguments={
                "image_path": test_path,
                "enable_subject_detection": False
            })
            
            data = json.loads(result.content[0].text)
            if "error" in data:
                print(f"❌ Error: {data['error']}")
            else:
                print(f"✅ Success! Judgement: {data['judgement']}")
                print(f"📊 Confidence: {data['overallConfidence']}")

if __name__ == "__main__":
    asyncio.run(test_sony_arw())
