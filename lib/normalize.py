#!/usr/bin/env python3
"""
normalize.py - Kubernetes resource normalization for stable comparison

This module removes dynamic and volatile fields from Kubernetes resources
to allow deterministic comparison between different clusters.

Removed fields:
- metadata.managedFields: automatically managed by K8s
- metadata.creationTimestamp: varies between deployments
- metadata.resourceVersion: K8s internal
- metadata.uid: unique per resource
- metadata.selfLink: deprecated in K8s 1.20+
- metadata.generation: increments on each modification
- metadata.labels: unnecessary noise (optional with --show-metadata)
- metadata.annotations: often empty or full of internal metadata (optional with --show-metadata)
  EXCEPTION: for Ingress, nginx.ingress.kubernetes.io/* annotations are kept
- status: runtime state, not part of desired configuration
- spec.template.metadata: same fields for pod templates
- spec.jobTemplate.spec.template.metadata: same fields for CronJobs
- spec.clusterIP / spec.clusterIPs: for Services, varies between environments (normal)

Special conversions:
- env arrays → dict: converts environment variable arrays to dictionary
  key=name to avoid false positives due to reordering

Usage: cat obj.json | python3 lib/normalize.py
Or: python3 lib/normalize.py < obj.json
"""
import sys
import json


def normalize(obj: dict, keep_metadata: bool = False) -> dict:
    """
    Normalize a Kubernetes object by removing volatile fields.
    
    Args:
        obj: Dictionary representing a Kubernetes resource
        keep_metadata: If False (default), removes empty labels and annotations
                      If True, preserves labels and annotations (except last-applied)
    
    Returns:
        Normalized dictionary ready for comparison
    
    Behavior:
        - Always removes dynamic fields (uid, resourceVersion, etc)
        - Always removes status (runtime state)
        - Always removes clusterIP/clusterIPs from Services (vary between environments)
        - If keep_metadata=False: 
          * removes labels to reduce noise
          * removes annotations EXCEPT for Ingress where it keeps nginx.ingress.kubernetes.io/*
        - If keep_metadata=True: keeps labels and annotations (useful for debugging)
        - Always converts env arrays to dict for non-positional comparison
    """
    m = obj.get('metadata', {})
    
    # Remove dynamic fields (always removed)
    if 'managedFields' in m:
        m.pop('managedFields', None)
    for k in ('creationTimestamp', 'resourceVersion', 'uid', 'selfLink', 'generation'):
        m.pop(k, None)

    # Labels: remove if not explicitly requested
    if not keep_metadata:
        m.pop('labels', None)

    # Annotations: remove if not explicitly requested
    # EXCEPTION: for Ingress, keep nginx.ingress.kubernetes.io/* annotations
    if not keep_metadata:
        if obj.get('kind') == 'Ingress':
            # For Ingress: keep only nginx annotations, remove others
            if 'annotations' in m and isinstance(m['annotations'], dict):
                # Filter keeping only nginx annotations and removing last-applied
                # Use exact prefix match to prevent URL sanitization bypass
                allowed_prefix = 'nginx.ingress.kubernetes.io/'
                nginx_annotations = {
                    k: v for k, v in m['annotations'].items()
                    if k.startswith(allowed_prefix) and 
                       len(k) > len(allowed_prefix) and
                       k != 'kubectl.kubernetes.io/last-applied-configuration'
                }
                if nginx_annotations:
                    m['annotations'] = nginx_annotations
                else:
                    m.pop('annotations', None)
        else:
            # For other resources: remove all annotations
            m.pop('annotations', None)
    else:
        try:
            if 'annotations' in m and isinstance(m['annotations'], dict):
                m['annotations'].pop('kubectl.kubernetes.io/last-applied-configuration', None)
                if not m['annotations']:
                    m.pop('annotations', None)
        except Exception:
            pass

    # spec.template.metadata: remove annotations and labels
    if not keep_metadata:
        try:
            if 'spec' in obj and 'template' in obj['spec']:
                tm = obj['spec']['template'].get('metadata', {})
                tm.pop('annotations', None)
                tm.pop('labels', None)
                if tm:
                    obj['spec']['template']['metadata'] = tm
                elif 'metadata' in obj['spec']['template']:
                    obj['spec']['template'].pop('metadata', None)
        except Exception:
            pass

    # spec.jobTemplate.spec.template.metadata for CronJob
    if not keep_metadata:
        try:
            if 'spec' in obj and 'jobTemplate' in obj['spec']:
                if 'spec' in obj['spec']['jobTemplate'] and 'template' in obj['spec']['jobTemplate']['spec']:
                    tm = obj['spec']['jobTemplate']['spec']['template'].get('metadata', {})
                    tm.pop('annotations', None)
                    tm.pop('labels', None)
                    if tm:
                        obj['spec']['jobTemplate']['spec']['template']['metadata'] = tm
                    elif 'metadata' in obj['spec']['jobTemplate']['spec']['template']:
                        obj['spec']['jobTemplate']['spec']['template'].pop('metadata', None)
        except Exception:
            pass

    # Convert env arrays to key=name dictionaries
    try:
        if 'spec' in obj and 'template' in obj['spec']:
            template_spec = obj['spec']['template'].get('spec', {})
            for container in template_spec.get('containers', []):
                if 'env' in container and isinstance(container['env'], list):
                    env_dict = {}
                    for env_var in container['env']:
                        if 'name' in env_var:
                            env_copy = {k: v for k, v in env_var.items() if k != 'name'}
                            env_dict[env_var['name']] = env_copy
                    container['env'] = env_dict
            for container in template_spec.get('initContainers', []):
                if 'env' in container and isinstance(container['env'], list):
                    env_dict = {}
                    for env_var in container['env']:
                        if 'name' in env_var:
                            env_copy = {k: v for k, v in env_var.items() if k != 'name'}
                            env_dict[env_var['name']] = env_copy
                    container['env'] = env_dict
    except Exception:
        pass

    # Converti env arrays per CronJob
    try:
        if 'spec' in obj and 'jobTemplate' in obj['spec']:
            if 'spec' in obj['spec']['jobTemplate'] and 'template' in obj['spec']['jobTemplate']['spec']:
                template_spec = obj['spec']['jobTemplate']['spec']['template'].get('spec', {})
                for container in template_spec.get('containers', []):
                    if 'env' in container and isinstance(container['env'], list):
                        env_dict = {}
                        for env_var in container['env']:
                            if 'name' in env_var:
                                env_copy = {k: v for k, v in env_var.items() if k != 'name'}
                                env_dict[env_var['name']] = env_copy
                        container['env'] = env_dict
                for container in template_spec.get('initContainers', []):
                    if 'env' in container and isinstance(container['env'], list):
                        env_dict = {}
                        for env_var in container['env']:
                            if 'name' in env_var:
                                env_copy = {k: v for k, v in env_var.items() if k != 'name'}
                                env_dict[env_var['name']] = env_copy
                        container['env'] = env_dict
    except Exception:
        pass

    # ========================================
    # Remove clusterIP/clusterIPs from Services
    # ========================================
    # Cluster IPs vary between environments (PROD vs QA vs DEV)
    # and don't represent a real configuration difference
    try:
        if obj.get('kind') == 'Service' and 'spec' in obj:
            obj['spec'].pop('clusterIP', None)
            obj['spec'].pop('clusterIPs', None)
    except Exception:
        pass

    # Remove status
    obj.pop('status', None)
    obj['metadata'] = m
    return obj


def main():
    """Entry point for command-line usage."""
    import argparse
    parser = argparse.ArgumentParser(description='Normalize Kubernetes resources')
    parser.add_argument('--show-metadata', action='store_true',
                       help='Keep labels and annotations')
    args = parser.parse_args()

    raw = sys.stdin.read()
    obj = json.loads(raw)
    normalized = normalize(obj, keep_metadata=args.show_metadata)
    print(json.dumps(normalized, sort_keys=True, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
