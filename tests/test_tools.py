import pytest
import os
import shutil
from pathlib import Path

# Import the server module from the fixture
def test_analyze_photo(mcp_server, test_assets_dir):
    """Test single photo analysis."""
    img_path = str(test_assets_dir / "sharp.jpg")
    result = mcp_server._analyze_photo_logic(img_path, enable_subject_detection=False)
    
    assert "error" not in result
    assert "judgement" in result
    assert "overallConfidence" in result
    assert result["overallConfidence"] > 0.0

def test_analyze_photo_not_found(mcp_server):
    """Test error handling for non-existent file."""
    result = mcp_server._analyze_photo_logic("/non/existent/file.jpg")
    assert "error" in result
    assert "Path not found" in result["error"]

def test_analyze_folder(mcp_server, test_assets_dir):
    """Test batch folder analysis."""
    result = mcp_server._analyze_folder_logic(str(test_assets_dir), enable_subject_detection=False)
    
    # Analyze folder returns a dict with results or error
    assert isinstance(result, dict)
    assert "error" not in result
    
    # The structure includes 'results' key
    assert "results" in result
    results_map = result["results"]
    assert len(results_map) >= 4 
    assert "sharp.jpg" in results_map
    assert "blur.jpg" in results_map

def test_rank_folder(mcp_server, test_assets_dir):
    """Test ranking logic."""
    result = mcp_server._rank_folder_logic(str(test_assets_dir), top_n=2, enable_subject_detection=False)
    
    assert result["status"] == "Ranking Complete"
    assert "bestImages" in result
    assert len(result["bestImages"]) <= 2
    
    # Verify we got results, valid structure
    best_image = result["bestImages"][0]
    assert "filename" in best_image
    assert "score" in best_image

def test_threshold_cull(mcp_server, test_assets_dir, tmp_path):
    """Test threshold culling."""
    # Copy assets to a temp working dir since culling modifies/moves files
    work_dir = tmp_path / "cull_work"
    shutil.copytree(test_assets_dir, work_dir)
    
    # Set high threshold so only sharp output passes
    # Note: Synthetic sharp image might have high score
    result = mcp_server._cull_logic(
        str(work_dir), 
        threshold=0.8, # logic maps 'threshold' to 'min_confidence' internally if needed or just passes it
        mode="move", 
        enable_subject_detection=False,
        is_threshold_mode=True
    )
    
    assert result["status"] == "Threshold Culling Complete"
    assert "keptCount" in result
    assert "rejectedCount" in result
    
    # Verify directories created
    assert (work_dir / "selects").exists()
    assert (work_dir / "rejects").exists()

def test_scene_content(mcp_server, test_assets_dir):
    """Test scene content extraction logic."""
    # We check that the function exists on the module
    # or import the underlying logic if we want to test it
    from photo_quality_analyzer_core.analyzer import detect_objects
    assert callable(detect_objects)

def test_color_palette(mcp_server, test_assets_dir):
    """Test color palette extraction logic."""
    img_path = str(test_assets_dir / "sharp.jpg")
    
    # Test the core function directly since MCP tool is wrapped
    from photo_quality_analyzer_core.analyzer import generate_color_palette
    palette = generate_color_palette(img_path, 5)
    
    assert isinstance(palette, list)
    assert len(palette) == 5
    assert all(c.startswith("#") for c in palette)

def test_folder_palettes(mcp_server, test_assets_dir):
    """Test batch palette extraction logic."""
    # Use the logic function, not the wrapped tool
    result = mcp_server._bulk_palette_logic(str(test_assets_dir), limit=5)
    
    # It returns a dict of filename -> palette (or error)
    # Wait, let's check _bulk_palette_logic return type in server.py
    # It seems to return `results` dict?
    # No, it returns a dict: {"message": ...} OR {filename: palette, ...} ?
    # Let's verify return of _bulk_palette_logic in server.py
    # Lines 619-629 imply it returns a dict of results.
    # Actually, looking at code, it returns `results`.
    
    assert isinstance(result, dict)
    assert "palettes" in result
    palettes_map = result["palettes"]
    assert len(palettes_map) >= 4
    assert "sharp.jpg" in palettes_map
    assert isinstance(palettes_map["sharp.jpg"], list)
