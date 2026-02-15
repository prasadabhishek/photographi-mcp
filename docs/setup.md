# photographi-mcp Setup & Configuration

This guide covers advanced configuration, local development, and troubleshooting for `photographi-mcp`.

## 🔄 Upgrading

To upgrade to the latest version of `photographi-mcp`, run:

```bash
uvx --refresh photographi-mcp
```

This command forces `uvx` to fetch and install the newest version from PyPI.

**When to upgrade:**
- After a new release is announced
- If you're experiencing issues that might be fixed in a newer version
- To get the latest features and improvements

**Check your current version:**
```bash
uvx photographi-mcp --version
```

---

## 🔒 Privacy & Telemetry

`photographi` is built on a **Privacy-First** philosophy. We collect high-level, anonymized usage metrics to help improve the tool, but we guarantee your personal data never leaves your machine.

### Our Privacy Promise
- **Anonymized Aggregates Only**: We **NEVER** collect file names, paths, EXIF metadata, or any identifiers. We only track total counts (e.g., "15 images processed") and quality distributions (e.g., "3 Excellent results").
- **Zero Identification**: We do not use fingerprints, machine IDs, or cookies. Even we cannot tell which user is sending which metrics.
- **Transparency**: You can audit exact collection logic in [`analytics.py`](../analytics.py).
- **Full Control**: Telemetry is enabled by default to help us improve, but you can opt-out completely with a single flag.

### How to Opt-Out
To disable all telemetry (both local logging and remote transmission), you can either set the environment variable `PHOTOGRAPHI_TELEMETRY_DISABLED=1`, or add the `--disable-telemetry` flag to your `mcp_config.json`:

```json
{
  "mcpServers": {
    "photographi": {
      "command": "uvx",
      "args": ["photographi-mcp", "--disable-telemetry"]
    }
  }
}
```

---

## 🛠️ Tools Reference

`photographi-mcp` provides several tools for your AI agent.

### 1. `photographi_analyze_photo`
Performs a deep technical audit of a single image.
- **Supports**: JPEG, PNG, RAW (.ARW, .CR2, .NEF, .DNG, .CR3, etc.), and TIFF.

### 2. `photographi_analyze_folder`
Scans an entire folder and provides a statistical quality report (with pagination).

### 3. `photographi_rank_photographs`
Identifies the "winners" in a group of photos based on technical perfection.

### 4. `photographi_cull_photographs`
Intelligently filters out low-quality "junk" (blurry, dark, or duplicates) into a separate `culled_photos` folder.
> [!TIP]
> **Selects stay in place**: New in v0.2.2—only rejected photos are moved.

### 5. `photographi_threshold_cull`
A strict "Keep or Toss" tool that sorts photos based on a specific quality score into `selects/` or `rejects/`.

### 6. `photographi_get_color_palette` / `photographi_get_folder_palettes`
Extracts dominant colors from images as Hex codes.

### 7. `photographi_get_scene_content`
Identifies key objects (people, animals, vehicles, etc.) for quick indexing.

---

## 🏗️ Local Development

If you want to contribute or edit the source code:

1. **Setup**:
   ```bash
   git clone https://github.com/prasadabhishek/photographi.git
   cd photographi
   uv venv
   source .venv/bin/activate
   pip install -e .
   ```

2. **Configuration**:
   Point your `command` to the local `photographi` executable or use the absolute path to your venv's python.

---

## 📊 Performance Benchmark

| Capability | Speed (M1/M2/M3) | Description |
| :--- | :--- | :--- |
| **Model Load** | **~0.38s** | One-time initialization of YOLO26n ONNX model |
| **Technical Scan** | **~0.19s** / img | **Fast Mode** (Downsampled 40MP -> 1024px) + Concurrency |
| **Forensic Scan** | **~1.50s** / img | Full-Resolution Analysis (Opt-in via `fast_mode=False`) |

---

## 🤝 Contributing
Contributions are welcome! Please read `CONTRIBUTING.md` for details.
