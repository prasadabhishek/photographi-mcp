# Changelog

All notable changes to the `photographi-mcp` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2026-02-15

### Fixed
- **Dependency Sync**: Updated requirement to `photo-quality-analyzer-core>=0.8.4` to ensure latest silhouette fixes and legacy cleanups are utilized.
- **Workflow Tests**: Adjusted integration test assertions to handle "technical veto" scoring caps (0.2) on synthetic test images.

## [0.2.3] - 2026-02-15

### Fixed
- **Silhouette Trap**: Corrected a major technical flaw where building silhouettes and high-contrast edges could trick the engine into a near-perfect sharpness score.
- **Gradient Sparsity Check**: Implemented volumetric texture analysis to distinguish paper-thin contrast edges from actual volumetric sharpness.
- **FFT Frequency Analysis**: Added a second spectral check in the frequency domain to verify real micro-texture.

### ⚡ Performance
- **Wait Time Reduced**: Optimized the analysis pipeline for high-resolution images. Ranking 100 images now takes ~26 seconds (0.26s/photo), down from several minutes.
- **Selective Forensics**: "Fast Mode" now correctly leverages downsampled analysis for all technical metrics including FFT and Noise, maintaining speed without losing accuracy for triage.

## [0.2.2] - 2026-02-15
### Changed
- **Culling Logic**: `photographi_cull_photographs` now keeps "Selects" in their original folder and ONLY moves "Rejects" to a `culled_photos/` subfolder. This is a non-breaking workflow improvement.
- **Defaults**: Increased default `limit` from 50 to 100 for all batch tools to reduce pagination friction.
- **Tool Descriptions**: Improved all MCP tool docstrings to be more actionable and LLM-friendly:
  - Clearly explain what each tool does and when to use it
  - Document the new culling behavior (selects stay in place)
  - Standardize `fast_mode` parameter descriptions across all tools
  - Add return format details and use case guidance
- **Docs**: Clarified `fast_mode=True` default in all tool descriptions.

## [0.2.1] - 2026-02-15

### Fixed
- **Performance Hotfix**: Critical fix for RAW file loading in Fast Mode. Previously, the engine loaded full-resolution RAW data before downsampling for `photographi_cull_photographs`. Now, it correctly uses `rawpy` embedded thumbnails or previews, restoring sub-second analysis speeds.

## [0.2.0] - 2026-02-15

### ⚡ Performance & Scalability
- **Concurrency**: Implemented `ThreadPoolExecutor` for all batch operations (`analyze_folder`, `cull_photographs`, `rank_photographs`), enabling parallel processing of 4-8 images.
- **Pagination**: Added `limit` and `offset` parameters to all batch tools, supporting large dataset processing without timeouts.
- **Fast Mode**: All batch tools now default to `fast_mode=True` (downsampled analysis) for rapid triage.
- **Thread Safety**: Fixed race conditions in `AnalyticsManager` to support concurrent telemetry.

### 🛠️ Fixes
- **Renaming**: Standardized internal logic functions (`_cull_logic` vs `_threshold_cull_logic`).
- **Stability**: Improved error handling in batch executors.

## [0.1.3] - 2026-02-15

### Fixed
- Removed `tqdm` dependency and all progress bars from the MCP server. This eliminates `stdout` noise permanently and reduces package bloat.
- Verified that all non-protocol output is strictly isolated from `stdout` by forcing logging to `sys.stderr`.

## [0.1.2] - 2026-02-15

### Added
- Initial release of the `photographi` MCP server.
- Deep technical photo analysis (Sharpness, Exposure, Noise).
- AI-powered subject detection and context-aware metering.
- Batch tools for ranking and culling photographs.
- Color palette extraction and scene intelligence.
- Multi-OS CI/CD pipeline (Ubuntu, Windows, macOS).
- Privacy-first telemetry system with local-first aggregation.
- Git pre-push hooks for automated code quality verification.
