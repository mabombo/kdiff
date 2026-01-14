#!/usr/bin/env python3
"""
Test suite for parallel execution features.
Tests multi-threading, worker management, and thread safety.
"""

import unittest
import json
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from threading import Lock
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kdiff_cli import fetch_resources, fetch_single_resource


class TestParallelExecution(unittest.TestCase):
    """Test parallel execution of kubectl calls."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch('kdiff_cli.subprocess.run')
    @patch('kdiff_cli.load_normalize_func')
    def test_parallel_fetch_creates_all_resources(self, mock_normalize, mock_run):
        """Test that parallel fetch creates all expected resource files."""
        # Mock kubectl responses
        def mock_kubectl(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            result.stdout = json.dumps({
                'items': [{
                    'metadata': {
                        'name': 'test-resource',
                        'namespace': 'default'
                    },
                    'spec': {}
                }]
            })
            return result
        
        mock_run.side_effect = mock_kubectl
        mock_normalize.return_value = lambda x, keep_metadata=False: x
        
        resources = ['deployment', 'configmap', 'secret']
        success = fetch_resources('test-context', self.test_dir, resources, 'default', max_workers=3)
        
        self.assertTrue(success)
        # Should have called kubectl for each resource type
        self.assertEqual(mock_run.call_count, 3)
        
    @patch('kdiff_cli.subprocess.run')
    @patch('kdiff_cli.load_normalize_func')
    def test_max_workers_parameter_is_used(self, mock_normalize, mock_run):
        """Test that max_workers parameter controls parallelization."""
        call_times = []
        
        def mock_kubectl_with_delay(*args, **kwargs):
            call_times.append(time.time())
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            result.stdout = json.dumps({'items': []})
            time.sleep(0.1)  # Simulate API call delay
            return result
        
        mock_run.side_effect = mock_kubectl_with_delay
        mock_normalize.return_value = lambda x, keep_metadata=False: x
        
        resources = ['deployment', 'configmap', 'secret', 'service', 'pod']
        start_time = time.time()
        fetch_resources('test-context', self.test_dir, resources, 'default', max_workers=5)
        elapsed = time.time() - start_time
        
        # With 5 resources and max_workers=5, all should run in parallel
        # Total time should be ~0.1s (one batch) not 0.5s (sequential)
        self.assertLess(elapsed, 0.3, "Parallel execution should be faster than sequential")

    @patch('kdiff_cli.subprocess.run')
    @patch('kdiff_cli.load_normalize_func')
    def test_thread_safe_console_output(self, mock_normalize, mock_run):
        """Test that console output is thread-safe with Lock."""
        def mock_kubectl(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            result.stdout = json.dumps({'items': []})
            return result
        
        mock_run.side_effect = mock_kubectl
        mock_normalize.return_value = lambda x, keep_metadata=False: x
        
        with patch('builtins.print') as mock_print:
            resources = ['deployment', 'configmap', 'secret', 'service']
            fetch_resources('test-context', self.test_dir, resources, 'default', max_workers=4)
            
            # Verify print was called (output happened)
            self.assertGreater(mock_print.call_count, 0)

    @patch('kdiff_cli.subprocess.run')
    @patch('kdiff_cli.load_normalize_func')
    def test_error_in_one_thread_does_not_block_others(self, mock_normalize, mock_run):
        """Test that an error in one thread doesn't prevent other threads from completing."""
        call_count = {'success': 0, 'error': 0}
        
        def mock_kubectl(*args, **kwargs):
            cmd = args[0]
            resource_type = cmd[cmd.index('get') + 1]
            
            result = MagicMock()
            if resource_type == 'deployment':
                # Simulate error for deployment
                result.returncode = 1
                result.stderr = "Error: forbidden"
                call_count['error'] += 1
            else:
                # Success for other resources with actual data
                result.returncode = 0
                result.stderr = ""
                result.stdout = json.dumps({
                    'items': [{
                        'metadata': {'name': f'test-{resource_type}', 'namespace': 'default'},
                        'spec': {}
                    }]
                })
                call_count['success'] += 1
            return result
        
        mock_run.side_effect = mock_kubectl
        mock_normalize.return_value = lambda x, keep_metadata=False: x
        
        resources = ['deployment', 'configmap', 'secret']
        with patch('sys.stderr'):
            success = fetch_resources('test-context', self.test_dir, resources, 'default', max_workers=3)
        
        # Should complete with resources retrieved despite one error
        self.assertTrue(success)
        self.assertEqual(call_count['error'], 1)
        self.assertEqual(call_count['success'], 2)
        
        # Verify that files were created for successful resources
        json_files = list(self.test_dir.glob('*.json'))
        self.assertEqual(len(json_files), 2)  # configmap and secret

    @patch('kdiff_cli.subprocess.run')
    @patch('kdiff_cli.load_normalize_func')
    def test_parallel_produces_same_results_as_sequential(self, mock_normalize, mock_run):
        """Test that parallel fetch produces the same files as sequential fetch."""
        def mock_kubectl(*args, **kwargs):
            cmd = args[0]
            resource_type = cmd[cmd.index('get') + 1]
            
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            result.stdout = json.dumps({
                'items': [{
                    'metadata': {
                        'name': f'test-{resource_type}',
                        'namespace': 'default'
                    },
                    'spec': {'data': resource_type}
                }]
            })
            return result
        
        mock_run.side_effect = mock_kubectl
        mock_normalize.return_value = lambda x, keep_metadata=False: x
        
        # Parallel execution
        parallel_dir = self.test_dir / 'parallel'
        resources = ['deployment', 'configmap', 'secret']
        fetch_resources('test-context', parallel_dir, resources, 'default', max_workers=3)
        
        # Sequential execution (max_workers=1)
        sequential_dir = self.test_dir / 'sequential'
        fetch_resources('test-context', sequential_dir, resources, 'default', max_workers=1)
        
        # Compare results
        parallel_files = sorted([f.name for f in parallel_dir.glob('*.json')])
        sequential_files = sorted([f.name for f in sequential_dir.glob('*.json')])
        
        self.assertEqual(parallel_files, sequential_files, 
                        "Parallel and sequential execution should produce same files")

    @patch('kdiff_cli.subprocess.run')
    def test_critical_error_terminates_all_threads(self, mock_run):
        """Test that critical errors (context not found) terminate gracefully."""
        def mock_kubectl(*args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stderr = "Error: context 'invalid-context' does not exist"
            return result
        
        mock_run.side_effect = mock_kubectl
        
        resources = ['deployment', 'configmap', 'secret']
        with self.assertRaises(SystemExit):
            fetch_resources('invalid-context', self.test_dir, resources, 'default', max_workers=3)


class TestFetchSingleResource(unittest.TestCase):
    """Test individual resource fetching function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.print_lock = Lock()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch('kdiff_cli.subprocess.run')
    def test_fetch_single_resource_success(self, mock_run):
        """Test successful single resource fetch."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stderr="",
            stdout=json.dumps({
                'items': [{
                    'metadata': {'name': 'test-deployment', 'namespace': 'default'},
                    'spec': {}
                }]
            })
        )
        
        mock_norm = lambda x, keep_metadata=False: x
        
        success, count, has_errors, error_msg = fetch_single_resource(
            'test-context', 'deployment', 'default', self.test_dir,
            mock_norm, False, False, self.print_lock
        )
        
        self.assertTrue(success)
        self.assertEqual(count, 1)
        self.assertFalse(has_errors)
        self.assertIsNone(error_msg)

    @patch('kdiff_cli.subprocess.run')
    def test_fetch_single_resource_permission_error(self, mock_run):
        """Test handling of permission errors."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Error: Forbidden",
            stdout=""
        )
        
        mock_norm = lambda x, keep_metadata=False: x
        
        with patch('sys.stderr'):
            success, count, has_errors, error_msg = fetch_single_resource(
                'test-context', 'deployment', 'default', self.test_dir,
                mock_norm, False, False, self.print_lock
            )
        
        self.assertTrue(success)  # Non-critical error
        self.assertEqual(count, 0)
        self.assertTrue(has_errors)
        self.assertIsNone(error_msg)  # Non-critical

    @patch('kdiff_cli.subprocess.run')
    def test_fetch_single_resource_context_not_found(self, mock_run):
        """Test handling of critical context errors."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Error: context 'invalid' does not exist",
            stdout=""
        )
        
        mock_norm = lambda x, keep_metadata=False: x
        
        success, count, has_errors, error_msg = fetch_single_resource(
            'invalid-context', 'deployment', 'default', self.test_dir,
            mock_norm, False, False, self.print_lock
        )
        
        self.assertFalse(success)  # Critical error
        self.assertEqual(count, 0)
        self.assertTrue(has_errors)
        self.assertIsNotNone(error_msg)
        self.assertIn("does not exist", error_msg)


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of shared resources."""

    @patch('kdiff_cli.subprocess.run')
    @patch('kdiff_cli.load_normalize_func')
    def test_concurrent_file_writes_are_safe(self, mock_normalize, mock_run):
        """Test that concurrent file writes don't corrupt data."""
        test_dir = Path(tempfile.mkdtemp())
        
        try:
            def mock_kubectl(*args, **kwargs):
                cmd = args[0]
                resource_type = cmd[cmd.index('get') + 1]
                result = MagicMock()
                result.returncode = 0
                result.stderr = ""
                # Create multiple items to test concurrent writes
                result.stdout = json.dumps({
                    'items': [
                        {
                            'metadata': {'name': f'{resource_type}-{i}', 'namespace': 'default'},
                            'spec': {'index': i}
                        }
                        for i in range(5)
                    ]
                })
                return result
            
            mock_run.side_effect = mock_kubectl
            mock_normalize.return_value = lambda x, keep_metadata=False: x
            
            resources = ['deployment', 'configmap', 'secret', 'service', 'pod']
            fetch_resources('test-context', test_dir, resources, 'default', max_workers=5)
            
            # Verify all files were created correctly
            json_files = list(test_dir.glob('*.json'))
            self.assertEqual(len(json_files), 25)  # 5 resources * 5 items each
            
            # Verify each file is valid JSON
            for json_file in json_files:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    self.assertIsInstance(data, dict)
                    
        finally:
            if test_dir.exists():
                shutil.rmtree(test_dir)


if __name__ == '__main__':
    unittest.main()
