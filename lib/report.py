#!/usr/bin/env python3
"""
Genera report console colorato da summary.json e directory diffs.

Questo script produce un report testuale human-readable con:
- Statistiche aggregate (risorse mancanti/differenti)
- Top resource kinds per numero modifiche
- Breakdown per-kind (tabella)
- Sample diff per risorse più modificate

Input:
    - summary.json: File JSON con conteggi e liste risorse
    - diffs/: Directory contenente file .diff generatesti da compare.py

Output:
    - Report console colorato con ANSI escape codes

Uso:
    python3 report.py SUMMARY_JSON DIFFS_DIR [--top N] [--cluster1 NAME] [--cluster2 NAME]

Esempio:
    python3 lib/report.py kdiff_output/20240115_120000Z/summary.json \\
                           kdiff_output/20240115_120000Z/diffs --top 5
"""
import argparse
import json
from pathlib import Path
import sys

# ============================================
# ANSI COLOR CODES - Colori per Console
# ============================================
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
RED = '\033[0;31m'
BOLD = '\033[1m'
RESET = '\033[0m'


# ============================================
# FUNZIONI HELPER
# ============================================

def read_summary(p: Path):
    """
    Carica summary.json con gestione errori.
    
    Args:
        p: Path al file summary.json
    
    Returns:
        Dizionario JSON parsed
    
    Exit:
        Codice 2 se file non leggibile
    """
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Failed to read summary JSON: {e}", file=sys.stderr)
        sys.exit(2)


def top_kinds_by_total(by_kind, top):
    """
    Estrae top N resource kinds per numero totale modifiche.
    
    Args:
        by_kind: Dizionario by_kind da summary.json
        top: Numero massimo risultati
    
    Returns:
        Lista tuple (kind, total_count) ordinata per count DESC
    
    Calcolo total:
        total = missing_in_2 + missing_in_1 + different
    """
    items = []
    for k, v in by_kind.items():
        total = v.get('missing_in_2', 0) + v.get('missing_in_1', 0) + v.get('different', 0)
        items.append((k, total))
    
    # Ordina per totale decrescente
    items.sort(key=lambda x: -x[1])
    return items[:top]


# ============================================
# MAIN - Generazione Report Console
# ============================================

def main():
    """
    Genera report console colorato da summary.json e directory diffs.
    
    Report includes:
        1. Header con conteggi totali colorati
        2. Top N resource kinds per numero modifiche
        3. Tabella breakdown per-kind
        4. Sample diff (prime 12 righe) per top N risorse differenti
    
    Args CLI:
        summary: Path a summary.json
        diffs: Path a directory diffs/
        --top: Numero max risorse da showsre (default: 10)
        --cluster1: Nome primo cluster (default: "cluster1")
        --cluster2: Nome secondo cluster (default: "cluster2")
    """
    # ========================================
    # 1. PARSING ARGOMENTI
    # ========================================
    p = argparse.ArgumentParser()
    p.add_argument('summary')
    p.add_argument('diffs')
    p.add_argument('--top', type=int, default=10)
    p.add_argument('--cluster1', default='cluster1')
    p.add_argument('--cluster2', default='cluster2')
    args = p.parse_args()

    summary_path = Path(args.summary)
    diffs_dir = Path(args.diffs)

    # Validazione file
    if not summary_path.exists():
        print(f"Summary file not found: {summary_path}", file=sys.stderr)
        sys.exit(2)

    # ========================================
    # 2. CARICAMENTO DATI
    # ========================================
    summary = read_summary(summary_path)
    counts = summary.get('counts', {})
    missing2 = counts.get('missing_in_2', 0)
    missing1 = counts.get('missing_in_1', 0)
    different = counts.get('different', 0)

    # ========================================
    # 3. HEADER - Statistiche Colorate
    # ========================================
    print(f"{BOLD}K8s diff summary{RESET} — Missing in {args.cluster2}: {RED}{missing2}{RESET}, Missing in {args.cluster1}: {RED}{missing1}{RESET}, Different: {YELLOW}{different}{RESET}\n")

    # ========================================
    # 4. TOP RESOURCE KINDS
    # ========================================
    print("Top resource kinds by total changes:")
    top = top_kinds_by_total(summary.get('by_kind', {}), args.top)
    for kind, total in top:
        print(f"- {kind}: {total}")

    # ========================================
    # 5. PER-KIND BREAKDOWN TABLE
    # ========================================
    print("\nPer-kind breakdown:\n")
    print(f"{ 'RESOURCE':25} { 'M2':>8} { 'M1':>8} { 'DIFF':>10}")
    
    for kind in sorted(summary.get('by_kind', {}).keys()):
        v = summary['by_kind'][kind]
        m2 = v.get('missing_in_2', 0)
        m1 = v.get('missing_in_1', 0)
        diff = v.get('different', 0)
        print(f"{kind:25} {m2:8} {m1:8} {diff:10}")

    # ========================================
    # 6. SAMPLE DIFFS - Prime Righe
    # ========================================
    print("\nTop different resources (sample diffs):\n")
    
    # Mostra diff per prime N risorse differenti
    for f in summary.get('different', [])[: args.top]:
        diffname = Path(f).with_suffix('.diff').name
        difffile = diffs_dir / diffname
        
        print(f"--- {diffname} ---")
        
        if difffile.exists():
            try:
                lines = difffile.read_text(encoding='utf-8', errors='ignore').splitlines()
            except Exception:
                lines = []
            
            # Mostra solo prime 12 righe
            for line in lines[:12]:
                print(line)
            print("...")
        else:
            print(f"(diff file missing for {f})")

    # ========================================
    # 7. FOOTER - Link Directory Diffs
    # ========================================
    print(f"\nDettagli completi dei diff in: {diffs_dir}")


if __name__ == '__main__':
    main()
