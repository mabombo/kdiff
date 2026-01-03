#!/usr/bin/env python3
"""
compare.py - Compare directories of normalized Kubernetes resources

This script compares two directories containing normalized Kubernetes resources
(in JSON format) and produces:
1. Unified diff files for each modified resource
2. Summary JSON with list of missing/different resources

Special features:
- Smart diff for ConfigMap: instead of showing entire JSON as modified,
  extracts data.* fields and compares them line by line, showing only real changes
- Standard JSON diff for all other resource types

Output:
- diffs/*.diff: one file for each modified resource
- summary.json: { missing_in_2: [...], missing_in_1: [...], different: [...] }

Exit code:
- 0: no differences
- 1: differences detected

Usage: python3 compare.py DIR1 DIR2 DIFFS_DIR [--json-out summary.json]
"""
import argparse
from pathlib import Path
import json
import sys
import difflib


def read_json_text(p: Path):
    """
    Legge un file JSON e lo converte in linee di testo per il diff.
    
    Args:
        p: Path del file JSON da leggere
    
    Returns:
        Lista di stringhe (linee) del JSON formattato in modo consistente
    
    Comportamento:
        1. Prova a parsare come JSON e riformattare (sort_keys, indent=2)
        2. Se fallisce, legge il file come testo raw
        
    Questo garantisce che diff identiche non vengano rilevate come diverse
    solo per formattazione diversa (spazi, ordine chiavi, etc).
    """
    try:
        txt = p.read_text(encoding='utf-8')
        # Normalizza formattazione per diff consistenti
        obj = json.loads(txt)
        return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False).splitlines(keepends=True)
    except Exception:
        # Fallback: leggi linee raw in caso di errore parsing
        return p.read_text(encoding='utf-8', errors='ignore').splitlines(keepends=True)


def generate_configmap_diff(pth1: Path, pth2: Path) -> str:
    """
    Genera un diff più utile per ConfigMap confrontando data.* linea per linea.
    
    Problema: i ConfigMap contengono spesso file di configurazione multi-linea
    nel campo data.* (es. data.config.yaml: "chiave1: valore1\\nchiave2: valore2").
    Un diff standard JSON mostrerebbe l'intera stringa come modificata, anche se
    è cambiata solo una riga.
    
    Soluzione: estrae ogni campo data.* separatamente, splita per newline, e genera
    un diff unified linea-per-linea per ogni campo modificato.
    
    Args:
        pth1: Path del ConfigMap nel cluster 1
        pth2: Path del ConfigMap nel cluster 2
    
    Returns:
        Stringa contenente il diff formattato, oppure None se:
        - Non sono ConfigMap
        - Errore durante elaborazione
        - Nessuna differenza nei data.*
    
    Formato output:
        --- /path/to/file1
        +++ /path/to/file2
        
        === data.config.yaml ===
        --- data.config.yaml (cluster1)
        +++ data.config.yaml (cluster2)
        @@ -10,7 +10,7 @@
         chiave1: valore1
        -chiave2: vecchio
        +chiave2: nuovo
         chiave3: valore3
    """
    try:
        # Carica entrambi i ConfigMap
        obj1 = json.loads(pth1.read_text(encoding='utf-8'))
        obj2 = json.loads(pth2.read_text(encoding='utf-8'))
        
        # Verifica che siano effettivamente ConfigMap
        if obj1.get('kind') != 'ConfigMap' or obj2.get('kind') != 'ConfigMap':
            return None
        
        # Estrai il campo data da entrambi
        data1 = obj1.get('data', {})
        data2 = obj2.get('data', {})
        
        # Raccogli tutte le chiavi presenti in almeno uno dei due ConfigMap
        all_keys = sorted(set(data1.keys()) | set(data2.keys()))
        
        # Inizializza output diff
        diff_lines = []
        diff_lines.append(f"--- {pth1}\n")
        diff_lines.append(f"+++ {pth2}\n")
        
        # Per ogni chiave data.*, confronta linea per linea
        for key in all_keys:
            val1 = data1.get(key, '')
            val2 = data2.get(key, '')
            
            # Solo se il valore è diverso
            if val1 != val2:
                diff_lines.append(f"\n=== data.{key} ===\n")
                
                # Splita il contenuto per newline (supporta file multi-riga)
                lines1 = val1.split('\n')
                lines2 = val2.split('\n')
                
                # Genera unified diff per questa chiave specifica
                # n=3 = mostra 3 linee di contesto prima/dopo le modifiche
                key_diff = difflib.unified_diff(
                    lines1,
                    lines2,
                    fromfile=f'data.{key} (cluster1)',
                    tofile=f'data.{key} (cluster2)',
                    lineterm='',  # Non aggiungere newline automaticamente
                    n=3  # Linee di contesto
                )
                
                # Aggiungi ogni linea del diff
                for line in key_diff:
                    diff_lines.append(line + '\n')
        
        # Ritorna il diff solo se ci sono differenze (più di header)
        return ''.join(diff_lines) if len(diff_lines) > 2 else None
        
    except Exception as e:
        # In caso di errore, ritorna None per fallback a diff standard
        return None


def main():
    """
    Entry point per confronto directory.
    
    Algoritmo:
        1. Scansiona tutti i .json in dir1
        2. Per ogni file, cerca corrispondente in dir2
        3. Se manca in dir2 → missing_in_2
        4. Se esiste in entrambi, confronta:
           a. ConfigMap? → usa generate_configmap_diff
           b. Altro? → usa diff JSON standard
        5. Scansiona dir2 per file che non esistono in dir1 → missing_in_1
        6. Genera summary.json con statistiche
    
    Args (via command line):
        dir1: Directory con risorse cluster 1 (normalizzate)
        dir2: Directory con risorse cluster 2 (normalizzate)
        diffs: Directory output per file .diff
        --json-out: Path per salvare summary.json
    
    Exit code:
        0: nessuna differenza rilevata
        1: differenze rilevate (normale quando ci sono diff)
    """
    # ============================================
    # PARSING ARGOMENTI
    # ============================================
    
    p = argparse.ArgumentParser(
        description='Confronta due directory di risorse Kubernetes normalizzate'
    )
    p.add_argument('dir1', help='Directory con risorse del cluster 1')
    p.add_argument('dir2', help='Directory con risorse del cluster 2')
    p.add_argument('diffs', help='Directory output per i file diff')
    p.add_argument('--json-out', dest='json_out', default=None,
                   help='Path per salvare summary.json')
    args = p.parse_args()

    # Converti a Path per gestione filesystem
    dir1 = Path(args.dir1)
    dir2 = Path(args.dir2)
    diffs = Path(args.diffs)
    diffs.mkdir(parents=True, exist_ok=True)  # Crea directory se non esiste

    # ============================================
    # INIZIALIZZA LISTE RISULTATI
    # ============================================
    
    missing_in_2 = []  # File presenti in cluster1 ma non in cluster2
    missing_in_1 = []  # File presenti in cluster2 ma non in cluster1
    different = []     # File presenti in entrambi ma con contenuto diverso

    # ============================================
    # SCANSIONE DIR1 (cluster 1)
    # ============================================
    
    # Per ogni file JSON in dir1
    for pth in sorted(dir1.glob('*.json')):
        rel = pth.name  # Nome file relativo (es. "deployment__ns__myapp.json")
        other = dir2 / rel  # Path corrispondente in dir2
        
        # Caso 1: file manca completamente in dir2
        if not other.exists():
            missing_in_2.append(rel)
            continue
        
        # Caso 2: file esiste in entrambi, confronta contenuto
        
        # Prova prima con diff intelligente per ConfigMap
        configmap_diff = generate_configmap_diff(pth, other)
        
        if configmap_diff:
            # È un ConfigMap E ha differenze
            different.append(rel)
            outname = f"{rel.replace('/', '__')}.diff"
            (diffs / outname).write_text(configmap_diff, encoding='utf-8')
        else:
            # Non è un ConfigMap OPPURE ConfigMap senza diff → usa diff standard
            a_lines = read_json_text(pth)
            b_lines = read_json_text(other)
            
            # Confronta linea per linea
            if a_lines != b_lines:
                different.append(rel)
                # Genera unified diff (-u style)
                df = ''.join(difflib.unified_diff(
                    a_lines, b_lines,
                    fromfile=str(pth),
                    tofile=str(other)
                ))
                outname = f"{rel.replace('/', '__')}.diff"
                (diffs / outname).write_text(df, encoding='utf-8')

    # ============================================
    # SCANSIONE DIR2 (cluster 2) per file mancanti in DIR1
    # ============================================
    
    for pth in sorted(dir2.glob('*.json')):
        rel = pth.name
        if not (dir1 / rel).exists():
            missing_in_1.append(rel)

    # ============================================
    # COSTRUZIONE SUMMARY JSON
    # ============================================
    
    summary = {
        'missing_in_2': missing_in_2,  # Risorse solo in cluster 1
        'missing_in_1': missing_in_1,  # Risorse solo in cluster 2
        'different': different,         # Risorse diverse tra i due cluster
        'counts': {
            'missing_in_2': len(missing_in_2),
            'missing_in_1': len(missing_in_1),
            'different': len(different),
        },
        'by_kind': {}  # Statistiche per tipo risorsa (deployment, configmap, etc)
    }

    # Helper per estrarre il kind dal nome file (es. "deployment__ns__app.json" → "deployment")
    def kind_from_name(n):
        return n.split('__', 1)[0] if '__' in n else 'unknown'

    # Aggrega statistiche per kind
    for k in set(missing_in_2 + missing_in_1 + different):
        kind = kind_from_name(k)
        bk = summary['by_kind'].setdefault(kind, {
            'missing_in_2': 0,
            'missing_in_1': 0,
            'different': 0
        })
        if k in missing_in_2:
            bk['missing_in_2'] += 1
        if k in missing_in_1:
            bk['missing_in_1'] += 1
        if k in different:
            bk['different'] += 1

    # ============================================
    # SALVA SUMMARY JSON
    # ============================================
    
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    # ============================================
    # EXIT CODE
    # ============================================
    
    # Exit 0 solo se NESSUNA differenza
    if (summary['counts']['missing_in_2'] == 0 and
        summary['counts']['missing_in_1'] == 0 and
        summary['counts']['different'] == 0):
        print('No differences detected')
        sys.exit(0)
    else:
        print('Differences detected')
        sys.exit(1)  # Normale quando ci sono differenze


if __name__ == '__main__':
    main()
