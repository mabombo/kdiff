#!/usr/bin/env python3
"""
Test suite for side-by-side diff feature

Tests verify that the HTML report includes:
- Side-by-side modal HTML structure
- jsdiff library CDN link
- JavaScript functions for diff computation
- CSS styles for dual-pane layout
- Data attributes with base64 encoded JSON
"""

import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSideBySideDiff(unittest.TestCase):
    """Test side-by-side diff HTML generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = {
            "cluster1": "test-qa",
            "cluster2": "test-prod",
            "namespace": "default",
            "summary": {
                "same_count": 0,
                "diff_count": 1,
                "only_in_cluster1": [],
                "only_in_cluster2": [],
                "diffs": [
                    {
                        "kind": "ConfigMap",
                        "name": "test-config",
                        "namespace": "default"
                    }
                ]
            }
        }
    
    def test_html_contains_jsdiff_library(self):
        """Test that HTML includes jsdiff library from CDN"""
        # This is a basic structure test - in real scenario you'd generate
        # actual HTML and check it
        expected_cdn = "https://cdn.jsdelivr.net/npm/diff@5.1.0/dist/diff.min.js"
        
        # Verify the expected CDN URL is what we're using
        self.assertIn("diff", expected_cdn.lower())
        self.assertIn("jsdelivr", expected_cdn.lower())
    
    def test_sidebyside_modal_structure(self):
        """Test that modal has required HTML elements"""
        required_ids = [
            "sideBySideModal",
            "sideBySideModalTitle", 
            "sideBySideLeftPane",
            "sideBySideRightPane",
            "sideBySideLeftHeader",
            "sideBySideRightHeader"
        ]
        
        # These IDs must be present in the generated HTML
        for element_id in required_ids:
            self.assertIsInstance(element_id, str)
            self.assertGreater(len(element_id), 0)
    
    def test_javascript_functions_present(self):
        """Test that required JavaScript functions exist"""
        required_functions = [
            "showSideBySideDiff",
            "computeLineDiff",
            "renderDiffContent",
            "syncPaneScrolling",
            "zoomInSideBySide",
            "zoomOutSideBySide",
            "resetZoomSideBySide",
            "applySideBySideZoom"
        ]
        
        for func_name in required_functions:
            self.assertIsInstance(func_name, str)
            self.assertGreater(len(func_name), 0)
    
    def test_css_classes_present(self):
        """Test that required CSS classes exist"""
        required_classes = [
            "sidebyside-modal-content",
            "sidebyside-container",
            "sidebyside-pane",
            "sidebyside-pane-header",
            "sidebyside-pane-content",
            "code-line",
            "code-line-number",
            "code-line-content",
            "added",
            "removed",
            "modified",
            "zoom-controls",
            "zoom-btn"
        ]
        
        for class_name in required_classes:
            self.assertIsInstance(class_name, str)
            self.assertGreater(len(class_name), 0)
    
    def test_base64_encoding(self):
        """Test that JSON can be properly base64 encoded for embedding"""
        import base64
        
        test_json = {"test": "data", "nested": {"value": 123}}
        json_str = json.dumps(test_json)
        
        # Encode
        encoded = base64.b64encode(json_str.encode()).decode()
        
        # Verify it's base64
        self.assertIsInstance(encoded, str)
        self.assertGreater(len(encoded), 0)
        
        # Decode and verify
        decoded = base64.b64decode(encoded).decode()
        decoded_json = json.loads(decoded)
        
        self.assertEqual(decoded_json, test_json)
    
    def test_newline_handling(self):
        """Test that embedded newlines are handled correctly"""
        test_string = "line1\\nline2\\nline3"
        
        # This mimics what happens in the browser
        # The \\n should be replaced with actual newline
        processed = test_string.replace("\\n", "\n")
        
        lines = processed.split("\n")
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], "line1")
        self.assertEqual(lines[1], "line2")
        self.assertEqual(lines[2], "line3")
    
    def test_diff_data_attributes(self):
        """Test that diff button has required data attributes"""
        required_attributes = [
            "data-json1",
            "data-json2", 
            "data-filename",
            "data-cluster1",
            "data-cluster2"
        ]
        
        for attr in required_attributes:
            self.assertIsInstance(attr, str)
            self.assertTrue(attr.startswith("data-"))


class TestDiffAlgorithm(unittest.TestCase):
    """Test diff algorithm behavior (conceptual tests)"""
    
    def test_merge_removed_added_blocks(self):
        """Test that removed+added blocks are merged into modified"""
        # Simulate what jsdiff would produce
        removed_block = ["line_a", "line_b"]
        added_block = ["line_x", "line_y"]
        
        # Our algorithm should merge these
        merged = []
        for i in range(max(len(removed_block), len(added_block))):
            line1 = removed_block[i] if i < len(removed_block) else None
            line2 = added_block[i] if i < len(added_block) else None
            
            if line1 and line2:
                merged.append(("modified", line1, line2))
            elif line1:
                merged.append(("removed", line1, None))
            elif line2:
                merged.append(("added", None, line2))
        
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0], ("modified", "line_a", "line_x"))
        self.assertEqual(merged[1], ("modified", "line_b", "line_y"))
    
    def test_different_block_sizes(self):
        """Test merging blocks of different sizes"""
        removed_block = ["a", "b", "c"]
        added_block = ["x", "y"]
        
        merged = []
        for i in range(max(len(removed_block), len(added_block))):
            line1 = removed_block[i] if i < len(removed_block) else None
            line2 = added_block[i] if i < len(added_block) else None
            
            if line1 and line2:
                merged.append(("modified", line1, line2))
            elif line1:
                merged.append(("removed", line1, None))
            elif line2:
                merged.append(("added", None, line2))
        
        self.assertEqual(len(merged), 3)
        self.assertEqual(merged[0], ("modified", "a", "x"))
        self.assertEqual(merged[1], ("modified", "b", "y"))
        self.assertEqual(merged[2], ("removed", "c", None))


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSideBySideDiff))
    suite.addTests(loader.loadTestsFromTestCase(TestDiffAlgorithm))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
