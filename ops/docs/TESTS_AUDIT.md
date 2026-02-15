# photographi: Test Architecture Audit

This document provides a comprehensive index of the 56+ tests that safeguard the `photographi` ecosystem, categorized by their scope and purpose.

---

## 1. Base Library: `photo-quality-analyzer`
These tests verify the core optical physics, signal processing, and RAW support.

| Test Suite | Category | Purpose |
| :--- | :--- | :--- |
| `test_metrics.py` | Unit | Verifies base Sharpness, Exposure Clipping, and Noise algorithms. |
| `test_phase2_metrics.py` | Unit | Validates advanced physics (Dynamic Range, Headroom, Focus DOF). |
| `test_iso_noise.py` | Unit | Verifies the ISO-Adaptive noise floor normalization. |
| `test_raw.py` | Unit | Ensures high-fidelity Sony RAW (.ARW) preview extraction. |
| `test_workflow_v5.py` | Integration | Validates the "move to selects/rejects" culling logic. |
| `test_lib_completeness.py` | Unit | Checks API consistency and camera database resolution. |

---

## 2. MCP Server: `photographi`
These tests ensure the MCP layer correctly bridges the AI Agent to the core engine.

| Test Suite | Category | Purpose |
| :--- | :--- | :--- |
| `test_mcp_server.py` | Unit/Int | Verifies Ranking, Analysis summaries, and Score-to-Judgement mapping. |
| `test_color_palette.py` | Unit | Validates K-Means extraction for both JPEG and RAW files. |
| `integration/master_suite.py` | End-to-End | Executes a full pipeline: Batch Scan -> Rank -> Threshold Cull -> XMP Write. |

---

## 3. How to Execute
We provide a unified verification script that handles all environment variables and path resolutions.

### Run All Tests
```bash
./verify.sh
```

### Run Specific Suites
```bash
# Core only
pytest ../photo-quality-analyzer/tests

# MCP only
python -m unittest discover tests
```
