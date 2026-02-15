import pytest
import os
from server import _analyze_photo_logic

def test_granular_metrics(mcp_server, test_assets_dir):
    """Test that granular metrics request works."""
    test_img = str(test_assets_dir / "sharp.jpg")
    
    # Test Selective Metrics
    result_fast = mcp_server._analyze_photo_logic(test_img, metrics=["sharpness", "exposure"], enable_subject_detection=False)
    
    assert "error" not in result_fast
    assert "metrics" in result_fast
    
    metrics_keys = list(result_fast['metrics'].keys())
    assert "sharpness" in metrics_keys
    assert "exposure" in metrics_keys
    assert "focus" not in metrics_keys
    assert "composition" not in metrics_keys

    # Test All Metrics (Default)
    result_all = mcp_server._analyze_photo_logic(test_img, enable_subject_detection=False)
    
    assert "metrics" in result_all
    # Default metrics should be >= 5 (sharpness, exposure, noise, color, etc)
    assert len(result_all['metrics']) >= 5
