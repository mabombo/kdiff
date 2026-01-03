#!/usr/bin/env python3
"""
Genera report.md e report.html da summary.json e directory diffs.

Questo script produce due file di report testuale:
    1. report.md: Report Markdown formattato
    2. report.html: HTML wrapper semplice del Markdown (pre-formattato)

Input:
    - summary.json: File JSON con statistiche aggregate
    - diffs/: Directory con file .diff
    - outdir: Directory output per report generatesti

Output:
    - report.md: Markdown con statistiche, breakdown, sample diffs
    - report.html: HTML semplice con contenuto escaped

Uso:
    python3 report_md.py SUMMARY_JSON DIFFS_DIR OUTDIR \\
                          [--cluster1 NAME] [--cluster2 NAME]

Esempio:
    python3 lib/report_md.py kdiff_output/20240115_120000Z/summary.json \\
                              kdiff_output/20240115_120000Z/diffs \\
                              kdiff_output/20240115_120000Z

Nota:
    - Questo è un report testuale semplificato
    - Per report HTML avanzato: usare diff_details.py che generates HTML interattivo
"""
import argparse
import json
from pathlib import Path
import html
import sys


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


# ============================================
# MAIN - Generazione Report MD/HTML
# ============================================

def main():
    """
    Genera report.md e report.html da summary.json e diffs/.
    
    Report Markdown includes:
        1. Header con statistiche aggregate
        2. Timestamp generateszione
        3. Top resource kinds ordinati per total changes
        4. Tabella breakdown per-kind
        5. Sample diffs (prime 10 risorse differenti)
    
    Report HTML:
        - Wrapper HTML semplice del Markdown
        - Contenuto escaped in blocco <pre>
        - CSS minimale per leggibilità
    
    Args CLI:
        summary: Path a summary.json
        diffs: Path a directory diffs/
        outdir: Path directory output
        --cluster1: Nome primo cluster (default: "cluster1")
        --cluster2: Nome secondo cluster (default: "cluster2")
    """
    # ========================================
    # 1. PARSING ARGOMENTI E VALIDAZIONE
    # ========================================
    p = argparse.ArgumentParser()
    p.add_argument('summary')
    p.add_argument('diffs')
    p.add_argument('outdir')
    p.add_argument('--cluster1', default='cluster1')
    p.add_argument('--cluster2', default='cluster2')
    args = p.parse_args()

    summary_path = Path(args.summary)
    diffs_dir = Path(args.diffs)
    outdir = Path(args.outdir)
    
    # Crea directory output se non esiste
    outdir.mkdir(parents=True, exist_ok=True)

    # ========================================
    # 2. CARICAMENTO DATI
    # ========================================
    summary = read_summary(summary_path)
    counts = summary.get('counts', {})
    missing2 = counts.get('missing_in_2', 0)
    missing1 = counts.get('missing_in_1', 0)
    different = counts.get('different', 0)

    # File output
    md = outdir / 'report.md'
    html_out = outdir / 'report.html'

    # ========================================
    # 3. GENERAZIONE REPORT MARKDOWN
    # ========================================
    with md.open('w', encoding='utf-8') as fh:
        # ----------------------------------------
        # 3.1 Header e Statistiche
        # ----------------------------------------
        fh.write('# kdiff report\n\n')
        fh.write(f"**Summary:** missing in {args.cluster2}: **{missing2}**, missing in {args.cluster1}: **{missing1}**, different: **{different}**\n\n")
        
        # Timestamp UTC
        from datetime import datetime, timezone
        fh.write(f"Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n\n---\n\n")

        # ----------------------------------------
        # 3.2 Top Resource Kinds
        # ----------------------------------------
        fh.write('## Top resource kinds by total changes\n\n')
        
        # Calcola totale per kind e ordina
        kinds = []
        for k, v in summary.get('by_kind', {}).items():
            total = v.get('missing_in_2', 0) + v.get('missing_in_1', 0) + v.get('different', 0)
            kinds.append((total, k))
        kinds.sort(reverse=True)
        
        # Lista ordinata per totale decrescente
        for total, kind in kinds:
            fh.write(f"- {kind}: {total}\n")

        # ----------------------------------------
        # 3.3 Per-Kind Breakdown Table
        # ----------------------------------------
        fh.write('\n---\n\n')
        fh.write('## Per-kind breakdown\n\n')
        fh.write(f'| Resource | Missing in {args.cluster2} | Missing in {args.cluster1} | Different |\n')
        fh.write('|---:|---:|---:|---:|\n')
        
        for kind in sorted(summary.get('by_kind', {}).keys()):
            v = summary['by_kind'][kind]
            m2 = v.get('missing_in_2', 0)
            m1 = v.get('missing_in_1', 0)
            diff = v.get('different', 0)
            fh.write(f"| {kind} | {m2} | {m1} | {diff} |\n")

        # ----------------------------------------
        # 3.4 Sample Diffs (Prime 10)
        # ----------------------------------------
        fh.write('\n---\n\n')
        fh.write('## Sample diffs (first 10)\n\n')
        
        # Mostra diff completo per prime 10 risorse differenti
        for f in summary.get('different', [])[:10]:
            diffname = Path(f).with_suffix('.diff').name
            fh.write(f"### {diffname} \n\n")
            
            difffile = diffs_dir / diffname
            if difffile.exists():
                # Blocco diff formattato con sintassi Markdown
                fh.write('```diff\n')
                try:
                    fh.write(difffile.read_text(encoding='utf-8', errors='ignore'))
                except Exception:
                    fh.write('(failed to read diff file)\n')
                fh.write('\n```\n')
            else:
                fh.write('(diff file missing)\n')

    # ========================================
    # 4. GENERAZIONE HTML WRAPPER
    # ========================================
    # HTML semplice con Markdown escaped in <pre>
    md_text = md.read_text(encoding='utf-8')
    
    with html_out.open('w', encoding='utf-8') as fh:
        fh.write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>kdiff report</title>\n')
        
        # CSS minimale per leggibilità
        fh.write('<style>body{font-family:Arial,Helvetica,sans-serif;padding:20px;}pre.diff{background:#f6f8fa;padding:10px;border-radius:6px;overflow:auto;}</style>\n')
        
        fh.write('</head>\n<body>\n<pre>\n')
        
        # Escape HTML per preservare formattazione Markdown
        fh.write(html.escape(md_text))
        
        fh.write('\n</pre>\n</body>\n</html>')

    # ========================================
    # 5. CONFERMA OUTPUT
    # ========================================
    print(f"Wrote: {md} and {html_out}")


if __name__ == '__main__':
    from datetime import datetime, timezone
    main()
