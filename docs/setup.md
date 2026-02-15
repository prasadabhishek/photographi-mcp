# 🔌 Setup & Integration Guide

This guide covers the installation, configuration, and troubleshooting of the **photographi** MCP server.

---

## 🛠️ Prerequisites

1.  **Claude Desktop** installed on macOS (or your preferred MCP-compatible client).
2.  **Python 3.10+** installed on your system.
3.  **photographi** source code or package access.

---

## 📥 Installation

### Option 1: Install via pip (Recommended)
Automatically installs the server and all necessary visual intelligence dependencies:
```bash
pip install photographi-mcp
```

### Option 2: Local Development (Source)
If you are developing or forking the engine:
```bash
git clone https://github.com/prasadabhishek/photographi.git
cd photographi
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## ⚙️ Configuration (Claude Desktop)

Add the following to your `claude_desktop_config.json`:
**Path**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Standard Setup
```json
{
  "mcpServers": {
    "photographi": {
      "command": "photographi",
      "args": []
    }
  }
}
```

### Development Setup (Source)
```json
{
  "mcpServers": {
    "photographi": {
      "command": "/Users/YOUR_USERNAME/workspace/photographi/venv/bin/python",
      "args": ["-m", "server"],
      "env": {
        "PYTHONPATH": "/Users/YOUR_USERNAME/workspace/photographi"
      }
    }
  }
}
```

---

## 🔄 Reloading & Verification

After saving the configuration, you must restart Claude Desktop to initialize the server.

### Verifying Tools
Type `/mcp` or "List available MCP tools" in Claude. You should see all 8 specialized tools:
1.  ✅ `photographi_analyze_photo`
2.  ✅ `photographi_analyze_folder`
3.  ✅ `photographi_rank_photographs`
4.  ✅ `photographi_cull_photographs`
5.  ✅ `photographi_threshold_cull`
6.  ✅ `photographi_get_color_palette`
7.  ✅ `photographi_get_folder_palettes`
8.  ✅ `photographi_get_scene_content`

---

## 🆘 Troubleshooting

### 1. Server Not Appearing
- **Check Logs**: `tail -f ~/Library/Logs/Claude/mcp*.log`
- **Verify Path**: Ensure the `command` path (if using absolute) is correct by running `which photographi` or checking your virtual environment.

### 2. "File Not Found"
The MCP server requires **absolute paths** to access your photos. 
- ❌ `Photos/DSC100.jpg`
- ✅ `/Users/Name/Pictures/DSC100.jpg`

### 3. Import or Execution Errors
If the server crashes on startup, verify the dependencies are correctly installed:
```bash
python -c "from photo_quality_analyzer_core.analyzer import evaluate_photo_quality; print('OK')"
```

---

## 🔒 Advanced options

### Disable Telemetry
Add the environment variable `PHOTOGRAPHI_TELEMETRY_DISABLED=1` to your config's `env` block:
```json
"env": {
  "PHOTOGRAPHI_TELEMETRY_DISABLED": "1"
}
```
