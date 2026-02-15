# photographi-mcp

**Give your AI the ability to see, analyze, and manage your local photo library.**

`photographi-mcp` is an MCP server that allows LLMs (like Claude) to work with your photos locally. It analyzes things like focus, lighting, and quality automatically—all while keeping your data **100% private**.

Whether you need to find the best shot in a burst, cull a massive shoot, or search your library semantically, `photographi-mcp` gives your AI agent the "visual brain" it needs to get the job done.

---

## � See It In Action

Here are real examples from actual photo analysis:

### Example 1: Excellent Photo
![Best Shot](docs/examples/burst_best.jpg)

```json
{
  "overallConfidence": 0.89,
  "judgement": "Excellent",
  "keyMetrics": {
    "sharpness": 0.94,
    "exposure": 0.87,
    "composition": 0.85
  }
}
```
**Verdict:** Tack sharp on subject, well exposed, strong composition.

---

### Example 2: Poor Photo  
![Worst Shot](/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/burst_worst.jpg)

```json
{
  "overallConfidence": 0.31,
  "judgement": "Poor",
  "keyMetrics": {
    "sharpness": 0.28,
    "exposure": 0.41
  }
}
```
**Verdict:** Motion blur, underexposed, not usable for prints.

---

### Example 3: Technical Breakdown
![Technical Analysis](/Users/abhishekprasad/.gemini/antigravity/brain/e29205bc-6f97-4407-9406-bedc84bab710/technical_example.jpg)

```json
{
  "metrics": {
    "sharpness": { "score": 0.78, "verdict": "Acceptably Sharp" },
    "exposure": { "score": 0.82, "verdict": "Well Exposed" },
    "noise": { "score": 0.71, "verdict": "Low Noise" },
    "focus": { "score": 0.80, "verdict": "Good Focus" }
  }
}
```
**Analysis:** Good overall quality, suitable for web use and medium prints.

---

## 👁️ What It Analyzes

- **Smart Focus**: Detects subjects and verifies they're sharp
- **Exposure**: Catches blown highlights and blocked shadows  
- **Gear-Aware**: Knows your lens's sweet spot for optimal sharpness
- **Composition**: Evaluates framing and subject placement
- **Quality Alerts**: Flags motion blur, diffraction, high ISO noise

For the science and math behind it, see the **[Technical Documentation](https://github.com/prasadabhishek/photo-quality-analyzer/blob/mainline/docs/SCIENCE.md)**.

---

## ⚡ Get Started in 30 Seconds

### Claude CLI (Fastest)
```bash
claude mcp add --scope user photographi uvx photographi-mcp
```

### Claude Desktop (macOS)
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
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

### GitHub Copilot CLI
Add to `~/.config/github-copilot/config.json`:
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

**📖 Full Setup Guide**: [docs/setup.md](docs/setup.md)

---

## � What's Next?

1. **Try it out**: Ask Claude to analyze a photo or cull a folder
2. **Learn the tools**: See all 8 available tools in [docs/setup.md](docs/setup.md#tools)
3. **Upgrade**: Run `uvx --refresh photographi-mcp` for latest features
4. **Advanced setup**: Check [docs/setup.md](docs/setup.md) for local dev, privacy config, and troubleshooting

**Privacy**: Telemetry enabled by default (anonymous aggregates only). [Opt-out instructions](docs/setup.md#privacy).

---

##🗺️ Community

**License**: MIT  
**Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)  
**Issues**: [GitHub Issues](https://github.com/prasadabhishek/photographi-mcp/issues)

Built with science. See [Technical Documentation](https://github.com/prasadabhishek/photo-quality-analyzer/blob/mainline/docs/SCIENCE.md).

---

<div align="center">
  <p>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-Compatible-green.svg" alt="MCP Protocol"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  </p>
  <p>Built with ❤️ for the Creative Community</p>
</div>
