import pytest
import os
import shutil
from server import _validate_path

def test_validate_path_security():
    """Test path validation security."""
    
    # Valid existing file
    assert _validate_path(__file__, must_exist=True, expected_type="file")
    
    # Non-existent file
    with pytest.raises(ValueError, match="Path not found"):
        _validate_path("/path/to/nonexistent/file.txt", must_exist=True)
        
    # Wrong type (file expected, dir given)
    current_dir = os.path.dirname(__file__)
    with pytest.raises(ValueError, match="Expected file but found directory"):
        _validate_path(current_dir, must_exist=True, expected_type="file")
        
    # Wrong type (dir expected, file given)
    with pytest.raises(ValueError, match="Expected directory but found file"):
        _validate_path(__file__, must_exist=True, expected_type="dir")
        
    # Empty path
    with pytest.raises(ValueError, match="Path cannot be empty"):
        _validate_path("", must_exist=False)

def test_tool_edge_cases(mcp_server, tmp_path):
    """Test tools with edge case inputs."""
    
    # Empty directory
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    res = mcp_server._analyze_folder_logic(str(empty_dir))
    assert "message" in res
    assert "No images found" in res["message"]
    
    # Directory with non-image files
    txt_file = empty_dir / "notes.txt"
    txt_file.write_text("not an image")
    
    res = mcp_server._analyze_folder_logic(str(empty_dir))
    assert "message" in res
    assert "No images found" in res["message"]
    
    # Analyze photo with corrupted file (simulated by non-image content)
    # The analyzer core might throw an exception which server should catch
    bad_img = tmp_path / "bad.jpg"
    bad_img.write_text("corrupted content")
    
    res = mcp_server._analyze_photo_logic(str(bad_img))
    
    # Core analyzer usually returns error in dict or specific failure
    # Server wrapper catches exceptions
    if "error" in res:
        assert True
    else:
        # If it returns a result, metrics should probably indicate failure/low score
        # But for strictly corrupted file that can't be read by cv2/PIL, it should error
        # Let's check if it errored or returned valid structure
        assert "error" in res or res["technicalScore"] == 0
