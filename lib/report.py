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
    - diffs/: Directory contenente file .diff generati da compare.py

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
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
BOLD = '\033[1m'
DIM = '\033[2m'
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


def print_section_header(title):
    """Stampa un header di sezione con separatore"""
    print(f"\n{BOLD}{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 80}{RESET}\n")


def print_subsection(title):
    """Stampa un sottotitolo"""
    print(f"\n{BOLD}{title}{RESET}")
    print(f"{DIM}{'─' * 60}{RESET}")


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
    total_changes = missing2 + missing1 + different
    by_kind = summary.get('by_kind', {})

    # ========================================
    # 3. HEADER - Report Overview
    # ========================================
    print(f"\n{BOLD}{MAGENTA}{'=' * 80}{RESET}")
    print(f"{BOLD}{MAGENTA}KDIFF - Kubernetes Cluster Comparison Report{RESET}")
    print(f"{BOLD}{MAGENTA}{'=' * 80}{RESET}")
    
    print(f"\n{BOLD}Clusters Compared:{RESET}")
    print(f"  {CYAN}{args.cluster1}{RESET}")
    print(f"  {CYAN}{args.cluster2}{RESET}")

    # ========================================
    # 4. SUMMARY OVERVIEW - Box Colorato
    # ========================================
    print_section_header("Summary Overview")
    
    if total_changes == 0:
        print(f"{GREEN}[OK] Clusters are IDENTICAL for the compared resources!{RESET}\n")
        print(f"{DIM}No differences detected between the two clusters.{RESET}")
        return
    
    print(f"{BOLD}Total Changes Detected:{RESET} {YELLOW}{total_changes}{RESET}\n")
    
    # Metriche principali senza box
    # NOTA: missing_in_2 = risorse solo in cluster1, missing_in_1 = risorse solo in cluster2
    print(f"{BOLD}Resources only in {args.cluster1}:{RESET} {RED}{missing2}{RESET}")
    print(f"  {DIM}These resources exist in {args.cluster1} but not in {args.cluster2}{RESET}")
    
    print(f"\n{BOLD}Resources only in {args.cluster2}:{RESET} {RED}{missing1}{RESET}")
    print(f"  {DIM}These resources exist in {args.cluster2} but not in {args.cluster1}{RESET}")
    
    print(f"\n{BOLD}Resources with differences:{RESET} {YELLOW}{different}{RESET}")
    print(f"  {DIM}Same resources present in both clusters but with different configurations{RESET}")


    # ========================================
    # 5. TOP RESOURCE KINDS
    # ========================================
    print_section_header("Top Resource Types by Changes")
    
    top = top_kinds_by_total(by_kind, min(args.top, 10))
    if top:
        for i, (kind, total) in enumerate(top, 1):
            v = by_kind[kind]
            m1 = v.get('missing_in_1', 0)
            m2 = v.get('missing_in_2', 0)
            diff = v.get('different', 0)
            
            print(f"{BOLD}{i:2}.{RESET} {CYAN}{kind:<25}{RESET} {BOLD}{total:4}{RESET} changes")
            print(f"    Only in {args.cluster1}: {RED}{m1:3}{RESET}  |  Only in {args.cluster2}: {RED}{m2:3}{RESET}  |  Modified: {YELLOW}{diff:3}{RESET}")
    else:
        print(f"{DIM}No resource changes detected.{RESET}")

    # ========================================
    # 6. DETAILED BREAKDOWN BY RESOURCE TYPE
    # ========================================
    print_section_header("📋 Detailed Breakdown by Resource Type")
    
    # Ordina per totale cambiamenti decrescente
    sorted_kinds = sorted(
        by_kind.items(), 
        key=lambda x: x[1].get('missing_in_1', 0) + x[1].get('missing_in_2', 0) + x[1].get('different', 0),
        reverse=True
    )
    
    if sorted_kinds:
        # Usa i nomi completi dei cluster nell'header
        header_c1 = f"Only {args.cluster1}"
        header_c2 = f"Only {args.cluster2}"
        
        print(f"{BOLD}{'Resource Type':<25} {header_c1:>15} {header_c2:>15} {'Modified':>12} {'Total':>10}{RESET}")
        print(f"{DIM}{'-' * 25} {'-' * 15} {'-' * 15} {'-' * 12} {'-' * 10}{RESET}")
        
        for kind, v in sorted_kinds:
            m1 = v.get('missing_in_1', 0)
            m2 = v.get('missing_in_2', 0)
            diff = v.get('different', 0)
            total = m1 + m2 + diff
            
            if total > 0:
                # Colora la riga in base al tipo di cambiamento prevalente
                if diff > m1 and diff > m2:
                    color = YELLOW
                elif m1 > 0 or m2 > 0:
                    color = RED
                else:
                    color = ""
                
                # m2 = solo in cluster1, m1 = solo in cluster2
                print(f"{color}{kind:<25} {m2:>15} {m1:>15} {diff:>12} {BOLD}{total:>10}{RESET}")

    # ========================================
    # 7. TOP MODIFIED RESOURCES
    # ========================================
    if different > 0:
        print_section_header(f"Top {min(args.top, len(summary.get('different', [])))} Modified Resources")
        
        for i, f in enumerate(summary.get('different', [])[:args.top], 1):
            # Estrai informazioni dal nome file
            parts = f.replace('.json', '').split('__')
            if len(parts) >= 3:
                res_type, namespace, name = parts[0], parts[1], '__'.join(parts[2:])
                resource_display = f"{CYAN}{res_type}{RESET}/{BOLD}{name}{RESET} (ns: {DIM}{namespace}{RESET})"
            else:
                resource_display = f"{BOLD}{f}{RESET}"
            
            print(f"\n{BOLD}{i}.{RESET} {resource_display}")
            
            diffname = Path(f).with_suffix('.diff').name
            difffile = diffs_dir / diffname
            
            if difffile.exists():
                try:
                    lines = difffile.read_text(encoding='utf-8', errors='ignore').splitlines()
                    # Conta le modifiche
                    additions = sum(1 for l in lines if l.startswith('+') and not l.startswith('+++'))
                    deletions = sum(1 for l in lines if l.startswith('-') and not l.startswith('---'))
                    print(f"   {GREEN}+{additions} additions{RESET} │ {RED}-{deletions} deletions{RESET}")
                    
                    # Mostra preview delle prime righe significative
                    significant_lines = [l for l in lines if l.startswith(('+', '-')) and not l.startswith(('+++', '---'))][:3]
                    if significant_lines:
                        print(f"   {DIM}Preview:{RESET}")
                        for line in significant_lines:
                            if line.startswith('+'):
                                print(f"   {GREEN}{line[:70]}{RESET}")
                            elif line.startswith('-'):
                                print(f"   {RED}{line[:70]}{RESET}")
                except Exception:
                    print(f"   {DIM}(Unable to read diff details){RESET}")

    # ========================================
    # 8. FOOTER - Links e Azioni
    # ========================================
    print_section_header("Files & Next Steps")
    print(f"Detailed HTML Report: {CYAN}{summary_path.parent / 'diff-details.html'}{RESET}")
    print(f"JSON Summary:         {CYAN}{summary_path}{RESET}")
    print(f"Diff Files:           {CYAN}{diffs_dir}{RESET}")
    
    print(f"\n{DIM}{'=' * 80}{RESET}\n")


if __name__ == '__main__':
    main()
