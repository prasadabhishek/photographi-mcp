# Reloading MCP Servers in Claude Desktop

After making changes to the `photographi` MCP server code or installing updates, Claude Desktop needs to reload the server to pick up the new tools.

## Method 1: Full Restart (Recommended)

1. **Quit Claude Desktop completely**
   - Use `Cmd+Q` or click `Claude → Quit Claude`
   - Verify it's fully closed (check Activity Monitor if unsure)

2. **Relaunch Claude Desktop**
   - The MCP server will initialize with the latest code

## Method 2: Quick Reload (if supported)

Some versions of Claude Desktop support reloading MCP servers without a full restart:

1. Open the MCP tools panel (`/mcp`)
2. Look for a "Reload" or "Refresh" button
3. Click to reinitialize all servers

## Verifying New Tools

After reloading, check that all 8 tools are visible:

```
/mcp
```

Expected tools:
1. ✅ `photographi_analyze_photo`
2. ✅ `photographi_analyze_folder`
3. ✅ `photographi_rank_photographs`
4. ✅ `photographi_cull_photographs`
5. ✅ `photographi_threshold_cull`
6. ✅ `photographi_get_color_palette`
7. ✅ `photographi_get_folder_palettes`
8. ✅ `photographi_get_scene_content` *(NEW)*

## Troubleshooting

### Tools Still Missing After Restart

1. **Check the config file path**:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Verify the Python path**:
   ```bash
   /Users/abhishekprasad/workspace/photographi/venv/bin/python -m server --help
   ```

3. **Check Claude's MCP logs**:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

4. **Reinstall the MCP server**:
   ```bash
   cd /Users/abhishekprasad/workspace/photographi
   source venv/bin/activate
   pip install -e . --force-reinstall
   ```

### Server Crashes on Startup

Check for import errors:
```bash
/Users/abhishekprasad/workspace/photographi/venv/bin/python -c "from photo_quality_analyzer_core.analyzer import detect_objects; print('OK')"
```

If this fails, the core library needs to be reinstalled:
```bash
pip install /Users/abhishekprasad/workspace/photo-quality-analyzer --force-reinstall
```
