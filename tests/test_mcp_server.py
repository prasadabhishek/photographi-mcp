"""
Unit tests for the Photographi MCP server.
Tests the integration between server.py and the photo-quality-analyzer-core.
"""
import unittest
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../photo-quality-analyzer')))

from photo_quality_analyzer_core.analyzer import evaluate_photo_quality
import server


class TestAnalyzerJudgementGeneration(unittest.TestCase):
    """Test that the analyzer properly generates judgements and descriptions."""
    
    def test_judgement_description_exists(self):
        """Verify that judgementDescription field is returned by the analyzer."""
        # Use actual test assets from local_test_assets
        test_image = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            'assets/DSC00504.ARW'
        ))
        if not os.path.exists(test_image):
            self.skipTest(f"Test image not found: {test_image}")
        
        result = evaluate_photo_quality(test_image, enable_subject_detection=False, model_size='nano')
        
        # Verify the key fields exist
        self.assertIn('judgement', result)
        self.assertIn('judgementDescription', result)
        self.assertIn('overallConfidence', result)
        
        # Verify judgementDescription is not empty
        self.assertIsInstance(result['judgementDescription'], str)
        self.assertGreater(len(result['judgementDescription']), 0)
        
    def test_judgement_levels(self):
        """Verify that judgement levels match confidence scores correctly."""
        test_image = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            'assets/DSC00504.ARW'
        ))
        if not os.path.exists(test_image):
            self.skipTest(f"Test image not found: {test_image}")
        
        result = evaluate_photo_quality(test_image, enable_subject_detection=False, model_size='nano')
        
        confidence = result['overallConfidence']
        judgement = result['judgement']
        
        # Verify judgement matches confidence thresholds
        if confidence >= 0.8:
            self.assertEqual(judgement, 'Excellent')
        elif confidence >= 0.65:
            self.assertEqual(judgement, 'Good')
        elif confidence >= 0.5:
            self.assertEqual(judgement, 'Acceptable')
        elif confidence >= 0.35:
            self.assertEqual(judgement, 'Poor')
        else:
            self.assertEqual(judgement, 'Very Poor')


class TestMCPServerRanking(unittest.TestCase):
    """Test that the MCP server ranking function includes proper summaries."""
    
    def test_rank_includes_summaries(self):
        """Verify that rank results include detailed summaries."""
        test_folder = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            'assets'
        ))
        if not os.path.exists(test_folder):
            self.skipTest(f"Test folder not found: {test_folder}")
        
        result = server._rank_folder_logic(test_folder, top_n=5, enable_subject_detection=False, model_size='nano')
        
        # Verify structure
        self.assertEqual(result['status'], 'Ranking Complete')
        self.assertIn('bestImages', result)
        self.assertIn('processed', result)
        
        # Verify each ranked image has a summary
        for image in result['bestImages']:
            self.assertIn('filename', image)
            self.assertIn('score', image)
            self.assertIn('judgement', image)
            self.assertIn('summary', image)
            
            # Verify summary is not empty - THIS IS THE KEY TEST
            self.assertIsInstance(image['summary'], str)
            self.assertGreater(len(image['summary']), 0, 
                             f"Summary for {image['filename']} should not be empty")
    
    def test_rank_sorting(self):
        """Verify that images are ranked from best to worst by score."""
        test_folder = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            'assets'
        ))
        if not os.path.exists(test_folder):
            self.skipTest(f"Test folder not found: {test_folder}")
        
        result = server._rank_folder_logic(test_folder, top_n=10, enable_subject_detection=False, model_size='nano')
        
        if len(result['bestImages']) > 1:
            scores = [img['score'] for img in result['bestImages']]
            # Verify scores are in descending order
            self.assertEqual(scores, sorted(scores, reverse=True))


class TestMCPServerAnalysis(unittest.TestCase):
    """Test individual photo analysis through the MCP server."""
    
    def test_analyze_returns_complete_data(self):
        """Verify that analyze_photo returns all expected fields."""
        test_image = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            'assets/DSC00504.ARW'
        ))
        if not os.path.exists(test_image):
            self.skipTest(f"Test image not found: {test_image}")
        
        result = server._analyze_photo_logic(test_image, enable_subject_detection=False, model_size='nano')
        
        # Verify no error
        self.assertNotIn('error', result)
        
        # Verify essential fields
        self.assertIn('judgement', result)
        self.assertIn('judgementDescription', result)
        self.assertIn('overallConfidence', result)
        self.assertIn('technicalScore', result)
        self.assertIn('aestheticScore', result)
        self.assertIn('metrics', result)


if __name__ == '__main__':
    unittest.main()
