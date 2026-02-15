# Contributing to photographi

Welcome! `photographi` is a **Local Computer Vision Engine**. We are building the future of privacy-first, programmable photo libraries.

## 🌟 Vision
We believe that:
1.  **Privacy is non-negotiable:** Your photos should never leave your machine to be "understood."
2.  **Photos are Data:** Every image has latent signal (sharpness, noise, subject) that should be queryable.
3.  **Workflows are Personal:** We provide the engine; users build the workflows (Search, Culling, Auditing).

## 🛠️ Development Setup

### 1. The Stack
*   **Core Logic**: `photo-quality-analyzer` (Physics + Neural SDK)
*   **Application**: `photographi` (CLI + MCP Server)
*   **Models**: YOLO26n (Nano Indexing) / YOLO11x (Studio Grade)

### 2. Quickstart (Local Development)

```bash
# 1. Clone the repository
git clone https://github.com/prasadabhishek/photographi.git
cd photographi

# 2. Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 3. Install in Editable Mode
pip install -e .[test]

# 4. Activate Automation Hooks
bash scripts/setup_hooks.sh
```

---

## 🧪 Testing & Verification

We maintain a zero-regression policy. Before pushing any code, you **must** run the local verification suite:

```bash
./verify.sh
```

This runs the full `pytest` suite and ensures cross-platform compatibility. Our **pre-push hook** will automatically block pushes if this suite fails.

---

## 🚀 Release Process

Releases are automated via GitHub Actions:
1. Add release notes to [CHANGELOG.md](CHANGELOG.md) under the `[Unreleased]` or next version header.
2. Run `./scripts/release.sh <version>` to bump version strings and create a git tag.
3. Push the tag: `git push origin v<version>` to trigger the PyPI/GitHub Release pipeline.

---

## 🗺️ Roadmap
We are looking for contributions in:
*   **Video Analysis**: Extending the engine to support `.mp4` and `.mov`.
*   **Facial Recognition**: Local, privacy-first clustering of faces.
*   **New Workflows**: Integrations with Capture One, Lightroom, or Darktable.

---
**License**: MIT
