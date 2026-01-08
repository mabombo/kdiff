#!/usr/bin/env python3
"""kdiff — compare Kubernetes resources between two clusters
This is the Python replacement for the previous Bash CLI.
Usage: bin/kdiff -c1 CONTEXT1 -c2 CONTEXT2 [options]
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import importlib.util

ROOT = Path(__file__).resolve().parent
LIB = ROOT / 'lib'

# Default resources
RESOURCES = [
    'deployment', 'statefulset', 'daemonset', 'configmap', 'secret',
    'persistentvolumeclaim', 'serviceaccount', 'role', 'rolebinding', 'horizontalpodautoscaler',
    'cronjob', 'job'
]
VOLATILE_RESOURCES = ['replicaset', 'pod']
SERVICE_INGRESS_RESOURCES = ['service', 'ingress']

# All supported resources for reference
ALL_SUPPORTED_RESOURCES = RESOURCES + VOLATILE_RESOURCES + SERVICE_INGRESS_RESOURCES

GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
RED = '\033[0;31m'
RESET = '\033[0m'


def check_deps():
    if not shutil.which('kubectl'):
        print("Error: 'kubectl' not found. Install it and try again.", file=sys.stderr)
        sys.exit(2)


def cleanup_output_dir(outdir: Path):
    """Clean output directory if it already exists."""
    if outdir.exists():
        try:
            shutil.rmtree(outdir)
            print(f"Cleaning existing output directory: {outdir}")
        except Exception as e:
            print(f"Warning: Unable to clean {outdir}: {e}", file=sys.stderr)


def is_running_in_docker() -> bool:
    """Detect if the script is running inside a Docker container."""
    # Check for .dockerenv file (most reliable)
    if os.path.exists('/.dockerenv'):
        return True
    
    # Check cgroup for docker
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read()
    except Exception:
        pass
    
    return False


def open_html_in_browser(html_path: Path) -> bool:
    """Try to open HTML file in the default browser.
    Returns True if successful, False otherwise.
    Skips opening if running in Docker container or if KDIFF_NO_BROWSER env var is set.
    """
    # Skip browser opening in Docker environment or if disabled via env var
    if is_running_in_docker() or os.getenv('KDIFF_NO_BROWSER'):
        return False
    
    # Convert to absolute path
    abs_path = html_path.resolve()
    
    import platform
    try:
        system = platform.system()
        if system == 'Darwin':  # macOS
            subprocess.run(['open', str(abs_path)], check=True)
        elif system == 'Linux':
            subprocess.run(['xdg-open', str(abs_path)], check=True)
        elif system == 'Windows':
            subprocess.run(['start', str(abs_path)], shell=True, check=True)
        else:
            return False
        return True
    except Exception:
        return False


# dynamic import helper to load normalize.normalize
def load_normalize_func():
    spec = importlib.util.spec_from_file_location('normalize', str(LIB / 'normalize.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return getattr(mod, 'normalize')


def fetch_resources(context: str, outdir: Path, resources: list[str], namespaces: list[str] | str | None, show_metadata: bool = False):
    """
    Fetch resources from a Kubernetes cluster.
    
    Args:
        context: Kubernetes context name
        outdir: Output directory for fetched resources
        resources: List of resource types to fetch
        namespaces: None (all namespaces), string (single namespace), or list (specific namespaces)
        show_metadata: Whether to keep metadata in normalized output
    """
    outdir.mkdir(parents=True, exist_ok=True)
    norm = load_normalize_func()
    has_errors = False
    resource_count = 0
    
    # Determine namespace mode
    if namespaces is None:
        ns_list = [None]  # Fetch from all namespaces
        ns_mode = "all"
    elif isinstance(namespaces, str):
        ns_list = [namespaces]  # Single namespace
        ns_mode = "single"
    else:
        ns_list = namespaces  # Multiple specific namespaces
        ns_mode = "multi"

    for kind in resources:
        for ns in ns_list:
            if ns:
                print(f"[{context}/{ns}] Fetching {kind}...")
            else:
                print(f"[{context}] Fetching {kind}...")
                
            cmd = ['kubectl', '--context', context]
            if ns:
                cmd += ['-n', ns, 'get', kind, '-o', 'json']
            else:
                cmd += ['get', kind, '--all-namespaces', '-o', 'json']

            cmd = ['kubectl', '--context', context]
            if ns:
                cmd += ['-n', ns, 'get', kind, '-o', 'json']
            else:
                cmd += ['get', kind, '--all-namespaces', '-o', 'json']

        try:
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                
                # CRITICAL connectivity errors (terminate execution)
                if 'does not exist' in stderr:
                    print(f"\n{RED}[ERROR] CRITICAL ERROR:{RESET} Context '{context}' does not exist in kubeconfig", file=sys.stderr)
                    print(f"{YELLOW}Suggestion:{RESET} Verify with 'kubectl config get-contexts'", file=sys.stderr)
                    sys.exit(2)
                elif 'no such host' in stderr or 'dial tcp' in stderr:
                    print(f"\n{RED}[ERROR] CRITICAL ERROR:{RESET} Unable to connect to cluster '{context}'", file=sys.stderr)
                    print(f"{YELLOW}Possible causes:{RESET}", file=sys.stderr)
                    print(f"  - Cluster unreachable (DNS, network, firewall)", file=sys.stderr)
                    print(f"  - VPN not active", file=sys.stderr)
                    print(f"  - API server unavailable", file=sys.stderr)
                    if 'no such host' in stderr:
                        # Extract hostname from error
                        import re
                        hostname_match = re.search(r'lookup ([^:]+):', stderr)
                        if hostname_match:
                            print(f"  - Unresolvable hostname: {hostname_match.group(1)}", file=sys.stderr)
                    sys.exit(2)
                elif 'timeout' in stderr.lower() or 'timed out' in stderr.lower():
                    print(f"\n{RED}[ERROR] CRITICAL ERROR:{RESET} Connection timeout to cluster '{context}'", file=sys.stderr)
                    print(f"{YELLOW}Suggestion:{RESET} Check network connectivity and that cluster is active", file=sys.stderr)
                    sys.exit(2)
                
                # NON-critical errors (permissions, empty resources, etc)
                elif 'Forbidden' in stderr or 'forbidden' in stderr:
                    ns_info = f" in namespace '{ns}'" if ns else " at cluster level"
                    print(f"[{context}] {RED}[ERROR]{RESET} Insufficient permissions for {kind}{ns_info}.", file=sys.stderr)
                    if not ns:
                        print(f"[{context}] {YELLOW}Suggestion:{RESET} Specify a namespace with -n <namespace> or --namespaces", file=sys.stderr)
                    has_errors = True
                elif stderr:
                    print(f"[{context}] {YELLOW}⚠{RESET}  kubectl error per {kind}: {stderr[:100]}", file=sys.stderr)
                    has_errors = True
                else:
                    print(f"[{context}] {YELLOW}⚠{RESET}  kubectl returned non-zero for {kind} (exit code {proc.returncode})", file=sys.stderr)
                    has_errors = True
                continue
            data = json.loads(proc.stdout) if proc.stdout.strip() else {}
            items = data.get('items', [])
            if not items:
                ns_info = f" in {ns}" if ns else ""
                print(f"[{context}] Nessun oggetto {kind}{ns_info}.")
                continue
            for item in items:
                name = item.get('metadata', {}).get('name')
                item_ns = item.get('metadata', {}).get('namespace')
                if item_ns:
                    fname = f"{kind}__{item_ns}__{name}.json"
                else:
                    fname = f"{kind}__{name}.json"
                path = outdir / fname
                resource_count += 1
                # pass show-metadata flag to the normalizer
                n = norm(item, keep_metadata=bool(show_metadata))
                path.write_text(json.dumps(n, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding='utf-8')
        except Exception as e:
            print(f"[{context}] Errore fetching {kind}: {e}", file=sys.stderr)
            continue
    
    # Final check: if no resources retrieved, it could be a serious problem
    if resource_count == 0 and has_errors:
        print(f"\n{RED}[WARNING]:{RESET} No resources retrieved from '{context}' due to errors.", file=sys.stderr)
        print(f"{YELLOW}Suggestion:{RESET} Resolve errors above before continuing.", file=sys.stderr)
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='kdiff — Compare Kubernetes resources between two clusters or multiple namespaces',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Two-cluster mode: Compare all default resources between two clusters
  kdiff -c1 prod-cluster -c2 staging-cluster

  # Two-cluster mode: Compare specific namespace
  kdiff -c1 prod-cluster -c2 staging-cluster -n my-namespace

  # Two-cluster mode: Compare multiple namespaces
  kdiff -c1 prod-cluster -c2 staging-cluster --namespaces ns1,ns2,ns3

  # Single-cluster mode: Compare multiple namespaces in same cluster
  kdiff -c prod-cluster --namespaces ns1,ns2,ns3

  # Compare only deployments and configmaps
  kdiff -c1 prod-cluster -c2 staging-cluster -r deployment,configmap -n my-namespace

  # Compare all supported resource types (including volatile resources)
  kdiff -c1 prod-cluster -c2 staging-cluster --include-resource-types all

  # Compare with custom output directory
  kdiff -c1 prod-cluster -c2 staging-cluster -o /tmp/my-diff-output

  # Compare and generate only JSON output (skip console report)
  kdiff -c1 prod-cluster -c2 staging-cluster -f json

  # Compare including pods and replicasets (volatile resources)
  kdiff -c1 prod-cluster -c2 staging-cluster --include-volatile

  # Compare keeping metadata labels and annotations
  kdiff -c1 prod-cluster -c2 staging-cluster --show-metadata

  # Compare excluding secrets and configmaps
  kdiff -c1 prod-cluster -c2 staging-cluster --exclude-resources secret,configmap

Default resources compared:
  deployment, statefulset, daemonset, configmap, secret, persistentvolumeclaim,
  serviceaccount, role, rolebinding, horizontalpodautoscaler, cronjob, job
        ''')
    
    parser.add_argument('-c1', 
                       metavar='CONTEXT1',
                       help='First Kubernetes context name (e.g., prod-cluster). Use "kubectl config get-contexts" to see available contexts')
    
    parser.add_argument('-c2', 
                       metavar='CONTEXT2', 
                       help='Second Kubernetes context name to compare against (e.g., staging-cluster)')
    
    parser.add_argument('-c',
                       metavar='CONTEXT',
                       help='Single Kubernetes context for multi-namespace comparison. Requires --namespaces with at least 2 namespaces')
    
    parser.add_argument('-r',
                       metavar='RESOURCES',
                       help='Comma-separated list of resource types to compare (e.g., deployment,configmap,secret). If not specified, compares default resources. See examples below for details')
    
    parser.add_argument('-n',
                       metavar='NAMESPACE',
                       help='Kubernetes namespace to filter resources (single namespace). If not specified, compares resources across all namespaces (--all-namespaces)')
    
    parser.add_argument('--namespaces',
                       metavar='NS1,NS2,...',
                       help='Comma-separated list of namespaces to compare. Use with -c for single-cluster mode or with -c1/-c2 for two-cluster mode')
    
    parser.add_argument('-o',
                       metavar='OUTPUT_DIR',
                       help='Output directory for comparison results (default: ./kdiff_output/latest). Directory will be cleaned if it already exists')
    
    parser.add_argument('-f', '--format',
                       dest='format',
                       default='text',
                       metavar='FORMAT',
                       choices=['text', 'json'],
                       help='Output format for console report: "text" (default, colorized console output) or "json" (only JSON files, no console report)')
    
    parser.add_argument('--include-volatile',
                       action='store_true',
                       help='Include volatile resources in comparison (pod, replicaset). By default these are excluded as they change frequently')
    
    parser.add_argument('--include-services-ingress', 
                       action='store_true', 
                       help='Include service and ingress resources in comparison')
    
    parser.add_argument('--include-resource-types',
                       metavar='TYPES',
                       help=f'Comma-separated list of resource types to include in comparison (overrides defaults). Use "all" to include all supported types. Supported: {", ".join(ALL_SUPPORTED_RESOURCES)}')
    
    parser.add_argument('--exclude-resources',
                       metavar='TYPES',
                       help=f'Comma-separated list of resource types to exclude from comparison. Supported resources: {", ".join(ALL_SUPPORTED_RESOURCES)}')
    
    parser.add_argument('--show-metadata',
                       action='store_true',
                       help='Keep metadata.labels and annotations in normalized output. By default, metadata is stripped to focus on actual configuration differences')
    
    args = parser.parse_args()

    # Validate arguments and determine mode
    single_cluster_mode = False
    namespaces_list = None
    
    # Check for conflicting arguments
    if args.c and (args.c1 or args.c2):
        print("Error: Cannot specify -c together with -c1 or -c2", file=sys.stderr)
        sys.exit(2)
    
    if args.n and args.namespaces:
        print("Error: Cannot specify both -n and --namespaces", file=sys.stderr)
        sys.exit(2)
    
    # Determine mode based on arguments
    if args.c:
        # Single-cluster mode
        single_cluster_mode = True
        if not args.namespaces:
            print("Error: Single-cluster mode (-c) requires --namespaces with at least 2 namespaces", file=sys.stderr)
            sys.exit(2)
        namespaces_list = [ns.strip() for ns in args.namespaces.split(',') if ns.strip()]
        if len(namespaces_list) < 2:
            print("Error: Single-cluster mode requires at least 2 namespaces", file=sys.stderr)
            sys.exit(2)
    elif args.c1 and args.c2:
        # Two-cluster mode
        single_cluster_mode = False
        if args.namespaces:
            namespaces_list = [ns.strip() for ns in args.namespaces.split(',') if ns.strip()]
    elif args.c1 or args.c2:
        print("Error: Two-cluster mode requires both -c1 and -c2", file=sys.stderr)
        sys.exit(2)
    else:
        print("Error: Must specify either -c (single-cluster mode) or -c1 and -c2 (two-cluster mode)", file=sys.stderr)
        sys.exit(2)

    resources = RESOURCES.copy()
    if args.r:
        resources = [r.strip() for r in args.r.split(',') if r.strip()]
    
    # Handle explicit include list (overrides defaults)
    if args.include_resource_types:
        if args.include_resource_types.lower() == 'all':
            resources = ALL_SUPPORTED_RESOURCES.copy()
        else:
            resources = [r.strip() for r in args.include_resource_types.split(',') if r.strip()]
            # Validate that all specified resources are supported
            unsupported = [r for r in resources if r.lower() not in [x.lower() for x in ALL_SUPPORTED_RESOURCES]]
            if unsupported:
                print(f"Error: Unsupported resource types: {', '.join(unsupported)}", file=sys.stderr)
                print(f"Supported types: {', '.join(ALL_SUPPORTED_RESOURCES)}", file=sys.stderr)
                sys.exit(2)
    else:
        # Use default behavior with optional additions
        if args.include_volatile:
            resources += VOLATILE_RESOURCES
        if args.include_services_ingress:
            resources += SERVICE_INGRESS_RESOURCES
    
    # Exclude specific resources if requested
    if args.exclude_resources:
        exclude_list = [r.strip().lower() for r in args.exclude_resources.split(',') if r.strip()]
        resources = [r for r in resources if r.lower() not in exclude_list]
        if not resources:
            print("Error: All resources excluded. Nothing to compare.", file=sys.stderr)
            sys.exit(2)

    # Usa sempre la stessa directory per output (latest)
    outdir = Path(args.o) if args.o else Path('./kdiff_output/latest')
    
    # Pulisce la directory se esiste già
    cleanup_output_dir(outdir)
    
    check_deps()

    if single_cluster_mode:
        # Single-cluster multi-namespace mode
        print(f"Mode: Single-cluster multi-namespace comparison")
        print(f"Cluster: {args.c}")
        print(f"Namespaces: {', '.join(namespaces_list)}")
        
        # Perform pairwise comparisons between all namespaces
        comparison_pairs = []
        for i in range(len(namespaces_list)):
            for j in range(i + 1, len(namespaces_list)):
                comparison_pairs.append((namespaces_list[i], namespaces_list[j]))
        
        all_successes = []
        for ns1, ns2 in comparison_pairs:
            print(f"\n{'='*60}")
            print(f"Comparing: {ns1} vs {ns2}")
            print(f"{'='*60}")
            
            dir1 = outdir / f"{args.c}_{ns1}"
            dir2 = outdir / f"{args.c}_{ns2}"
            diffs = outdir / f'diffs_{ns1}_vs_{ns2}'
            json_out = outdir / f'summary_{ns1}_vs_{ns2}.json'
            
            print(f"Fetching resources from {args.c}/{ns1}...")
            success1 = fetch_resources(args.c, dir1, resources, ns1, args.show_metadata)
            
            print(f"Fetching resources from {args.c}/{ns2}...")
            success2 = fetch_resources(args.c, dir2, resources, ns2, args.show_metadata)
            
            all_successes.append((success1, success2))
            
            if not success1 and not success2:
                print(f"\n{RED}[ERROR]:{RESET} Unable to retrieve resources from both namespaces.", file=sys.stderr)
                continue
            elif not success1:
                print(f"\n{RED}[ERROR]:{RESET} Unable to retrieve resources from '{ns1}'.", file=sys.stderr)
                print(f"{YELLOW}Continuing with available resources from '{ns2}'...{RESET}", file=sys.stderr)
            elif not success2:
                print(f"\n{RED}[ERROR]:{RESET} Unable to retrieve resources from '{ns2}'.", file=sys.stderr)
                print(f"{YELLOW}Continuing with available resources from '{ns1}'...{RESET}", file=sys.stderr)
            
            print("Comparing...")
            rc = subprocess.run(['python3', str(LIB / 'compare.py'), str(dir1), str(dir2), str(diffs), '--json-out', str(json_out)]).returncode
            
            # Generate HTML report for this comparison
            subprocess.run(['python3', str(LIB / 'diff_details.py'), str(outdir), 
                          '--cluster1', f"{args.c}/{ns1}", '--cluster2', f"{args.c}/{ns2}",
                          '--output-suffix', f"_{ns1}_vs_{ns2}"])
        
        # Generate summary report for all comparisons
        print(f"\n{'='*60}")
        print(f"{GREEN}Multi-namespace comparison completed{RESET}")
        print(f"Output directory: {outdir}")
        print(f"{YELLOW}View individual comparison reports in the output directory{RESET}")
        
    else:
        # Two-cluster mode
        print(f"Mode: Two-cluster comparison")
        print(f"Cluster 1: {args.c1}")
        print(f"Cluster 2: {args.c2}")
        if namespaces_list:
            print(f"Namespaces: {', '.join(namespaces_list)}")
        elif args.n:
            print(f"Namespace: {args.n}")
        else:
            print(f"Namespaces: all")
        
        dir1 = outdir / args.c1
        dir2 = outdir / args.c2
        diffs = outdir / 'diffs'
        json_out = outdir / 'summary.json'
        
        # Determine which namespace(s) to fetch
        ns_to_fetch = namespaces_list if namespaces_list else args.n

        print(f"Fetching resources from {args.c1}...")
        success1 = fetch_resources(args.c1, dir1, resources, ns_to_fetch, args.show_metadata)

        print(f"Fetching resources from {args.c2}...")
        success2 = fetch_resources(args.c2, dir2, resources, ns_to_fetch, args.show_metadata)
    
        print(f"Fetching resources from {args.c2}...")
        success2 = fetch_resources(args.c2, dir2, resources, ns_to_fetch, args.show_metadata)
        
        # If both clusters failed fetch, exit
        if not success1 and not success2:
            print(f"\n{RED}[ERROR] FATAL ERROR:{RESET} Unable to retrieve resources from both clusters.", file=sys.stderr)
            sys.exit(2)
        elif not success1:
            print(f"\n{RED}[ERROR]:{RESET} Unable to retrieve resources from '{args.c1}'.", file=sys.stderr)
            print(f"{YELLOW}Continuing anyway with available resources from '{args.c2}'...{RESET}", file=sys.stderr)
        elif not success2:
            print(f"\n{RED}[ERROR]:{RESET} Unable to retrieve resources from '{args.c2}'.", file=sys.stderr)
            print(f"{YELLOW}Continuing anyway with available resources from '{args.c1}'...{RESET}", file=sys.stderr)

        print("Comparing...")
        # call compare.py
        rc = subprocess.run(['python3', str(LIB / 'compare.py'), str(dir1), str(dir2), str(diffs), '--json-out', str(json_out)]).returncode

        # Report HTML interattivo dettagliato - SEMPRE generato (anche con 0 differenze)
        subprocess.run(['python3', str(LIB / 'diff_details.py'), str(outdir), '--cluster1', args.c1, '--cluster2', args.c2])
        
        # Path to the HTML report
        html_report = outdir / 'diff-details.html'

        if rc == 0:
            print(f"\n{GREEN}[OK] Clusters are equal for the verified resources.{RESET}")
            print(f"HTML Report: {html_report}")
            
            # Try to open HTML report in browser
            if open_html_in_browser(html_report):
                print(f"{GREEN}Opening report in browser...{RESET}")
            else:
                # Show OS-specific command to open the file
                import platform
                system = platform.system()
                
                # Use the path as-is (it's already relative to output dir)
                file_path = html_report
                
                if system == 'Darwin':  # macOS
                    cmd = f"open {file_path}"
                elif system == 'Linux':
                    cmd = f"xdg-open {file_path}"
                elif system == 'Windows':
                    cmd = f"start {file_path}"
                else:
                    cmd = f"<browser> {file_path}"
                print(f"{YELLOW}Open manually: {cmd}{RESET}")
            
            sys.exit(0)
        else:
            print(f"\n{YELLOW}[WARNING] Differences found. See {diffs} for details.{RESET}", file=sys.stderr)
            print(f"JSON Summary: {json_out}")
            
            # Report console (solo se richiesto formato text)
            if args.format == 'text':
                subprocess.run(['python3', str(LIB / 'report.py'), str(json_out), str(diffs), '--cluster1', args.c1, '--cluster2', args.c2])
            
            print(f"HTML Report: {html_report}")
            
            # Try to open HTML report in browser
            if open_html_in_browser(html_report):
                print(f"{GREEN}Opening report in browser...{RESET}")
            else:
                # Show OS-specific command to open the file
                import platform
                system = platform.system()
                
                # Use the path as-is (it's already relative to output dir)
                file_path = html_report
                
                if system == 'Darwin':  # macOS
                    cmd = f"open {file_path}"
                elif system == 'Linux':
                    cmd = f"xdg-open {file_path}"
                elif system == 'Windows':
                    cmd = f"start {file_path}"
                else:
                    cmd = f"<browser> {file_path}"
                print(f"{YELLOW}Open manually: {cmd}{RESET}")
            
            sys.exit(1)


if __name__ == '__main__':
    main()

