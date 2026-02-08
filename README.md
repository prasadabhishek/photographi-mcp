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

---

## 🔌 Installation & Setup

### Option 1: The Easy Way (pip)
```bash
pip install photographi-mcp
```

**Claude Desktop Configuration** (Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`):
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

### Option 2: For Developers (Source)
If you want to modify the code or contribute:

1.  Clone this repository.
2.  Install dependencies: `pip install -e .`
3.  Point Claude to your local server:

```json
{
  "mcpServers": {
    "photographi": {
      "command": "python3",
      "args": ["/absolute/path/to/photographi/server.py"]
    }
  }
}
```

### 🔒 Privacy Config (Optional)
Telemetry is enabled by default to help us improve the tool. To **disable all usage tracking**, simply add the `--disable-telemetry` flag (see the [Privacy & Telemetry](#-privacy--telemetry) section for details):

```json
{
  "mcpServers": {
    "photographi": {
      "command": "photographi", // or "python3" if using source
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
- **Supports**: JPEG, PNG, RAW (.ARW, .CR2, .NEF), and TIFF.

### 2. `photographi_analyze_folder`
**What it does**: Scans an entire folder and provides a statistical quality report.
- **LLM Use Case**: *"I just finished a shoot; scan the 'Portraits' folder and tell me the overall success rate of the focus."*

### 3. `photographi_rank_photographs`
**What it does**: Identifies the "winners" in a group of photos based on technical perfection.
- **LLM Use Case**: *"I took 10 shots of this bird taking flight. Find the single frame that is the sharpest and best exposed."*

### 4. `photographi_cull_photographs`
**What it does**: Intelligently filters out low-quality "junk" (blurry, dark, or duplicates) into a separate folder.
- **LLM Use Case**: *"Clean up my 'Downloads' folder by moving all the low-quality or blurry screenshots to a culled folder."*

### 5. `photographi_threshold_cull`
**What it does**: A strict "Keep or Toss" tool that sorts photos based on a specific quality score.
- **LLM Use Case**: *"Be strict: sort this folder. Anything with a quality score below 0.7 goes into 'rejects', the rest go into 'selects'."*

### 6. `photographi_get_color_palette`
**What it does**: Extracts the dominant colors from a photo (as Hex codes).
- **LLM Use Case**: *"Look at my best landscape shots and extract a color palette I can use to design my photography portfolio website."*

---

## 🔒 Privacy & Telemetry

`photographi` is built on a **Privacy-First** philosophy. We collect high-level, anonymized usage metrics to help improve the tool, but we guarantee your personal data never leaves your machine.

### Our Privacy Promise
- **Anonymized Aggregates Only**: We **NEVER** collect file names, paths, EXIF metadata, or any identifiers. We only track total counts (e.g., "15 images processed") and quality distributions (e.g., "3 Excellent results").
- **Zero Identification**: We do not use fingerprints, machine IDs, or cookies. Even we cannot tell which user is sending which metrics.
- **Transparency**: You can audit exact collection logic in [`analytics.py`](https://github.com/prasadabhishek/photographi-mcp/blob/mainline/analytics.py).
- **Full Control**: Telemetry is enabled by default to help us improve, but you can opt-out completely with a single flag.

### How to Opt-Out
To disable all telemetry (both local logging and remote transmission), add the `--disable-telemetry` flag to your `mcp_config.json`:

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
> **Open Source Security**: For the official release, we use a **Telemetry Relay** (proxy) to securely manage Axiom tokens. If you are forking this project, see [`docs/telemetry_relay.js`](https://github.com/prasadabhishek/photographi-mcp/blob/mainline/docs/telemetry_relay.js) for instructions on how to set up your own secure metrics relay.

---

---

## 📚 Documentation

*   **[Full Tool Reference (API)](docs/api.md)**: Detailed breakdown of every tool, parameter, and return type.
*   **[System Architecture](docs/architecture.md)**: Deep dive into the Physics/Neural engines and the Privacy-First Telemetry design.
*   **[Telemetry Relay Setup](docs/telemetry_relay.js)**: Instructions for self-hosting the privacy proxy on Cloudflare.

---

## 📊 Performance Benchmark

| Capability | Speed (M1 Max) | Description |
| :--- | :--- | :--- |
| **Technical Scan** | **0.05s** / img | Pure signal processing (Sharpness/Exposure) |
| **Deep Vision** | **0.25s** / img | Full Neural Analysis (YOLO11n Nano) |
| **Studio Grade** | **1.80s** / img | High-precision analysis (YOLO11x Xlarge) |
| **Throughput** | **5,000+** img/hr | Validated for massive shoot culling |

*Tested on 1TB External SSD with 24MP Sony ARW files.*

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
