import pytest
import os
import shutil
import cv2
import numpy as np
from pathlib import Path
import sys

# Ensure photographi packages are in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../photo-quality-analyzer')))

@pytest.fixture(scope="session")
def test_assets_dir(tmp_path_factory):
    """
    Creates a temporary directory with synthetic test assets
    that persist for the entire test session.
    """
    assets_dir = tmp_path_factory.mktemp("assets")
    
    # 1. Create a "perfect" sharp image
    img_sharp = np.zeros((512, 512, 3), dtype=np.uint8)
    cv2.rectangle(img_sharp, (100, 100), (412, 412), (255, 255, 255), -1)
    cv2.putText(img_sharp, "Sharp", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    cv2.imwrite(str(assets_dir / "sharp.jpg"), img_sharp)
    
    # 2. Create a blurry image
    img_blur = cv2.GaussianBlur(img_sharp, (21, 21), 0)
    cv2.imwrite(str(assets_dir / "blur.jpg"), img_blur)
    
    # 3. Create a dark/underexposed image
    img_dark = (img_sharp * 0.2).astype(np.uint8)
    cv2.imwrite(str(assets_dir / "dark.jpg"), img_dark)
    
    # 4. Create a noisy image
    noise = np.random.normal(0, 50, (512, 512, 3)).astype(np.uint8)
    img_noise = cv2.add(img_sharp, noise)
    cv2.imwrite(str(assets_dir / "noise.jpg"), img_noise)
    
    return assets_dir

@pytest.fixture
def mcp_server():
    """
    Returns the imported server module for direct function testing.
    """
    import server
    return server
