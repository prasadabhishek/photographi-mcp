# Claude Desktop MCP Integration Guide

This guide shows how to integrate the **photographi** MCP server with Claude Desktop for interactive photo analysis.

---

## Prerequisites

1. **Claude Desktop** installed on macOS
2. **photographi** installed in a virtual environment
3. **photo-quality-analyzer-core** installed (dependency)

---

## Installation Steps

### 1. Install the MCP Server

From the `photographi` directory:

```bash
# Create and activate virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate

# Install the core library
pip install /Users/abhishekprasad/workspace/photo-quality-analyzer

# Install the MCP server
pip install -e .
```

### 2. Configure Claude Desktop

Edit Claude Desktop's configuration file:

**File Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Add this configuration**:

```json
{
  "mcpServers": {
    "photographi": {
      "command": "/Users/abhishekprasad/workspace/photographi/venv/bin/python",
      "args": [
        "-m",
        "server"
      ],
      "env": {
        "PYTHONPATH": "/Users/abhishekprasad/workspace/photographi"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

After saving the configuration:
1. Quit Claude Desktop completely
2. Relaunch Claude Desktop
3. The `photographi` server should initialize automatically

---

## Available Tools

Once connected, Claude will have access to these tools:

| Tool | Description |
|------|-------------|
| `photographi_analyze_photo` | Deep technical analysis of a single photo |
| `photographi_analyze_folder` | Quick batch scan of a folder |
| `photographi_rank_photographs` | Find the best N images in a folder |
| `photographi_cull_photographs` | Move low-quality images to a culled folder |
| `photographi_threshold_cull` | Binary selection based on confidence threshold |
| `photographi_get_color_palette` | Extract dominant colors from an image |
| `photographi_get_folder_palettes` | Batch color palette extraction |
| `photographi_get_scene_content` | Quick scene intelligence (NEW) |

---

## Example Usage with Claude

Once integrated, you can ask Claude:

```
Analyze the photo at /Volumes/homes/abhishek_rw/Photos/Camera/A6000/Florida 19/10291215/DSC00875.JPG and tell me about its technical quality.
```

Or for batch operations:

```
Scan the folder /Volumes/homes/abhishek_rw/Photos/Camera/A6000/Florida 19/10291215 and show me the top 10 sharpest images.
```

Or for scene intelligence:

```
What objects are in /Volumes/homes/abhishek_rw/Photos/Camera/A6000/Florida 19/10291215/DSC00875.JPG?
```

---

## Troubleshooting

### 1. Server Not Appearing in Claude Desktop

**Check the logs**:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Common Issues**:
- Incorrect Python path in config (verify with `which python` in your venv)
- Missing dependencies (re-run `pip install -e .`)
- PYTHONPATH not set correctly

### 2. "File Not Found" Errors

**Issue**: The MCP server can't access the file path.

**Solution**: Use absolute paths when referencing files:
```
/Volumes/homes/abhishek_rw/Photos/Camera/A6000/Florida 19/10291215/DSC00875.JPG
```

### 3. Performance Issues on Large Folders

**Issue**: Analyzing 1000+ images is slow.

**Solution**: Use the `photographi_threshold_cull` or `photographi_rank_photographs` tools which are optimized for large batches.

---

## Testing the Integration

### Quick Verification

1. Open Claude Desktop
2. Look for the 🔌 icon in the bottom-left (MCP servers connected)
3. Type: "List available MCP tools"
4. Verify `photographi_` tools appear

### End-to-End Test

Ask Claude:
```
Use photographi to analyze /Volumes/homes/abhishek_rw/Photos/Camera/A6000/Florida 19/10291215/DSC00875.JPG
```

Expected response should include:
- Sharpness score
- Exposure assessment
- Detected objects (if subject detection is enabled)
- Overall confidence

---

## Advanced Configuration

### Disable Telemetry

Add to the `env` block in Claude Desktop config:
```json
"env": {
  "PYTHONPATH": "/Users/abhishekprasad/workspace/photographi",
  "PQA_DISABLE_TELEMETRY": "1"
}
```

### Custom YOLO Model

If you have a custom trained model:
```json
"env": {
  "PYTHONPATH": "/Users/abhishekprasad/workspace/photographi",
  "PQA_MODEL_PATH": "/path/to/custom/model.onnx"
}
```

---

## Uninstallation

To remove the MCP server from Claude Desktop:

1. Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Remove the `"photographi"` entry from `mcpServers`
3. Restart Claude Desktop
