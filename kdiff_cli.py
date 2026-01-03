#!/usr/bin/env python3
"""kdiff — compare Kubernetes resources between two clusters
This is the Python replacement for the previous Bash CLI.
Usage: bin/kdiff -c1 CONTEXT1 -c2 CONTEXT2 [options]
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
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
        print("Errore: 'kubectl' non trovato. Installalo e riprova.", file=sys.stderr)
        sys.exit(2)


def cleanup_output_dir(outdir: Path):
    """Pulisce la directory di output se esiste già."""
    if outdir.exists():
        try:
            shutil.rmtree(outdir)
            print(f"Pulizia directory output esistente: {outdir}")
        except Exception as e:
            print(f"Warning: Impossibile pulire {outdir}: {e}", file=sys.stderr)


# dynamic import helper to load normalize.normalize
def load_normalize_func():
    spec = importlib.util.spec_from_file_location('normalize', str(LIB / 'normalize.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return getattr(mod, 'normalize')


def fetch_resources(context: str, outdir: Path, resources: list[str], namespace: str | None, show_metadata: bool = False):
    outdir.mkdir(parents=True, exist_ok=True)
    norm = load_normalize_func()
    has_errors = False
    resource_count = 0

    for kind in resources:
        print(f"[{context}] Fetching {kind}...")
        cmd = ['kubectl', '--context', context]
        if namespace:
            cmd += ['-n', namespace, 'get', kind, '-o', 'json']
        else:
            cmd += ['get', kind, '--all-namespaces', '-o', 'json']

        try:
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                
                # Errori CRITICI di connettività (interrompono l'esecuzione)
                if 'does not exist' in stderr:
                    print(f"\n{RED}✗ ERRORE CRITICO:{RESET} Context '{context}' non esiste in kubeconfig", file=sys.stderr)
                    print(f"{YELLOW}💡 Suggerimento:{RESET} Verifica con 'kubectl config get-contexts'", file=sys.stderr)
                    sys.exit(2)
                elif 'no such host' in stderr or 'dial tcp' in stderr:
                    print(f"\n{RED}✗ ERRORE CRITICO:{RESET} Impossibile connettersi al cluster '{context}'", file=sys.stderr)
                    print(f"{YELLOW}💡 Cause possibili:{RESET}", file=sys.stderr)
                    print(f"  - Cluster non raggiungibile (DNS, rete, firewall)", file=sys.stderr)
                    print(f"  - VPN non attiva", file=sys.stderr)
                    print(f"  - API server non disponibile", file=sys.stderr)
                    if 'no such host' in stderr:
                        # Estrai hostname dall'errore
                        import re
                        hostname_match = re.search(r'lookup ([^:]+):', stderr)
                        if hostname_match:
                            print(f"  - Hostname non risolvibile: {hostname_match.group(1)}", file=sys.stderr)
                    sys.exit(2)
                elif 'timeout' in stderr.lower() or 'timed out' in stderr.lower():
                    print(f"\n{RED}✗ ERRORE CRITICO:{RESET} Timeout connessione al cluster '{context}'", file=sys.stderr)
                    print(f"{YELLOW}💡 Suggerimento:{RESET} Verifica connettività di rete e che il cluster sia attivo", file=sys.stderr)
                    sys.exit(2)
                
                # Errori NON critici (permessi, risorse vuote, etc)
                elif 'Forbidden' in stderr or 'forbidden' in stderr:
                    print(f"[{context}] {RED}✗{RESET} Permessi insufficienti per {kind} a livello cluster.", file=sys.stderr)
                    if not namespace:
                        print(f"[{context}] {YELLOW}💡 Suggerimento:{RESET} Specifica un namespace con -n <namespace>", file=sys.stderr)
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
                print(f"[{context}] Nessun oggetto {kind}.")
                continue
            for item in items:
                name = item.get('metadata', {}).get('name')
                ns = item.get('metadata', {}).get('namespace')
                if ns:
                    fname = f"{kind}__{ns}__{name}.json"
                else:
                    fname = f"{kind}__{name}.json"
                path = outdir / fname
                # pass show-metadata flag to the normalizer
                n = norm(item, keep_metadata=bool(show_metadata))
                path.write_text(json.dumps(n, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding='utf-8')
        except Exception as e:
            print(f"[{context}] Errore fetching {kind}: {e}", file=sys.stderr)
            continue
    
    # Verifica finale: se non sono state recuperate risorse, potrebbe essere un problema serio
    if resource_count == 0 and has_errors:
        print(f"\n{RED}✗ ATTENZIONE:{RESET} Nessuna risorsa recuperata da '{context}' a causa di errori.", file=sys.stderr)
        print(f"{YELLOW}💡 Suggerimento:{RESET} Risolvi gli errori sopra prima di continuare.", file=sys.stderr)
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c1', required=True)
    parser.add_argument('-c2', required=True)
    parser.add_argument('-r')
    parser.add_argument('-n')
    parser.add_argument('-o')
    parser.add_argument('-f', '--format', dest='format', default='text')
    parser.add_argument('--include-volatile', action='store_true')
    parser.add_argument('--include-services-ingress', action='store_true', help='Include service and ingress resources in comparison')
    parser.add_argument('--include-resource-types', help=f'Comma-separated list of resource types to include in comparison (overrides defaults). Use "all" to include all supported types. Supported: {", ".join(ALL_SUPPORTED_RESOURCES)}')
    parser.add_argument('--exclude-resources', help=f'Comma-separated list of resource types to exclude from comparison. Supported resources: {", ".join(ALL_SUPPORTED_RESOURCES)}')
    parser.add_argument('--show-metadata', action='store_true', help='Keep metadata.labels and annotations in normalized output')
    args = parser.parse_args()

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
    
    # Use actual cluster names instead of generic cluster1/cluster2
    dir1 = outdir / args.c1
    dir2 = outdir / args.c2
    diffs = outdir / 'diffs'
    json_out = outdir / 'summary.json'

    check_deps()

    print(f"Fetching resources from {args.c1}...")
    success1 = fetch_resources(args.c1, dir1, resources, args.n, args.show_metadata)

    print(f"Fetching resources from {args.c2}...")
    success2 = fetch_resources(args.c2, dir2, resources, args.n, args.show_metadata)
    
    # Se entrambi i cluster hanno fallito il fetch, esci
    if not success1 and not success2:
        print(f"\n{RED}✗ ERRORE FATALE:{RESET} Impossibile recuperare risorse da entrambi i cluster.", file=sys.stderr)
        sys.exit(2)
    elif not success1:
        print(f"\n{RED}✗ ERRORE:{RESET} Impossibile recuperare risorse da '{args.c1}'.", file=sys.stderr)
        print(f"{YELLOW}Continuo comunque con le risorse disponibili da '{args.c2}'...{RESET}", file=sys.stderr)
    elif not success2:
        print(f"\n{RED}✗ ERRORE:{RESET} Impossibile recuperare risorse da '{args.c2}'.", file=sys.stderr)
        print(f"{YELLOW}Continuo comunque con le risorse disponibili da '{args.c1}'...{RESET}", file=sys.stderr)

    print("Confronto...")
    # call compare.py
    rc = subprocess.run(['python3', str(LIB / 'compare.py'), str(dir1), str(dir2), str(diffs), '--json-out', str(json_out)]).returncode

    if rc == 0:
        print(f"\n{GREEN}✅ I cluster sono uguali per le risorse verificate.{RESET}")
        sys.exit(0)
    else:
        print(f"\n{YELLOW}⚠️ Sono state trovate differenze. Vedi {diffs} per i dettagli.{RESET}", file=sys.stderr)
        print(f"Sintesi JSON: {json_out}")
        
        # Report console (solo se richiesto formato text)
        if args.format == 'text':
            subprocess.run(['python3', str(LIB / 'report.py'), str(json_out), str(diffs), '--cluster1', args.c1, '--cluster2', args.c2])
        
        # Report Markdown/HTML semplici (commentati - usare diff-details invece)
        # subprocess.run(['python3', str(LIB / 'report_md.py'), str(json_out), str(diffs), str(outdir), '--cluster1', args.c1, '--cluster2', args.c2])
        
        # Report HTML interattivo dettagliato con diff campo per campo
        subprocess.run(['python3', str(LIB / 'diff_details.py'), str(outdir), '--cluster1', args.c1, '--cluster2', args.c2])
        sys.exit(1)


if __name__ == '__main__':
    main()

