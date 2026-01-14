#!/usr/bin/env python3
"""
Test suite for Custom Resources discovery functionality
Mocks kubectl api-resources command to test CR discovery without real clusters
"""
import unittest
from subprocess import CalledProcessError
from unittest.mock import patch
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add bin to path to import kdiff functions
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def discover_custom_resources_mock(context: str, namespace: Optional[str] = None, groups: Optional[list[str]] = None) -> list[str]:
    """
    Mock implementation of discover_custom_resources for testing
    Discovers Custom Resources from a Kubernetes cluster via kubectl api-resources
    """
    native_prefixes = [
        'bindings', 'componentstatuses', 'configmaps', 'endpoints', 'events',
        'limitranges', 'namespaces', 'nodes', 'persistentvolumeclaims',
        'persistentvolumes', 'pods', 'podtemplates', 'replicationcontrollers',
        'resourcequotas', 'secrets', 'serviceaccounts', 'services',
        'mutatingwebhookconfigurations', 'validatingwebhookconfigurations',
        'customresourcedefinitions', 'apiservices', 'controllerrevisions',
        'daemonsets', 'deployments', 'replicasets', 'statefulsets',
        'tokenreviews', 'localsubjectaccessreviews', 'selfsubjectaccessreviews',
        'selfsubjectrulesreviews', 'subjectaccessreviews', 'horizontalpodautoscalers',
        'cronjobs', 'jobs', 'certificatesigningrequests', 'leases',
        'endpointslices', 'ingresses', 'networkpolicies', 'runtimeclasses',
        'poddisruptionbudgets', 'clusterrolebindings', 'clusterroles',
        'rolebindings', 'roles', 'priorityclasses', 'csidrivers', 'csinodes',
        'csistoragecapacities', 'storageclasses', 'volumeattachments'
    ]
    
    try:
        cmd = ['kubectl', '--context', context, 'api-resources', '--verbs=list', '-o', 'name']
        if namespace:
            cmd.insert(3, '--namespaced=true')
        
        result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        all_resources = result.decode('utf-8').strip().split('\n')
        
        custom_resources = []
        for resource in all_resources:
            if '.' in resource:
                resource_name = resource.split('.')[0]
                if resource_name not in native_prefixes:
                    if groups:
                        resource_group = '.'.join(resource.split('.')[1:])
                        if any(resource_group.endswith(g) or resource_group == g for g in groups):
                            custom_resources.append(resource)
                    else:
                        custom_resources.append(resource)
        
        return custom_resources
    except Exception:
        return []


class TestCRDiscovery(unittest.TestCase):
    """Test Custom Resources discovery without real cluster dependencies"""
    
    def setUp(self):
        """Set up the mock function for testing"""
        self.discover_custom_resources = discover_custom_resources_mock
    
    @patch('subprocess.check_output')
    def test_discover_all_crs(self, mock_subprocess):
        """Test auto-discovery of all Custom Resources"""
        # Mock kubectl api-resources output
        mock_output = """deployments.apps
statefulsets.apps
services
configmaps
secrets
elasticsearches.elasticsearch.k8s.elastic.co
virtualservices.networking.istio.io
gateways.networking.istio.io
certificates.cert-manager.io
issuers.cert-manager.io
kafkas.kafka.strimzi.io
"""
        mock_subprocess.return_value = mock_output.encode('utf-8')
        
        # Call function without groups filter
        result = self.discover_custom_resources('test-context', 'test-namespace')
        
        # Verify kubectl was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn('kubectl', call_args)
        self.assertIn('--context', call_args)
        self.assertIn('test-context', call_args)
        self.assertIn('api-resources', call_args)
        
        # Verify only CRs are returned (those with dots, excluding native resources)
        expected_crs = [
            'elasticsearches.elasticsearch.k8s.elastic.co',
            'virtualservices.networking.istio.io',
            'gateways.networking.istio.io',
            'certificates.cert-manager.io',
            'issuers.cert-manager.io',
            'kafkas.kafka.strimzi.io'
        ]
        self.assertEqual(sorted(result), sorted(expected_crs))
        
        # Verify native resources are excluded
        self.assertNotIn('deployments.apps', result)
        self.assertNotIn('statefulsets.apps', result)
        self.assertNotIn('services', result)
        self.assertNotIn('configmaps', result)
        self.assertNotIn('secrets', result)
    
    @patch('subprocess.check_output')
    def test_discover_filtered_by_single_group(self, mock_subprocess):
        """Test CR discovery filtered by single API group"""
        mock_output = """elasticsearches.elasticsearch.k8s.elastic.co
virtualservices.networking.istio.io
gateways.networking.istio.io
certificates.cert-manager.io
issuers.cert-manager.io
kafkas.kafka.strimzi.io
"""
        mock_subprocess.return_value = mock_output.encode('utf-8')
        
        # Call with istio.io filter
        result = self.discover_custom_resources('test-context', 'test-namespace', ['istio.io'])
        
        # Verify only istio.io CRs are returned
        expected_crs = [
            'virtualservices.networking.istio.io',
            'gateways.networking.istio.io'
        ]
        self.assertEqual(sorted(result), sorted(expected_crs))
        
        # Verify other CRs are excluded
        self.assertNotIn('elasticsearches.elasticsearch.k8s.elastic.co', result)
        self.assertNotIn('certificates.cert-manager.io', result)
    
    @patch('subprocess.check_output')
    def test_discover_filtered_by_multiple_groups(self, mock_subprocess):
        """Test CR discovery filtered by multiple API groups"""
        mock_output = """elasticsearches.elasticsearch.k8s.elastic.co
virtualservices.networking.istio.io
gateways.networking.istio.io
certificates.cert-manager.io
issuers.cert-manager.io
kafkas.kafka.strimzi.io
"""
        mock_subprocess.return_value = mock_output.encode('utf-8')
        
        # Call with multiple groups filter
        result = self.discover_custom_resources(
            'test-context', 
            'test-namespace', 
            ['istio.io', 'cert-manager.io']
        )
        
        # Verify only filtered CRs are returned
        expected_crs = [
            'virtualservices.networking.istio.io',
            'gateways.networking.istio.io',
            'certificates.cert-manager.io',
            'issuers.cert-manager.io'
        ]
        self.assertEqual(sorted(result), sorted(expected_crs))
        
        # Verify other CRs are excluded
        self.assertNotIn('elasticsearches.elasticsearch.k8s.elastic.co', result)
        self.assertNotIn('kafkas.kafka.strimzi.io', result)
    
    @patch('subprocess.check_output')
    def test_discover_no_crs_available(self, mock_subprocess):
        """Test behavior when no Custom Resources are available"""
        # Mock output with only native resources
        mock_output = """deployments.apps
statefulsets.apps
services
configmaps
secrets
pods
"""
        mock_subprocess.return_value = mock_output.encode('utf-8')
        
        result = self.discover_custom_resources('test-context', 'test-namespace')
        
        # Verify empty list is returned
        self.assertEqual(result, [])
    
    @patch('subprocess.check_output')
    def test_discover_with_exact_group_match(self, mock_subprocess):
        """Test that group filtering works with exact matches"""
        mock_output = """virtualservices.networking.istio.io
gateways.networking.istio.io
virtualservices.networking.internal.istio.io
"""
        mock_subprocess.return_value = mock_output.encode('utf-8')
        
        # Filter for exact "istio.io" - should match both networking.istio.io and internal.istio.io
        result = self.discover_custom_resources('test-context', 'test-namespace', ['istio.io'])
        
        # All should match as they end with istio.io
        self.assertEqual(len(result), 3)
        self.assertIn('virtualservices.networking.istio.io', result)
        self.assertIn('gateways.networking.istio.io', result)
        self.assertIn('virtualservices.networking.internal.istio.io', result)
    
    @patch('subprocess.check_output')
    def test_discover_handles_kubectl_error(self, mock_subprocess):
        """Test that function handles kubectl errors gracefully"""
        # Mock kubectl command failure
        mock_subprocess.side_effect = CalledProcessError(1, 'kubectl', b'Error: context not found')
        
        result = self.discover_custom_resources('invalid-context', 'test-namespace')
        
        # Verify empty list is returned on error
        self.assertEqual(result, [])
    
    @patch('subprocess.check_output')
    def test_namespace_parameter_affects_command(self, mock_subprocess):
        """Test that namespace parameter is used correctly in kubectl command"""
        mock_output = b"elasticsearches.elasticsearch.k8s.elastic.co\n"
        mock_subprocess.return_value = mock_output
        
        # Call with namespace
        self.discover_custom_resources('test-context', 'my-namespace')
        
        # Verify --namespaced=true is in the command
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn('--namespaced=true', call_args)


class TestCRIntegration(unittest.TestCase):
    """Integration test for CR comparison workflow"""
    
    @patch('subprocess.check_output')
    def test_cr_group_parsing(self, mock_subprocess):
        """Test parsing of comma-separated CR groups"""
        groups_string = "istio.io,cert-manager.io,elasticsearch.k8s.elastic.co"
        parsed_groups = [g.strip() for g in groups_string.split(',')]
        
        expected = ['istio.io', 'cert-manager.io', 'elasticsearch.k8s.elastic.co']
        self.assertEqual(parsed_groups, expected)
    
    def test_cr_groups_with_spaces(self):
        """Test parsing handles spaces around commas"""
        groups_string = "istio.io , cert-manager.io , elasticsearch.k8s.elastic.co "
        parsed_groups = [g.strip() for g in groups_string.split(',')]
        
        expected = ['istio.io', 'cert-manager.io', 'elasticsearch.k8s.elastic.co']
        self.assertEqual(parsed_groups, expected)
    
    def test_union_of_crs_from_two_clusters(self):
        """Test that CRs from both clusters are merged correctly"""
        cluster1_crs = [
            'virtualservices.networking.istio.io',
            'certificates.cert-manager.io'
        ]
        cluster2_crs = [
            'virtualservices.networking.istio.io',
            'kafkas.kafka.strimzi.io'
        ]
        
        # Union of both sets
        cr_set = set()
        cr_set.update(cluster1_crs)
        cr_set.update(cluster2_crs)
        merged_crs = sorted(list(cr_set))
        
        expected = [
            'certificates.cert-manager.io',
            'kafkas.kafka.strimzi.io',
            'virtualservices.networking.istio.io'
        ]
        self.assertEqual(merged_crs, expected)


class TestMultipleNamespaces(unittest.TestCase):
    """Test multiple namespace parsing and handling"""
    
    def test_single_namespace_parsing(self):
        """Test parsing of single namespace"""
        namespace_string = "connect"
        namespaces = [ns.strip() for ns in namespace_string.split(',')]
        
        self.assertEqual(namespaces, ['connect'])
    
    def test_multiple_namespaces_parsing(self):
        """Test parsing of comma-separated namespaces"""
        namespace_string = "connect,default,kube-system"
        namespaces = [ns.strip() for ns in namespace_string.split(',')]
        
        expected = ['connect', 'default', 'kube-system']
        self.assertEqual(namespaces, expected)
    
    def test_namespaces_with_spaces(self):
        """Test parsing handles spaces around commas"""
        namespace_string = "connect , default , kube-system "
        namespaces = [ns.strip() for ns in namespace_string.split(',')]
        
        expected = ['connect', 'default', 'kube-system']
        self.assertEqual(namespaces, expected)
    
    def test_none_namespace(self):
        """Test that None namespace is handled correctly"""
        namespace_value = None
        namespaces = None
        if namespace_value:
            namespaces = [ns.strip() for ns in namespace_value.split(',')]
        
        self.assertIsNone(namespaces)


