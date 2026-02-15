# Changelog

All notable changes to the `photographi-mcp` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
