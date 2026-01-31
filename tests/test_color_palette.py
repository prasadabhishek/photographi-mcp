"""
Unit tests for color palette extraction with RAW file support.
Tests the fix for the bug where RAW files returned empty palettes.
"""
import unittest
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../photo-quality-analyzer')))

from photo_quality_analyzer_core.analyzer import extract_palette


class TestColorPalette(unittest.TestCase):
    """Test color palette extraction with various image formats."""
    
    def setUp(self):
        """Set up test image path."""
        self.test_arw = 'local_test_assets/DSC00504.ARW'
        self.test_jpg = 'local_test_assets/DSC00504.JPG'
    
    def test_palette_raw_file(self):
        """Color palette should work with RAW files."""
        if not os.path.exists(self.test_arw):
            self.skipTest(f"Test image not found: {self.test_arw}")
        
        palette = extract_palette(self.test_arw, 5)
        
        # Should return 5 hex colors
        self.assertEqual(len(palette), 5, f"Expected 5 colors, got {len(palette)}")
        self.assertNotEqual(palette, [], "Palette should not be empty for RAW files")
        
        # Each should be a valid hex color
        for color in palette:
            self.assertTrue(color.startswith('#'), f"Color {color} should start with #")
            self.assertEqual(len(color), 7, f"Color {color} should be 7 characters (#RRGGBB)")
    
    def test_palette_jpg_file(self):
        """Color palette should still work with regular JPEGs."""
        if not os.path.exists(self.test_jpg):
            self.skipTest(f"Test image not found: {self.test_jpg}")
        
        palette = extract_palette(self.test_jpg, 7)
        
        self.assertEqual(len(palette), 7, f"Expected 7 colors, got {len(palette)}")
        self.assertNotEqual(palette, [], "Palette should not be empty for JPEG files")
    
    def test_palette_nonexistent_file(self):
        """Non-existent files should return empty palette gracefully."""
        palette = extract_palette('/path/to/nonexistent/file.arw', 5)
        
        self.assertEqual(palette, [], "Non-existent files should return empty list")
    
    def test_palette_custom_count(self):
        """Should respect custom color count parameter."""
        if not os.path.exists(self.test_arw):
            self.skipTest(f"Test image not found: {self.test_arw}")
        
        palette_3 = extract_palette(self.test_arw, 3)
        palette_10 = extract_palette(self.test_arw, 10)
        
        self.assertEqual(len(palette_3), 3, "Should return 3 colors")
        self.assertEqual(len(palette_10), 10, "Should return 10 colors")


if __name__ == '__main__':
    unittest.main()
