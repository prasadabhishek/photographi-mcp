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
*   **Models**: YOLO12x (Subject Detection)

### 2. Quickstart
```bash
# Clone the repository
git clone https://github.com/yourusername/photographi.git
cd photographi

# Install dependencies (including the local core library)
pip install -e .

# Run the integration test suite
python tests/integration/master_test_suite.py
```

## 🧪 Testing Strategy
We use a **Dual-Verification System**:
1.  **Unit Tests**: Located in the base library. Verify pure physics (e.g., "Is this FFT calculation correct?").
2.  **Integration Tests**: Located here. Verify the application (e.g., "Does the XMP file get written correctly?").

**Please ensure all tests pass before submitting a PR.**

## 🗺️ Roadmap
We are looking for contributions in:
*   **Video Analysis**: Extending the engine to support `.mp4` and `.mov`.
*   **Facial Recognition**: Local, privacy-first clustering of faces.
*   **New Workflows**: Integrations with Capture One or Darktable.

---
**License**: MIT
