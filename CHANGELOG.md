# Changelog

All notable changes to the `photographi-mcp` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-02-15

### Fixed
- Explicitly forced logging to `sys.stderr` to prevent protocol corruption on `stdout`.
- Simplified `uvx` installation instructions to include the `--quiet` flag.

## [0.1.1] - 2026-02-15

### Added
- Initial release of the `photographi` MCP server.
- Deep technical photo analysis (Sharpness, Exposure, Noise).
- AI-powered subject detection and context-aware metering.
- Batch tools for ranking and culling photographs.
- Color palette extraction and scene intelligence.
- Multi-OS CI/CD pipeline (Ubuntu, Windows, macOS).
- Privacy-first telemetry system with local-first aggregation.
- Git pre-push hooks for automated code quality verification.
