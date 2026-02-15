# Photographi MCP Test Suite Breakdown

This document provides a detailed overview of the testing framework for the `photographi` MCP server, including unit, integration, and performance tests.

## 🧪 Shared Fixtures & Configuration

### `conftest.py`
- **Purpose**: Provides shared `pytest` fixtures used across multiple test modules.
- **Key Fixtures**:
    - `test_assets_dir`: Generates a temporary directory with synthetic test images (sharp, blur, dark, noise) for every test run to ensure consistent evaluation baselines.
    - `mcp_server`: Provides an instance of the MCP server context for direct logic testing.

---

## 🛠️ Main Test Suite

### `test_workflow.py` (Master Integration)
- **What it tests**: The complete End-to-End user flow.
- **Coverage**:
    - `analyze` -> `rank` -> `cull` logic.
    - Pagination stability (verifies `limit` and `offset` behavior).
    - File system state changes (ensures files are moved to `culled_photos/` correctly).

### `test_tools.py`
- **What it tests**: Functional correctness of every MCP tool.
- **Coverage**:
    - Verifies return structures, keys, and data types for all tools.
    - Specifically covers `photographi_get_scene_content`, `photographi_get_folder_palettes`, and technical analysis tools.

### `test_mcp_server.py`
- **What it tests**: The bridge between the MCP protocol and the analytical logic.
- **Coverage**:
    - Server initialization and tool registration.
    - Response formatting and error bubbling.

### `test_edge_cases.py`
- **What it tests**: Robustness against invalid input and weird file system states.
- **Coverage**:
    - **Security**: Verifies `_validate_path` prevents path traversal.
    - **Resilience**: Tests behavior with empty directories, non-image files, and corrupted assets.

### `test_color_palette.py`
- **What it tests**: The K-Means clustering logic for palette extraction.
- **Coverage**:
    - Accuracy of color extraction.
    - Handling of monochrome vs. colorful images.

---

## 📊 Performance Testing

### `benchmark_performance.py`
- **What it tests**: Throughput and latency of the analytical engine.
- **Metrics tracked**:
    - **Warm-up Time**: Initial model load latency.
    - **Single Latency**: Average time per image (Nano model).
    - **Batch Throughput**: Projected images-per-hour capacity.

---

## 🔗 Legacy & Unit Integration (`/tests/integration`)

These tests cover specific signal processing and analytical components:

- **`test_composition.py`**: Validates the "Rule of Thirds" and subject placement analysis.
- **`test_enhanced_culling.py`**: Verifies strict threshold culling vs. soft culling.
- **`test_granular_metrics.py`**: Details metrics for sharpness, exposure, and noise.
- **`test_batch.py`**: Stress test for directory-scale processing.
- **`test_mock_exif.py`**: Verifies camera-aware normalization (FFT/DLA) using simulated EXIF data.

---

## 🚀 How to Run

To run the full suite:
```bash
source venv/bin/activate
pytest tests/ -v
```

To run a specific test file:
```bash
pytest tests/test_workflow.py -v
```
