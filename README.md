# photographi-mcp

**Give your AI the ability to see, analyze, and manage your local photo library.**

`photographi-mcp` is an MCP server that allows LLMs (like Claude) to work with your photos locally. It analyzes things like focus, lighting, and quality automatically—all while keeping your data **100% private**.

Whether you need to find the best shot in a burst, cull a massive shoot, or search your library semantically, `photographi-mcp` gives your AI agent the "visual brain" it needs to get the job done.

---

## 👁️ What It Sees

The engine analyzes every pixel to understand exactly what happened when you pressed the shutter:

*   **Smart Focus**: It finds the main subject of your photo and makes sure it's actually sharp.
*   **Lighting Check**: It looks for photos that are too bright or too dark, and finds "hidden" details in the shadows.
*   **Gear Awareness**: It understands your specific camera and lens to know what a "perfect" shot should look like for your equipment.
*   **Composition**: It evaluates how the photo is organized and if there is enough space around the subject.
*   **Quality Alerts**: It catches common issues, like when your settings are accidentally making your images look soft or fuzzy.

For the math and signal processing details, see the **[Technical Science Documentation](https://github.com/prasadabhishek/photo-quality-analyzer/blob/mainline/docs/SCIENCE.md)**.

---

## 🔌 Installation & Setup

### Install via pip
```bash
pip install photographi-mcp
```

---

### Option A: Claude Desktop Integration

**Configuration File**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

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

**For Development (Source Installation)**:
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

Restart Claude Desktop after saving the configuration.

📖 **Detailed Guide**: See [docs/setup.md](docs/setup.md)

---

### Option B: GitHub Copilot CLI Integration

**Configuration File**: `~/.config/github-copilot/config.json`

```json
{
  "mcp_servers": {
    "photographi": {
      "command": "photographi",
      "args": []
    }
  }
}
```

**For Development (Source Installation)**:
```json
{
  "mcp_servers": {
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

Restart your terminal session to activate the MCP server.

**Quick Test**:
```bash
gh copilot explain "Use photographi to analyze this image: /path/to/photo.jpg"
```

---

### 🔒 Privacy Config (Optional)
Telemetry is enabled by default to help us improve the tool. To **disable all usage tracking**, add the `--disable-telemetry` flag:

```json
{
  "mcpServers": {  // or "mcp_servers" for Copilot CLI
    "photographi": {
      "command": "photographi",
      "args": ["--disable-telemetry"]
    }
  }
}
```

---

## 🛠️ Tools (MCP)

`photographi-mcp` gives your AI agent (like Claude) a set of powerful tools to interact with your photos. Here is how to use them:

### 1. `photographi_analyze_photo`
**What it does**: Performs a deep technical audit of a single image.
- **LLM Use Case**: *"Audit this RAW file and tell me if the focus is sharp enough for a large print."*
- **Supports**: JPEG, PNG, RAW (.ARW, .CR2, .NEF, .DNG, .CR3, etc.), and TIFF.

### 2. `photographi_analyze_folder`
**What it does**: Scans an entire folder and provides a statistical quality report (with pagination).
- **LLM Use Case**: *"I just finished a shoot; scan the 'Portraits' folder and tell me the overall success rate of the focus."*

### 3. `photographi_rank_photographs`
**What it does**: Identifies the "winners" in a group of photos based on technical perfection.
- **LLM Use Case**: *"I took 10 shots of this bird taking flight. Find the single frame that is the sharpest and best exposed."*

### 4. `photographi_cull_photographs`
**What it does**: Intelligently filters out low-quality "junk" (blurry, dark, or duplicates) into a separate `culled_photos` folder.
- **LLM Use Case**: *"Clean up my 'Downloads' folder by moving all the low-quality or blurry screenshots to a culled folder."*

### 5. `photographi_threshold_cull`
**What it does**: A strict "Keep or Toss" tool that sorts photos based on a specific quality score into `selects/` or `rejects/`.
- **LLM Use Case**: *"Be strict: sort this folder. Anything with a quality score below 0.7 goes into 'rejects', the rest go into 'selects'."*

### 6. `photographi_get_color_palette`
**What it does**: Extracts the dominant colors from a photo (as Hex codes).
- **LLM Use Case**: *"Look at my best landscape shots and extract a color palette I can use to design my photography portfolio website."*

### 7. `photographi_get_folder_palettes`
**What it does**: Extracts dominant colors for every image in a folder (with pagination).
- **LLM Use Case**: *"Analyze all photos in this folder and give me their color palettes so I can group them by mood."*

### 8. `photographi_get_scene_content`
**What it does**: Identifies key objects (people, animals, vehicles, etc.) for quick indexing.
- **LLM Use Case**: *"Which photos in this folder contain a 'dog'?"*

---

## 🔒 Privacy & Telemetry

`photographi` is built on a **Privacy-First** philosophy. We collect high-level, anonymized usage metrics to help improve the tool, but we guarantee your personal data never leaves your machine.

### Our Privacy Promise
- **Anonymized Aggregates Only**: We **NEVER** collect file names, paths, EXIF metadata, or any identifiers. We only track total counts (e.g., "15 images processed") and quality distributions (e.g., "3 Excellent results").
- **Zero Identification**: We do not use fingerprints, machine IDs, or cookies. Even we cannot tell which user is sending which metrics.
- **Transparency**: You can audit exact collection logic in [`analytics.py`](https://github.com/prasadabhishek/photographi-mcp/blob/mainline/analytics.py).
- **Full Control**: Telemetry is enabled by default to help us improve, but you can opt-out completely with a single flag.

### How to Opt-Out
To disable all telemetry (both local logging and remote transmission), you can either set the environment variable `PHOTOGRAPHI_TELEMETRY_DISABLED=1`, or add the `--disable-telemetry` flag to your `mcp_config.json`:

```json
{
  "mcpServers": {
    "photographi": {
      "command": "python",
      "args": [
        "/absolute/path/to/photographi/server.py",
        "--disable-telemetry"
      ]
    }
  }
}
```

> **Note:**
> **Open Source Security**: For the official release, we use a **Telemetry Relay** (proxy) to securely manage Axiom tokens. If you are forking this project, see [`docs/telemetry-relay.js`](https://github.com/prasadabhishek/photographi-mcp/blob/mainline/docs/telemetry-relay.js) for instructions on how to set up your own secure metrics relay.

---

---

## 📚 Documentation

*   **[Full Tool Reference (API)](docs/api-reference.md)**: Detailed breakdown of every tool, parameter, and return type.
*   **[System Architecture](docs/architecture.md)**: Deep dive into the Physics/Neural engines and the Privacy-First Telemetry design.
*   **[Telemetry Relay Setup](docs/telemetry-relay.js)**: Instructions for self-hosting the privacy proxy on Cloudflare.

---

## 📊 Performance Benchmark

| Capability | Speed (M1/M2/M3) | Description |
| :--- | :--- | :--- |
| **Model Load** | **~0.50s** | One-time initialization of YOLO26n ONNX model |
| **Technical Scan** | **~0.44s** / img | Full Signal Processing + AI Subject Detection (Nano) |
| **Throughput** | **~28,000** img/hr | Validated batch processing speed for massive culls |
| **Scalability** | **Unlimited** | Verified pagination stability for 10,000+ folders |

*Tested on local Apple Silicon hardware with 1024x1024 synthetic assets. High-resolution RAW files may vary based on disk I/O.*

---

## 🏗️ Technology

`photographi-mcp` is built on top of the **[photo-quality-analyzer-core](https://pypi.org/project/photo-quality-analyzer-core/)** engine. This core library provides the signal processing, physics-based metrics, and neural network logic that powers the analysis.

---

<div align="center">
  <p>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-Compatible-green.svg" alt="MCP Protocol"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  </p>
  <p>Built with ❤️ for the Creative Community</p>
</div>
