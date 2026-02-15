# Extensive Privacy-Preserving Telemetry Plan

Upgrade the telemetry system to capture professional-grade developer insights while maintaining absolute user anonymity.

## Proposed Metrics Schema

The following metrics will be aggregated **locally** and transmitted via the secure relay:

### ⚡ Performance & Efficiency
- **Processing Latency**: Track `total_processing_time_ms` and `avg_time_per_image`.
- **Model Efficiency**: Track `model_load_time_ms` to identify cold-start bottlenecks.
- **Hardware Context**: Record `os_platform` and `cpu_count` (no machine IDs).

### ⚙️ Camera & Optics
- **Device Distribution**: Track aggregate counts of `camera_make` and `camera_model` (e.g., "Sony ILCE-7M4: 15").
- **Optics Context**: Distribution of `lens_model` usage (helps prioritize lens-aware sharpness corrections).

### 🛠️ Technical Operations & Features
- **File Formats**: Track distribution of `jpg`, `png`, `tiff`, and `raw` files.
- **Model Usage**: Compare `nano` vs `xlarge` usage.
- **Feature Depth**: 
    - `subject_detection` usage.
    - `xmp_sidecar` generation count.
    - `color_palette` extraction hits.
    - `rank_photographs` and `cull_photographs` invocation frequency.

### 🚨 System Health & Error Depth
- **Error Categories**: Categorize errors by type (e.g., `IOError`, `ModelError`, `CorruptImage`).
- **Failure Points**: Identify which tool fails most often (e.g., "Ranking failed: 3").

---

## Technical Changes

### 📡 Analytics Engine

#### [MODIFY] [analytics.py](file:///Users/abhishekprasad/workspace/photographi/analytics.py)
- Update `_ensure_file_exists` to include the new expanded data structure.
- Add `track_performance(latency_ms, load_time_ms)` method.
- Add `track_environment()` method (called on init).
- Add `track_feature_usage(feature_name)` method.
- Update `transmit_telemetry` payload to include the new metrics.

### 🏗️ MCP Server Integration

#### [MODIFY] [server.py](file:///Users/abhishekprasad/workspace/photographi/server.py)
- Wrap `evaluate_photo_quality` calls with timers to capture performance metrics.
- Detect file extensions and pass to analytics.
- Categorize exceptions and pass to `track_error(category)`.

---

## Verification Plan

### Automated Tests
- Run `verify.sh` to ensure no regressions in tool signatures.
- Create a specific telemetry test to verify that time-based metrics are correctly recorded and aggregated.

### Manual Verification
- Run a batch analysis of 5 mixed-format images.
- Verify `telemetry.json` contains the expected latency and format distributions.
- Check the Axiom dashboard (via relay) for the new schema keys.
