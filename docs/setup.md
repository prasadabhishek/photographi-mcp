# 🔌 Setup & Integration Guide

This guide covers the installation, configuration, and troubleshooting of the **photographi** MCP server.

---

## 🛠️ Prerequisites

1.  **Claude Desktop** installed on macOS (or your preferred MCP-compatible client).
2.  **Python 3.10+** installed on your system.
3.  **photographi** source code or package access.

---

## 📥 Zero-Install Setup (Recommended)

The fastest way to run `photographi` is via **Claude CLI** (Claude Code) or **uvx**. These methods require no manual virtual environment management.

### Claude CLI (Claude Code)
Install and configure automatically with a single command:
```bash
claude mcp add photographi uvx photographi-mcp
```

### GitHub Copilot CLI
Add this to your `~/.config/github-copilot/config.json`:

```json
{
  "mcp_servers": {
    "photographi": {
      "command": "uvx",
      "args": ["photographi-mcp"]
    }
  }
}
```

### Claude Desktop
Add this to your `claude_desktop_config.json`:
**Path**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "photographi": {
      "command": "uvx",
      "args": ["photographi-mcp"]
    }
  }
}
```

---

## 🛠️ Advanced: Local Development Setup

If you are developing or want to use a local clone:

1. **Install in Editable Mode**:
   ```bash
   pip install -e .
   ```

2. **Manual Configuration**:
   ```json
   "photographi": {
     "command": "photographi",
     "args": []
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
