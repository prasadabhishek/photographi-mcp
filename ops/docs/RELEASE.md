# Releasing photographi-mcp

This guide details the process for publishing the `photographi-mcp` package to PyPI.

## 📋 Prerequisites
Ensure you have the build tools installed:
```bash
pip install build twine
```

## 🚀 1. Bump Version
Update the `version` string in `pyproject.toml`:
```toml
[project]
version = "0.1.0"  # <--- Update this
```

## 📦 2. Build Artifacts
Clean previous builds and generate new distributions (Source + Wheel):
```bash
rm -rf dist/
python -m build
```
*Output should be in `dist/`: `photographi_mcp-0.1.0.tar.gz` and `photographi_mcp-0.1.0-py3-none-any.whl`.*

## 🧪 3. Verify
Check the package metadata (README rendering, license, etc.):
```bash
twine check dist/*
```

## ☁️ 4. Publish (TestPyPI First)
Start by uploading to TestPyPI to ensure everything looks right:
```bash
twine upload --repository testpypi dist/*
```
*   **Username**: `__token__` (Recommended) or `abhishek.a.prasad`
*   **Password**: Your PyPI API Token (pypi-...) or account password.

*Verify on [test.pypi.org](https://test.pypi.org/project/photographi-mcp/).*

## 🌍 5. Publish (Production)
When ready, upload to the real PyPI. **The first upload registers the package to your account.**
```bash
twine upload dist/*
```
*Verify on [pypi.org](https://pypi.org/project/photographi-mcp/).*

## 🏷️ 6. Git Tag
Tag the release in git:
```bash
git tag v0.1.0
git push origin v0.1.0
```
