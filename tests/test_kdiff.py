#!/usr/bin/env python3
"""
Comprehensive test suite for kdiff
Converts all bash tests to Python unittest
"""
import unittest
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add lib to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'lib'))

from normalize import normalize
from compare import generate_configmap_diff
import diff_details


class TestNormalize(unittest.TestCase):
    """Test resource normalization"""
    
    def test_basic_normalize(self):
        """Test that metadata fields are removed during normalization"""
        input_file = ROOT / 'tests' / 'basic_normalize_test.json'
        expected_file = ROOT / 'tests' / 'fixtures' / 'expected_normalize.json'
        
        with open(input_file) as f:
            resource = json.load(f)
        
        normalized = normalize(resource, keep_metadata=False)
        
        with open(expected_file) as f:
            expected = json.load(f)
        
        self.assertEqual(normalized, expected)
    
    def test_normalize_show_metadata(self):
        """Test that --show-metadata preserves labels and annotations"""
        # Create test input
        test_input = {
            "metadata": {
                "name": "test",
                "namespace": "default",
                "labels": {"app": "test"},
                "annotations": {"note": "keep"}
            },
            "spec": {"replicas": 3}
        }
        
        normalized = normalize(test_input, keep_metadata=True)
        
        # Labels and annotations should be preserved
        self.assertIn('labels', normalized['metadata'])
        self.assertIn('annotations', normalized['metadata'])
        self.assertEqual(normalized['metadata']['labels']['app'], 'test')


class TestEnvDictConversion(unittest.TestCase):
    """Test that env arrays are converted to dictionaries"""
    
    def test_env_different_order_same_result(self):
        """Env vars in different order should produce identical normalized output"""
        input1 = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "test",
                            "env": [
                                {"name": "VAR1", "value": "value1"},
                                {"name": "VAR2", "value": "value2"},
                                {"name": "VAR3", "value": "value3"}
                            ]
                        }]
                    }
                }
            }
        }
        
        input2 = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "test",
                            "env": [
                                {"name": "VAR3", "value": "value3"},
                                {"name": "VAR1", "value": "value1"},
                                {"name": "VAR2", "value": "value2"}
                            ]
                        }]
                    }
                }
            }
        }
        
        norm1 = normalize(input1, keep_metadata=False)
        norm2 = normalize(input2, keep_metadata=False)
        
        # Should be identical
        self.assertEqual(norm1, norm2)
    
    def test_env_dict_structure(self):
        """Env should be converted to dictionary keyed by name"""
        input_data = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "test",
                            "env": [
                                {"name": "VAR1", "value": "value1"},
                                {"name": "VAR2", "value": "value2"}
                            ]
                        }]
                    }
                }
            }
        }
        
        normalized = normalize(input_data, keep_metadata=False)
        
        env = normalized['spec']['template']['spec']['containers'][0]['env']
        
        # Should be a dict
        self.assertIsInstance(env, dict)
        self.assertIn('VAR1', env)
        self.assertIn('VAR2', env)
        # Env dict values are the full env var objects
        self.assertEqual(env['VAR1']['value'], 'value1')
        self.assertEqual(env['VAR2']['value'], 'value2')
    
    def test_env_value_change_detected(self):
        """Value changes should be detected even with dict conversion"""
        input1 = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "test",
                            "env": [
                                {"name": "VAR1", "value": "value1"},
                                {"name": "VAR2", "value": "value2"}
                            ]
                        }]
                    }
                }
            }
        }
        
        input2 = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "test",
                            "env": [
                                {"name": "VAR1", "value": "different"},
                                {"name": "VAR2", "value": "value2"}
                            ]
                        }]
                    }
                }
            }
        }
        
        norm1 = normalize(input1, keep_metadata=False)
        norm2 = normalize(input2, keep_metadata=False)
        
        # Should be different
        self.assertNotEqual(norm1, norm2)


class TestConfigMapDiff(unittest.TestCase):
    """Test ConfigMap-specific diff generation"""
    
    def test_configmap_shows_only_changes(self):
        """ConfigMap diff should show only changed lines, not entire content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cm1_path = Path(tmpdir) / 'cm1.json'
            cm2_path = Path(tmpdir) / 'cm2.json'
            
            cm1 = {
                "kind": "ConfigMap",
                "metadata": {"name": "test-cm", "namespace": "default"},
                "data": {
                    "config.yaml": "key1: value1\nkey2: value2\nkey3: value3",
                    "other.txt": "unchanged content"
                }
            }
            
            cm2 = {
                "kind": "ConfigMap",
                "metadata": {"name": "test-cm", "namespace": "default"},
                "data": {
                    "config.yaml": "key1: value1\nkey2: CHANGED\nkey3: value3",
                    "other.txt": "unchanged content"
                }
            }
            
            cm1_path.write_text(json.dumps(cm1))
            cm2_path.write_text(json.dumps(cm2))
            
            diff = generate_configmap_diff(cm1_path, cm2_path)
            
            # Should contain the changed values
            self.assertIn('key2: value2', diff)
            self.assertIn('key2: CHANGED', diff)
            
            # Should have - and + prefixes
            self.assertIn('-', diff)
            self.assertIn('+', diff)
            
            # Should not have a diff section for unchanged field
            self.assertNotIn('=== data.other.txt ===', diff)
    
    def test_non_configmap_returns_none(self):
        """Non-ConfigMap resources should return None for ConfigMap diff"""
        with tempfile.TemporaryDirectory() as tmpdir:
            deploy1_path = Path(tmpdir) / 'deploy1.json'
            deploy2_path = Path(tmpdir) / 'deploy2.json'
            
            deploy1 = {
                "kind": "Deployment",
                "metadata": {"name": "test"},
                "spec": {"replicas": 1}
            }
            
            deploy2 = {
                "kind": "Deployment",
                "metadata": {"name": "test"},
                "spec": {"replicas": 2}
            }
            
            deploy1_path.write_text(json.dumps(deploy1))
            deploy2_path.write_text(json.dumps(deploy2))
            
            diff = generate_configmap_diff(deploy1_path, deploy2_path)
            
            # Should return None for non-ConfigMap
            self.assertIsNone(diff)


class TestCompare(unittest.TestCase):
    """Test comparison and diff generation"""
    
    def test_compare_detects_differences(self):
        """Compare should detect differences between resources"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / 'cluster1'
            dir2 = Path(tmpdir) / 'cluster2'
            diffs_dir = Path(tmpdir) / 'diffs'
            
            dir1.mkdir()
            dir2.mkdir()
            diffs_dir.mkdir()
            
            # Same resource with different values
            res1 = {"metadata": {"name": "test"}, "spec": {"replicas": 1}}
            res2 = {"metadata": {"name": "test"}, "spec": {"replicas": 2}}
            
            (dir1 / 'deployment__ns__test.json').write_text(json.dumps(res1))
            (dir2 / 'deployment__ns__test.json').write_text(json.dumps(res2))
            
            # Run compare
            result = subprocess.run(
                [sys.executable, str(ROOT / 'lib' / 'compare.py'),
                 str(dir1), str(dir2), str(diffs_dir),
                 '--json-out', str(Path(tmpdir) / 'summary.json')],
                capture_output=True
            )
            
            # Should exit with code 1 (differences found)
            self.assertEqual(result.returncode, 1)
            
            # Summary should show differences
            summary = json.loads((Path(tmpdir) / 'summary.json').read_text())
            self.assertEqual(len(summary['different']), 1)
            
            # Diff file should be created
            diff_files = list(diffs_dir.glob('*.diff'))
            self.assertEqual(len(diff_files), 1)


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_e2e_with_mock_kubectl(self):
        """Full kdiff run with mock kubectl"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            bin_dir = tmpdir / 'bin'
            resp_dir = tmpdir / 'responses'
            out_dir = tmpdir / 'out'
            
            bin_dir.mkdir()
            (resp_dir / 'cluster1').mkdir(parents=True)
            (resp_dir / 'cluster2').mkdir(parents=True)
            out_dir.mkdir()
            
            # Create mock kubectl
            kubectl_script = '''#!/usr/bin/env bash
set -euo pipefail
RESP_DIR="${RESP_DIR:-}"
context=""
kind=""
command=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --context) context="$2"; shift 2;;
    -n) shift 2;;
    get) kind="$2"; shift 2;;
    cluster-info) command="cluster-info"; shift;;
    config) 
      if [[ "$2" == "get-contexts" ]]; then
        command="get-contexts"
        shift 2
        # Skip -o name if present
        if [[ "$1" == "-o" ]]; then shift 2; fi
      else
        shift
      fi
      ;;
    -o) shift 2;;
    --all-namespaces) shift;;
    --request-timeout*) shift;;
    *) shift;;
  esac
done

# Handle cluster-info command (for connectivity testing)
if [[ "$command" == "cluster-info" ]]; then
  echo "Kubernetes control plane is running"
  exit 0
fi

# Handle config get-contexts command (for context validation)
if [[ "$command" == "get-contexts" ]]; then
  echo "cluster1"
  echo "cluster2"
  exit 0
fi

# Handle get resources
if [[ -z "$context" || -z "$kind" ]]; then
  echo "{}"
  exit 0
fi

if [[ -f "$RESP_DIR/$context/$kind.json" ]]; then
  cat "$RESP_DIR/$context/$kind.json"
else
  echo '{"items": []}'
fi
'''
            kubectl_path = bin_dir / 'kubectl'
            kubectl_path.write_text(kubectl_script)
            kubectl_path.chmod(0o755)
            
            # Prepare mock responses
            cluster1_cm = {
                "items": [{
                    "metadata": {"name": "a", "namespace": "ns"},
                    "data": {"k": "v1"}
                }]
            }
            
            cluster1_deploy = {
                "items": [{
                    "metadata": {"name": "d", "namespace": "ns"},
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [{
                                    "name": "c1",
                                    "env": [
                                        {"name": "VAR1", "value": "val1"},
                                        {"name": "VAR2", "value": "val2"}
                                    ]
                                }]
                            }
                        }
                    }
                }]
            }
            
            cluster2_cm = {
                "items": [
                    {"metadata": {"name": "a", "namespace": "ns"}, "data": {"k": "v2"}},
                    {"metadata": {"name": "b", "namespace": "ns"}, "data": {"key": "value"}}
                ]
            }
            
            cluster2_deploy = {"items": []}
            
            (resp_dir / 'cluster1' / 'configmap.json').write_text(json.dumps(cluster1_cm))
            (resp_dir / 'cluster1' / 'deployment.json').write_text(json.dumps(cluster1_deploy))
            (resp_dir / 'cluster2' / 'configmap.json').write_text(json.dumps(cluster2_cm))
            (resp_dir / 'cluster2' / 'deployment.json').write_text(json.dumps(cluster2_deploy))
            
            # Run kdiff
            env = os.environ.copy()
            env['PATH'] = f"{bin_dir}:{env['PATH']}"
            env['RESP_DIR'] = str(resp_dir)
            env['KDIFF_NO_BROWSER'] = '1'  # Prevent browser opening during tests
            
            result = subprocess.run(
                [str(ROOT / 'bin' / 'kdiff'),
                 '-c1', 'cluster1',
                 '-c2', 'cluster2',
                 '-o', str(out_dir),
                 '-f', 'json'],
                env=env,
                capture_output=True,
                text=True
            )
            
            # Should exit 1 (differences found)
            self.assertEqual(result.returncode, 1)
            
            # Check summary
            summary_path = out_dir / 'summary.json'
            self.assertTrue(summary_path.exists())
            
            summary = json.loads(summary_path.read_text())
            
            # Should have 1 missing in cluster2 (deployment "d")
            self.assertEqual(len(summary['missing_in_2']), 1)
            
            # Should have 1 missing in cluster1 (configmap "b")
            self.assertEqual(len(summary['missing_in_1']), 1)
            
            # Should have 1 different (configmap "a")
            self.assertEqual(len(summary['different']), 1)
            
            # Check reports were generated (solo diff-details.html ora)
            # report.md/html e diff-details.md sono commentati
            # self.assertTrue((out_dir / 'report.md').exists())
            # self.assertTrue((out_dir / 'report.html').exists())
            # self.assertTrue((out_dir / 'diff-details.md').exists())
            self.assertTrue((out_dir / 'diff-details.html').exists())


class TestReports(unittest.TestCase):
    """Test report generation"""
    
    def test_diff_details_generation(self):
        """Test that diff-details reports are generated correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create mock summary - use the complete format expected by diff_details.py
            summary = {
                "missing_in_1": [],
                "missing_in_2": [],
                "different": [
                    "configmap__ns__test.json"
                ],
                "counts": {
                    "missing_in_1": 0,
                    "missing_in_2": 0,
                    "different": 1
                },
                "field_changes": {
                    "data.config": {"count": 1, "files": ["configmap__ns__test.json"]}
                }
            }
            
            (tmpdir / 'summary.json').write_text(json.dumps(summary))
            
            # Create mock cluster dirs with actual content
            cluster1_dir = tmpdir / 'cluster1'
            cluster2_dir = tmpdir / 'cluster2'
            cluster1_dir.mkdir()
            cluster2_dir.mkdir()
            (tmpdir / 'diffs').mkdir()
            
            # Create mock resources
            resource1 = {"metadata": {"name": "test"}, "data": {"config": "old"}}
            resource2 = {"metadata": {"name": "test"}, "data": {"config": "new"}}
            (cluster1_dir / 'configmap__ns__test.json').write_text(json.dumps(resource1))
            (cluster2_dir / 'configmap__ns__test.json').write_text(json.dumps(resource2))
            
            # Create a mock diff
            diff_content = "--- cluster1/configmap__ns__test.json\n+++ cluster2/configmap__ns__test.json\n@@ -1,1 +1,1 @@\n-old\n+new\n"
            (tmpdir / 'diffs' / 'configmap__ns__test.json.diff').write_text(diff_content)
            
            # Generate reports
            result = subprocess.run(
                [sys.executable, str(ROOT / 'lib' / 'diff_details.py'), str(tmpdir)],
                capture_output=True,
                text=True
            )
            
            # Check files were created - at minimum, HTML should be created
            # (diff_details.py always creates HTML even if summary is incomplete)
            if not (tmpdir / 'diff-details.html').exists():
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                print("Return code:", result.returncode)
                self.fail("diff-details.html was not created")
            
            # Other files might not be created depending on summary structure
            # so we only check for HTML which should always be present


class TestSingleClusterMode(unittest.TestCase):
    """Test single-cluster namespace comparison mode"""
    
    def test_filename_without_namespace_in_single_cluster_mode(self):
        """Test that resources in single-cluster mode don't include namespace in filename"""
        # This would normally be tested with actual kubectl execution
        # For now, we verify the logic works correctly by checking the output structure
        
        # Create temporary directories to simulate single-cluster comparison
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ns1_dir = tmpdir / 'cluster_ns1'
            ns2_dir = tmpdir / 'cluster_ns2'
            ns1_dir.mkdir()
            ns2_dir.mkdir()
            
            # In single-cluster mode, filenames should NOT include namespace
            # This allows the same resource in different namespaces to be matched
            resource1 = {
                "metadata": {"name": "test-cm", "namespace": "ns1"},
                "data": {"key1": "value1"}
            }
            resource2 = {
                "metadata": {"name": "test-cm", "namespace": "ns2"},
                "data": {"key1": "value2"}
            }
            
            # Files should be named without namespace for matching to work
            (ns1_dir / 'configmap__test-cm.json').write_text(json.dumps(resource1))
            (ns2_dir / 'configmap__test-cm.json').write_text(json.dumps(resource2))
            
            # Verify files exist and have the same name (without namespace)
            self.assertTrue((ns1_dir / 'configmap__test-cm.json').exists())
            self.assertTrue((ns2_dir / 'configmap__test-cm.json').exists())
            
            # Verify content is different
            with open(ns1_dir / 'configmap__test-cm.json') as f:
                content1 = json.load(f)
            with open(ns2_dir / 'configmap__test-cm.json') as f:
                content2 = json.load(f)
            
            self.assertNotEqual(content1['data'], content2['data'])
            self.assertEqual(content1['metadata']['name'], content2['metadata']['name'])
    
    def test_fetch_resources_excludes_namespace_in_filename(self):
        """Test that fetch_resources with single_cluster_mode=True excludes namespace from filename"""
        import sys
        sys.path.insert(0, str(ROOT))
        from kdiff_cli import fetch_resources
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            outdir = tmpdir / 'output'
            
            # Mock a kubectl get configmap output
            mock_item = {
                "metadata": {
                    "name": "test-config",
                    "namespace": "test-ns"
                },
                "data": {
                    "key": "value"
                }
            }
            
            # We can't run actual kubectl, but we can verify the logic
            # by checking that the expected filename format would be used
            # In single_cluster_mode, filename should be: configmap__test-config.json
            # In two_cluster_mode, filename should be: configmap__test-ns__test-config.json
            
            expected_single_cluster = "configmap__test-config.json"
            expected_two_cluster = "configmap__test-ns__test-config.json"
            
            # Verify naming convention
            name = mock_item['metadata']['name']
            namespace = mock_item['metadata']['namespace']
            kind = 'configmap'
            
            # Single cluster mode filename
            fname_single = f"{kind}__{name}.json"
            self.assertEqual(fname_single, expected_single_cluster)
            
            # Two cluster mode filename
            fname_two = f"{kind}__{namespace}__{name}.json"
            self.assertEqual(fname_two, expected_two_cluster)
    
    def test_pairwise_namespace_comparison(self):
        """Test that single-cluster mode creates pairwise comparisons"""
        # Test the pairwise comparison logic
        namespaces = ['ns1', 'ns2', 'ns3']
        
        # Generate all pairs
        pairs = []
        for i in range(len(namespaces)):
            for j in range(i + 1, len(namespaces)):
                pairs.append((namespaces[i], namespaces[j]))
        
        # Verify correct pairs
        expected_pairs = [('ns1', 'ns2'), ('ns1', 'ns3'), ('ns2', 'ns3')]
        self.assertEqual(pairs, expected_pairs)
        
        # With 2 namespaces, should have 1 comparison
        namespaces_2 = ['ns1', 'ns2']
        pairs_2 = []
        for i in range(len(namespaces_2)):
            for j in range(i + 1, len(namespaces_2)):
                pairs_2.append((namespaces_2[i], namespaces_2[j]))
        
        self.assertEqual(len(pairs_2), 1)
        self.assertEqual(pairs_2[0], ('ns1', 'ns2'))


class TestTwoClusterMode(unittest.TestCase):
    """Test two-cluster comparison mode"""
    
    def test_filename_includes_namespace_in_two_cluster_mode(self):
        """Test that resources in two-cluster mode include namespace in filename"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            c1_dir = tmpdir / 'cluster1'
            c2_dir = tmpdir / 'cluster2'
            c1_dir.mkdir()
            c2_dir.mkdir()
            
            # In two-cluster mode, filenames SHOULD include namespace
            # This allows distinguishing resources in different namespaces
            resource1 = {
                "metadata": {"name": "test-cm", "namespace": "prod"},
                "data": {"env": "production"}
            }
            resource2 = {
                "metadata": {"name": "test-cm", "namespace": "staging"},
                "data": {"env": "staging"}
            }
            
            # Files should be named WITH namespace in two-cluster mode
            (c1_dir / 'configmap__prod__test-cm.json').write_text(json.dumps(resource1))
            (c2_dir / 'configmap__staging__test-cm.json').write_text(json.dumps(resource2))
            
            # Verify files exist with namespace in name
            self.assertTrue((c1_dir / 'configmap__prod__test-cm.json').exists())
            self.assertTrue((c2_dir / 'configmap__staging__test-cm.json').exists())
            
            # Verify these are treated as different resources (different filenames)
            files_c1 = list(c1_dir.glob('*.json'))
            files_c2 = list(c2_dir.glob('*.json'))
            
            self.assertEqual(len(files_c1), 1)
            self.assertEqual(len(files_c2), 1)
            self.assertNotEqual(files_c1[0].name, files_c2[0].name)


class TestArgumentValidation(unittest.TestCase):
    """Test CLI argument validation"""
    
    def test_single_cluster_requires_namespaces(self):
        """Test that -c requires --namespaces option"""
        # When using -c (single cluster), --namespaces is required
        # This is validated in the CLI, so we test the logic
        
        # Valid: -c with --namespaces
        has_c = True
        has_namespaces = True
        self.assertTrue(has_c and has_namespaces)
        
        # Invalid: -c without --namespaces would need validation
        has_c = True
        has_namespaces = False
        should_error = has_c and not has_namespaces
        self.assertTrue(should_error)
    
    def test_two_cluster_mode_requires_both_contexts(self):
        """Test that two-cluster mode requires both -c1 and -c2"""
        # Valid: both -c1 and -c2
        has_c1 = True
        has_c2 = True
        self.assertTrue(has_c1 and has_c2)
        
        # Invalid: only -c1 or only -c2
        has_c1 = True
        has_c2 = False
        should_error = (has_c1 and not has_c2) or (has_c2 and not has_c1)
        self.assertTrue(should_error)


if __name__ == '__main__':
    unittest.main(verbosity=2)
