#!/usr/bin/env python3
"""
diff_details.py - Generatore Report Dettagliati Diff Kubernetes

Questo script genera report dettagliati campo-per-campo delle differenze
tra risorse Kubernetes di due cluster.

Input:
  - OUTDIR/summary.json: summary del confronto (da compare.py)
  - OUTDIR/<cluster1>/: directory con risorse normalizzate cluster 1
  - OUTDIR/<cluster2>/: directory con risorse normalizzate cluster 2
  - OUTDIR/diffs/*.diff: file diff già generati

Output:
  - diff-details.md: report markdown con tabelle differenze
  - diff-details.json: dati strutturati per automazione
  - diff-details.html: report HTML interattivo con UI avanzata ⭐

Funzionalità HTML:
  - Dashboard with statistics aggregate
  - Collapsible sections per tipo risorsa (Kind)
  - Risorse individuali expandable
  - Modal popup to view complete diffs
  - Controlli zoom (+, -, reset) per diff
  - Tabella risorse presenti solo in un cluster
  - Color-coding per tipi di risorsa
  - Legenda interattiva

Uso:
  python3 lib/diff_details.py <output_directory> [--cluster1 name1] [--cluster2 name2]

Esempio:
  python3 lib/diff_details.py ./kdiff_output/20260103T153045Z
"""
import argparse
import json
from pathlib import Path
import sys
import html as html_lib
import datetime
import typing


# ============================================
# UTILITY FUNCTIONS - Manipolazione Dati
# ============================================

def flatten(obj: typing.Any, prefix: str = "") -> dict:
    """
    Appiattisce un oggetto JSON nested in un dizionario flat.
    
    Converte strutture profondamente annidate in path flat per confronto field-level.
    
    Args:
        obj: Oggetto da appiattire (dict, list, o valore scalare)
        prefix: Prefisso corrente del path (uso interno ricorsivo)
    
    Returns:
        Dizionario con path come chiavi e valori scalari
    
    Esempi:
        Input:  {"a": {"b": 1, "c": [2, 3]}}
        Output: {"a.b": 1, "a.c[0]": 2, "a.c[1]": 3}
        
        Input:  {"metadata": {"name": "test", "labels": {"app": "web"}}}
        Output: {"metadata.name": "test", "metadata.labels.app": "web"}
    
    Comportamento:
        - Dict: crea path con dot notation (es. "spec.replicas")
        - List: crea path con bracket notation (es. "containers[0]")
        - Scalari: ritorna come coppia path:valore
    """
    out = {}
    
    if isinstance(obj, dict):
        # Dizionario: processa ogni chiave ricorsivamente
        for k, v in obj.items():
            # Costruisci path: se prefix esiste usa "prefix.key", altrimenti solo "key"
            p = f"{prefix}.{k}" if prefix else k
            out.update(flatten(v, p))
    
    elif isinstance(obj, list):
        # Lista: processa ogni elemento con indice
        for i, v in enumerate(obj):
            # Path con bracket notation: "path[0]", "path[1]", etc
            p = f"{prefix}[{i}]"
            out.update(flatten(v, p))
    
    else:
        # Valore scalare (string, number, bool, None): aggiungi al risultato
        out[prefix] = obj
    
    return out


def shortrepr(v):
    """
    Genera una rappresentazione breve e leggibile di un valore.
    
    Args:
        v: Valore da rappresentare (qualsiasi tipo)
    
    Returns:
        Stringa formattata con lunghezza max 200 caratteri
    
    Comportamento:
        - None → "❌ (not set)"
        - Valori lunghi → troncati a 200 char + "..."
        - Newline → convertiti in \\n per visualizzazione inline
        - JSON serializable → usa json.dumps per formattazione
    """
    if v is None:
        return "❌ (not set)"
    
    try:
        # Prova serializzazione JSON per formattazione consistente
        s = json.dumps(v, ensure_ascii=False)
    except Exception:
        # Fallback: conversione stringa diretta
        s = str(v)
    
    # Tronca se troppo lungo
    if len(s) > 200:
        s = s[:197] + "..."
    
    # Sostituisci newline per visualizzazione inline
    return s.replace("\n", "\\n")


def top_key_for_path(p: str) -> str:
    """
    Estrae la chiave di primo livello da un path nested.
    
    Args:
        p: Path in formato flat (es. "spec.template.spec.containers[0].image")
    
    Returns:
        Prima componente del path (es. "spec")
    
    Esempi:
        "spec.replicas" → "spec"
        "metadata.name" → "metadata"
        "containers[0].image" → "containers"
        "status.phase" → "status"
    
    Uso: Aggregare statistiche per chiave di primo livello
          (quanti campi spec.* sono cambiati, quanti metadata.*, etc)
    """
    import re
    
    # Split su '.' o '[' per isolare il primo token
    # Regex: split su punto O parentesi quadra aperta
    m = re.split(r"[.\[]", p)
    
    # Ritorna primo token, oppure path originale se split fallisce
    return m[0] if m else p


# ============================================
# COLOR SCHEME - Palette Colori Risorse K8s
# ============================================

def get_kind_color(kind: str) -> str:
    """
    Ritorna un colore HEX univoco per ogni tipo di risorsa Kubernetes.
    
    Args:
        kind: Type risorsa K8s (es. "Deployment", "ConfigMap", "Service")
    
    Returns:
        Codice colore HEX (es. "#2563eb")
    
    Palette design:
        - Deployment: blu (workload principale)
        - ConfigMap: verde (configurazione)
        - Secret: rosso (credenziali sensibili)
        - Service: cyan (networking)
        - StatefulSet: viola (stateful apps)
        - DaemonSet: arancione (system agents)
        - etc.
    
    Uso:
        - Badge colorati nei report HTML
        - Sezioni visivamente distinte per tipo risorsa
        - Legenda colori interattiva
    
    Nota: totale 16 colori distinti + 1 default gray per tipi sconosciuti
    """
    colors = {
        'Deployment': '#2563eb',      # blu - workload principale
        'StatefulSet': '#7c3aed',     # viola - app stateful
        'DaemonSet': '#ea580c',       # arancione - agent system-wide
        'Service': '#0891b2',         # cyan - networking
        'ConfigMap': '#059669',       # verde - configurazione
        'Secret': '#dc2626',          # rosso - credenziali
        'Ingress': '#db2777',         # rosa - routing HTTP
        'PersistentVolumeClaim': '#ca8a04',  # giallo-scuro - storage
        'ServiceAccount': '#475569',  # slate - identity
        'Role': '#4f46e5',            # indigo - RBAC role
        'RoleBinding': '#7c2d12',     # arancione-scuro - RBAC binding
        'HorizontalPodAutoscaler': '#0e7490',  # cyan-scuro - autoscaling
        'CronJob': '#15803d',         # verde-scuro - scheduled jobs
        'Job': '#166534',             # verde-più-scuro - one-off jobs
        'ReplicaSet': '#6366f1',      # indigo-chiaro - replica management
        'Pod': '#9333ea',             # viola-chiaro - pod standalone
    }
    
    # Default: grigio per tipi non mappati
    return colors.get(kind, '#374151')


def get_namespace_color(namespace: str) -> str:
    """
    Ritorna un colore solido univoco per ogni namespace.
    
    Args:
        namespace: Nome del namespace Kubernetes
    
    Returns:
        Codice colore HEX (es. "#667eea")
    
    Palette colori:
        - Colori solidi distinti e vibranti per differenziare visualmente i namespace
        - Hash-based per consistenza: stesso namespace = stesso colore
    
    Uso:
        - Badge namespace nei report HTML
        - Identificazione visiva rapida quando si confrontano multipli namespace
    """
    # Hash del namespace per ottenere un indice consistente
    hash_value = sum(ord(c) for c in namespace)
    
    # Palette di colori solidi vibranti e distinti
    colors = [
        "#667eea",  # indigo
        "#f56565",  # red
        "#38b2ac",  # teal
        "#48bb78",  # green
        "#ed8936",  # orange
        "#9f7aea",  # purple
        "#ed64a6",  # pink
        "#4299e1",  # blue
        "#ecc94b",  # yellow
        "#f687b3",  # light pink
        "#4fd1c5",  # cyan
        "#fc8181",  # light red
        "#9ae6b4",  # light green
        "#fbd38d",  # light orange
        "#a78bfa",  # light purple
        "#63b3ed",  # light blue
    ]
    
    # Seleziona colore basato su hash
    index = hash_value % len(colors)
    return colors[index]


# ============================================
# MISSING RESOURCES TABLE - Risorse Esclusive
# ============================================

def generate_missing_resources_table(summary, cluster1, cluster2, c1_dir, c2_dir):
    """
    Genera tabella HTML per risorse presenti solo in un cluster.
    
    Args:
        summary: Dizionario summary.json con liste missing_in_1 e missing_in_2
        cluster1: Name primo cluster
        cluster2: Name secondo cluster
        c1_dir: Path directory risorse cluster 1
        c2_dir: Path directory risorse cluster 2
    
    Returns:
        Stringa HTML con tabella formattata
    
    Tabella include:
        - Type risorsa (Kind) con badge colorato
        - Name risorsa
        - Namespace
        - Badge "Only in <cluster>" con colore distintivo
    
    Comportamento:
        - missing_in_2: risorsa in cluster1 ma NON in cluster2
        - missing_in_1: risorsa in cluster2 ma NON in cluster1
        - Se nessuna risorsa mancante: messaggio "No resources found..."
        - In caso di errore lettura: messaggio "Unable to read..."
    
    Design:
        - Tabella responsive con 4 colonne
        - Badge colorati per Kind
        - Badge distintivi per missing_in_c1 vs missing_in_c2
        - Cliccabile per navigare alla risorsa specifica
    """
    # Estrai liste dal summary
    missing_in_c2 = summary.get('missing_in_2', [])
    missing_in_c1 = summary.get('missing_in_1', [])
    
    # Caso 1: nessuna risorsa mancante
    if not missing_in_c2 and not missing_in_c1:
        return '<p style="color: #6b7280; font-style: italic;">No resources found exclusively in one cluster.</p>'
    
    # Lista per raccogliere tutte le risorse con i loro metadati per l'ordinamento
    all_resources = []
    
    # ========================================
    # Risorse presenti SOLO in cluster1
    # ========================================
    for resource_file in missing_in_c2:
        try:
            resource_path = c1_dir / resource_file
            if resource_path.exists():
                # Carica risorsa per estrarre metadati
                with open(resource_path) as file:
                    obj = json.load(file)
                kind = obj.get('kind', 'Unknown')
                name = obj.get('metadata', {}).get('name', 'unknown')
                namespace = obj.get('metadata', {}).get('namespace', '-')
                color = get_kind_color(kind)
                
                all_resources.append({
                    'kind': kind,
                    'name': name,
                    'namespace': namespace,
                    'color': color,
                    'location': f'Only in {cluster1}',
                    'location_class': 'missing-in-c2'
                })
        except Exception:
            # Ignora errori (file corrotto, JSON invalido, etc)
            pass
    
    # ========================================
    # Risorse presenti SOLO in cluster2
    # ========================================
    for resource_file in missing_in_c1:
        try:
            resource_path = c2_dir / resource_file
            if resource_path.exists():
                with open(resource_path) as file:
                    obj = json.load(file)
                kind = obj.get('kind', 'Unknown')
                name = obj.get('metadata', {}).get('name', 'unknown')
                namespace = obj.get('metadata', {}).get('namespace', '-')
                color = get_kind_color(kind)
                
                all_resources.append({
                    'kind': kind,
                    'name': name,
                    'namespace': namespace,
                    'color': color,
                    'location': f'Only in {cluster2}',
                    'location_class': 'missing-in-c1'
                })
        except (IOError, json.JSONDecodeError, KeyError):
            # Ignore unreadable or malformed resource files
            pass
    
    # Caso 2: errori lettura file (nessuna risorsa generata)
    if not all_resources:
        return '<p style="color: #6b7280; font-style: italic;">Unable to read resource details.</p>'
    
    # ========================================
    # ORDINAMENTO: per tipo (kind) alfabetico crescente (A->Z)
    # ========================================
    all_resources.sort(key=lambda x: x['kind'])
    
    # Genera le righe HTML dalle risorse ordinate
    rows = []
    for res in all_resources:
        rows.append(f'''
            <tr>
                <td><span class="kind-badge" style="background: {res['color']};">{res['kind']}</span></td>
                <td><strong>{res['name']}</strong></td>
                <td>{res['namespace']}</td>
                <td><span class="missing-badge {res['location_class']}">{res['location']}</span></td>
            </tr>
        ''')
    
    # Caso 3: genera tabella HTML completa
    return f'''
        <table class="missing-table">
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Name</th>
                    <th>Namespace</th>
                    <th>Location</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    '''


# ============================================
# MAIN - Elaborazione Principale
# ============================================

def main():
    """
    Funzione principale: elabora summary.json e genera report dettagliato.
    
    Processo:
        1. Carica summary.json con lista risorse differenti
        2. Per ogni risorsa differente:
           - Appiattisce JSON di entrambi i cluster (flatten)
           - Confronta campo per campo
           - Aggrega differenze per top-level key
        3. Genera statistiche (top fields modificati)
        4. Produce output:
           - diff-details.md (Markdown)
           - diff-details.json (JSON)
           - diff-details.html (HTML interattivo)
    
    Args (da CLI):
        outdir: Directory output con summary.json e sottodirectory cluster
        --cluster1: Name primo cluster (default: "cluster1")
        --cluster2: Name secondo cluster (default: "cluster2")
    
    Exit codes:
        0: Successo
        2: summary.json non trovato
    
    Output files:
        - diff-details.md: Report Markdown testuale
        - diff-details.json: Dati strutturati per integrazione
        - diff-details.html: Report HTML interattivo con zoom/modal
    """
    
    # ========================================
    # 1. PARSING ARGOMENTI CLI
    # ========================================
    p = argparse.ArgumentParser()
    p.add_argument("outdir", help="Output directory where summary.json and cluster directories exist")
    p.add_argument('--cluster1', default='cluster1')
    p.add_argument('--cluster2', default='cluster2')
    args = p.parse_args()
    
    # ========================================
    # 2. VALIDAZIONE FILE INPUT
    # ========================================
    outdir = Path(args.outdir)
    summary_file = outdir / "summary.json"
    
    if not summary_file.exists():
        print(f"Summary not found: {summary_file}", file=sys.stderr)
        sys.exit(2)

    # Carica summary.json (contiene liste different/missing_in_1/missing_in_2)
    with open(summary_file) as fh:
        summary = json.load(fh)

    # Directory contenenti risorse normalizzate dei due cluster
    c1_dir = outdir / args.cluster1
    c2_dir = outdir / args.cluster2

    # ========================================
    # 3. INIZIALIZZAZIONE OUTPUT MARKDOWN
    # ========================================
    md_lines = []
    md_lines.append("# kdiff — Detailed field-level differences")
    md_lines.append(f"**Clusters:** {args.cluster1} vs {args.cluster2}")
    md_lines.append(f"Generated on: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    md_lines.append("\n**Legend:**")
    md_lines.append("- 🔄 Value changed")
    md_lines.append("- ➕ Added in {args.cluster2} (not in {args.cluster1})")
    md_lines.append("- ➖ Removed in {args.cluster2} (exists in {args.cluster1})")
    md_lines.append("- ❌ (not set) = field not present or null")
    md_lines.append("\n---\n")

    # ========================================
    # 4. INIZIALIZZAZIONE CONTATORI E STRUTTURE DATI
    # ========================================
    details = []          # Lista dettagli per ogni risorsa differente
    counts_top = {}       # Dizionario: top-level key → conteggio modifiche
    total_resources = 0   # Contatore risorse elaborate
    total_paths = 0       # Contatore totale campi modificati

    # ========================================
    # 5. ELABORAZIONE RISORSE DIFFERENTI
    # ========================================
    # Cicla su ogni risorsa marcata come "different" nel summary.json
    for entry in summary.get("different", []):
        total_resources += 1
        base = Path(entry).name  # Name file (es. "deployment__default__myapp.json")
        f1 = c1_dir / base
        f2 = c2_dir / base

        # ----------------------------------------
        # 5.1 Validazione File
        # ----------------------------------------
        # Se file mancante in un cluster: segnala e continua
        if not f1.exists() or not f2.exists():
            md_lines.append(f"### {base}\n")
            md_lines.append("**Skipping**: file missing in one cluster.\n")
            details.append({"file": base, "changed": []})
            continue

        # ----------------------------------------
        # 5.2 Caricamento Risorse JSON
        # ----------------------------------------
        with open(f1) as file1, open(f2) as file2:
            a = json.load(file1)  # Risorsa cluster1
            b = json.load(file2)  # Risorsa cluster2
        
        # Estrai metadati per identificazione
        kind = a.get('kind', 'Unknown')
        name = a.get('metadata', {}).get('name', 'unknown')
        color = get_kind_color(kind)
        
        # Aggiungi header risorsa al Markdown
        md_lines.append(f'### <span style="color: {color}; font-weight: bold;">Kind: {kind} | Name: {name}</span> <span style="color: #6b7280; font-size: 0.9em;">({base})</span>\n')
        
        # ----------------------------------------
        # 5.3 Appiattimento JSON (flatten)
        # ----------------------------------------
        # Converte JSON annidato in percorsi piatti (es. "spec.replicas": 3)
        fa = flatten(a)
        fb = flatten(b)
        
        # Unisci tutte le chiavi presenti in entrambi
        keys = sorted(set(fa.keys()) | set(fb.keys()))
        
        # ----------------------------------------
        # 5.4 Confronto Campo per Campo
        # ----------------------------------------
        changed = []  # Lista tuple: (percorso, valore_a, valore_b)
        
        for k in keys:
            va = fa.get(k, None)
            vb = fb.get(k, None)
            
            # Se valori differenti: registra modifica
            if va != vb:
                changed.append((k, va, vb))
                
                # Aggrega per top-level key (es. "spec", "metadata", etc)
                tk = top_key_for_path(k)
                counts_top[tk] = counts_top.get(tk, 0) + 1
        
        # ----------------------------------------
        # 5.5 Generazione Output Markdown
        # ----------------------------------------
        md_lines.append(f"**Changed paths:** {len(changed)}\n")
        
        if not changed:
            md_lines.append("No scalar differences detected.\n")
        else:
            # Tabella Markdown con 3 colonne
            md_lines.append(f"| Path | {args.cluster1} | {args.cluster2} |")
            md_lines.append("|---|---|---|")
            
            for pth, va, vb in changed:
                # Indicatori visivi per tipo modifica:
                # ➕ = Campo aggiunto in cluster2
                # ➖ = Campo rimosso in cluster2
                # 🔄 = Valore modificato
                if va is None and vb is not None:
                    indicator = "➕"
                elif va is not None and vb is None:
                    indicator = "➖"
                else:
                    indicator = "🔄"
                
                # Formatta riga tabella con valori abbreviati
                md_lines.append(f"| {indicator} `{pth}` | `{shortrepr(va)}` | `{shortrepr(vb)}` |")
        
        md_lines.append("\n")
        total_paths += len(changed)
        
        # Salva dettagli strutturati per JSON output
        details.append({
            "file": base,
            "changed": [{"path": p, "a": fa.get(p), "b": fb.get(p)} for (p, a, b) in changed]
        })

    # ========================================
    # 6. GENERAZIONE SUMMARY MARKDOWN
    # ========================================
    md_lines.append("\n---\n")
    md_lines.append("## Summary\n")
    md_lines.append(f"- **Total resources with differences:** {total_resources}")
    md_lines.append(f"- **Total changed scalar paths:** {total_paths}")
    md_lines.append(f"- **Average changes per resource:** {total_paths / total_resources if total_resources > 0 else 0:.1f}")
    
    # Tabella aggregata: top-level keys più modificati
    md_lines.append("\n## Aggregated top changed keys\n")
    md_lines.append("| Key | Approx. change count |")
    md_lines.append("|---:|---:|")
    for k, cnt in sorted(counts_top.items(), key=lambda x: x[1], reverse=True):
        md_lines.append(f"| {k} | {cnt} |")

    # ========================================
    # 7. SCRITTURA FILE OUTPUT
    # ========================================
    
    # 7.1 Salva Markdown Report (commentato - mantenere solo HTML)
    # md_text = "\n".join(md_lines)
    # (outdir / "diff-details.md").write_text(md_text, encoding="utf-8")

    # 7.2 Salva JSON Report (strutturato per integrazione)
    json_output = {
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "details": details,
        "counts_top": counts_top,
        "total_resources": total_resources,
        "total_paths": total_paths
    }
    (outdir / "diff-details.json").write_text(
        json.dumps(json_output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # 7.3 Genera HTML Report Interattivo (con CSS/JS)
    generate_html_report(
        outdir, summary, details, counts_top,
        total_resources, total_paths,
        args.cluster1, args.cluster2,
        c1_dir, c2_dir
    )

    print(f"Wrote detailed diff report: {outdir / 'diff-details.html'}")




# ============================================
# HTML REPORT GENERATOR - Report Interattivo
# ============================================

def generate_html_report(outdir, summary, details, counts_top, total_resources, total_paths, cluster1, cluster2, c1_dir, c2_dir):
    """
    Genera report HTML interattivo con CSS/JavaScript avanzato.
    
    Args:
        outdir: Directory output
        summary: Dizionario summary.json
        details: Lista dettagli risorse differenti
        counts_top: Dizionario conteggi per top-level key
        total_resources: Numero totale risorse con differenze
        total_paths: Numero totale campi modificati
        cluster1: Name primo cluster
        cluster2: Name secondo cluster
        c1_dir: Path directory cluster1
        c2_dir: Path directory cluster2
    
    Output:
        - diff-details.html: Report HTML interattivo con:
          * Dashboard with statistics colorate
          * Collapsible sections per Kind
          * Tabelle dettagliate per ogni risorsa
          * Modal popup per view diff con zoom
          * CSS gradient design (#667eea → #764ba2)
          * Badge colorati per tipo risorsa
          * Indicatori visivi (➕ ➖ 🔄)
          * Filtro per tipo modifica
          * Esportazione dati
    
    Features interattive:
        - Collapse/expand sezioni
        - View Diff modal con zoom +/-
        - Badge colorati per Kind
        - Legenda interattiva
        - Statistiche aggregate
        - Risorse solo in un cluster (missing table)
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # ========================================
    # 1. RAGGRUPPAMENTO RISORSE PER KIND
    # ========================================
    # Organizza risorse per tipo (Deployment, ConfigMap, etc)
    resources_by_kind = {}
    
    for detail in details:
        base = detail['file']
        changed = detail['changed']
        
        # Salta risorse senza differenze
        if not changed:
            continue
        
        # Estrai Kind, Name e Namespace dal file JSON
        try:
            f1 = c1_dir / base
            if f1.exists():
                with open(f1) as file:
                    obj = json.load(file)
                kind = obj.get('kind', 'Unknown')
                name = obj.get('metadata', {}).get('name', 'unknown')
                namespace = obj.get('metadata', {}).get('namespace', None)
            else:
                kind = 'Unknown'
                name = 'unknown'
                namespace = None
        except Exception:
            kind = 'Unknown'
            name = 'unknown'
            namespace = None
        
        # Inizializza lista per nuovo Kind
        if kind not in resources_by_kind:
            resources_by_kind[kind] = []
        
        # Aggiungi risorsa al gruppo
        resources_by_kind[kind].append({
            'base': base,
            'name': name,
            'kind': kind,
            'namespace': namespace,
            'changed': changed
        })
    
    # ========================================
    # 2. GENERAZIONE HTML PER OGNI KIND GROUP
    # ========================================
    kind_groups_html = []
    
    for kind in sorted(resources_by_kind.keys()):
        resources = resources_by_kind[kind]
        color = get_kind_color(kind)
        total_changes = sum(len(r['changed']) for r in resources)
        
        # ----------------------------------------
        # 2.1 Genera HTML per ogni risorsa del Kind
        # ----------------------------------------
        resources_html = []
        
        for resource in resources:
            base = resource['base']
            name = resource['name']
            namespace = resource.get('namespace')
            changed = resource['changed']
            
            # ----------------------------------------
            # 2.2 Genera righe tabella per ogni campo modificato
            # ----------------------------------------
            rows_html = []
            
            for item in changed:
                path = item['path']
                va = item.get('a')
                vb = item.get('b')
                
                # Determina tipo modifica e badge:
                # ➕ = Added in cluster2
                # ➖ = Removed in cluster2
                # 🔄 = Valore modificato
                if va is None and vb is not None:
                    icon = f'<span class="badge badge-add" title="Present in {cluster2}, not in {cluster1}">➕ Added</span>'
                    row_class = 'row-add'
                elif va is not None and vb is None:
                    icon = f'<span class="badge badge-remove" title="Present in {cluster1}, not in {cluster2}">➖ Removed</span>'
                    row_class = 'row-remove'
                else:
                    icon = '<span class="badge badge-change" title="Value modified between clusters">🔄 Changed</span>'
                    row_class = 'row-change'
                
                # Formatta valori con gestione newline e HTML escape
                if va is not None:
                    val_str = shortrepr(va)
                    # Converti \n in newline reali per pre-wrap CSS
                    val_a_html = html_lib.escape(val_str).replace('\\n', '\n')
                else:
                    # Valore null: mostra ❌ con tooltip
                    val_a_html = '<span class="null-value" title="Not set">❌</span>'
                
                if vb is not None:
                    val_str = shortrepr(vb)
                    val_b_html = html_lib.escape(val_str).replace('\\n', '\n')
                else:
                    val_b_html = '<span class="null-value" title="Not set">❌</span>'
                
                # Genera riga tabella HTML
                rows_html.append(f'''
                    <tr class="{row_class}">
                        <td class="col-icon">{icon}</td>
                        <td class="col-path"><code>{html_lib.escape(path)}</code></td>
                        <td class="col-value"><code>{val_a_html}</code></td>
                        <td class="col-value"><code>{val_b_html}</code></td>
                    </tr>
                ''')
            
            # ----------------------------------------
            # 2.3 Carica contenuto diff file per modal
            # ----------------------------------------
            diff_file = outdir / 'diffs' / f"{base}.diff"
            diff_content = ""
            
            if diff_file.exists():
                try:
                    diff_content = diff_file.read_text(encoding='utf-8')
                except Exception:
                    diff_content = "Error reading diff file"
            else:
                diff_content = "Diff file not found"
            
            # Encode base64 per evitare problemi HTML escaping
            import base64
            diff_content_base64 = base64.b64encode(diff_content.encode('utf-8')).decode('ascii')
            
            # ----------------------------------------
            # 2.3.1 Carica contenuti JSON per side-by-side diff
            # ----------------------------------------
            f1 = c1_dir / base
            f2 = c2_dir / base
            
            json1_content = ""
            json2_content = ""
            
            if f1.exists():
                try:
                    json1_content = f1.read_text(encoding='utf-8')
                except Exception:
                    json1_content = "Error reading file"
            else:
                json1_content = "File not found"
            
            if f2.exists():
                try:
                    json2_content = f2.read_text(encoding='utf-8')
                except Exception:
                    json2_content = "Error reading file"
            else:
                json2_content = "File not found"
            
            # Encode to base64 for HTML embedding
            json1_base64 = base64.b64encode(json1_content.encode('utf-8')).decode('ascii')
            json2_base64 = base64.b64encode(json2_content.encode('utf-8')).decode('ascii')
            
            # ----------------------------------------
            # 2.4 Genera HTML sezione risorsa (collapsabile)
            # ----------------------------------------
            # Prepara il namespace badge se disponibile con colore dinamico
            namespace_badge = ''
            if namespace:
                ns_color = get_namespace_color(namespace)
                namespace_badge = f'<span class="namespace-badge" style="background-color: {ns_color};">{html_lib.escape(namespace)}</span>'
            
            resources_html.append(f'''
                <div class="resource-section" id="resource-{base.replace('.', '-')}">
                    <div class="resource-header" style="border-left: 4px solid {color};">
                        <div style="flex: 1; cursor: pointer;" onclick="toggleResource('{base.replace('.', '-')}')">
                            <div class="resource-title">
                                <span class="toggle-icon-small" id="toggle-res-{base.replace('.', '-')}">▼</span>
                                <span class="resource-name">{name}</span>
                                {namespace_badge}
                            </div>
                        </div>
                        <div class="resource-stats">
                            <span class="info-icon" title="Number of JSON fields/paths modified in this resource (not the number of diff lines)">ⓘ</span>
                            <span class="stat-badge">
                                {len(changed)} changes
                            </span>
                            <button class="view-diff-btn" 
                                    data-diff-content="{diff_content_base64}"
                                    data-filename="{html_lib.escape(base)}"
                                    data-cluster1="{html_lib.escape(cluster1)}"
                                    data-cluster2="{html_lib.escape(cluster2)}"
                                    onclick="event.stopPropagation(); showDiffFromButton(this)">
                                View Diff
                            </button>
                            <button class="view-sidebyside-btn" 
                                    data-json1="{json1_base64}"
                                    data-json2="{json2_base64}"
                                    data-filename="{html_lib.escape(base)}"
                                    data-cluster1="{html_lib.escape(cluster1)}"
                                    data-cluster2="{html_lib.escape(cluster2)}"
                                    onclick="event.stopPropagation(); showSideBySideDiff(this)">
                                Side-by-Side
                            </button>
                        </div>
                    </div>
                    <div class="resource-body" id="res-body-{base.replace('.', '-')}">
                        <table class="diff-table">
                            <thead>
                                <tr>
                                    <th style="width: 100px;">Type</th>
                                    <th style="width: 30%;">Path</th>
                                    <th style="width: 35%;">{cluster1}</th>
                                    <th style="width: 35%;">{cluster2}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(rows_html)}
                            </tbody>
                        </table>
                    </div>
                </div>
            ''')
        
        # ----------------------------------------
        # 2.5 Genera gruppo Kind collapsabile
        # ----------------------------------------
        # Ogni Kind (Deployment, ConfigMap, etc) ha sezione collassabile
        kind_id = kind.lower().replace(' ', '-')
        kind_groups_html.append(f'''
            <div class="kind-group" data-kind="{kind_id}">
                <div class="kind-header" style="border-left: 4px solid {color};">
                    <div class="kind-title" onclick="toggleKind('{kind_id}')" style="cursor: pointer; flex: 1;">
                        <span class="toggle-icon collapsed" id="toggle-{kind_id}">▶</span>
                        <span class="kind-badge" style="background: {color};">{kind}</span>
                        <span class="kind-count">{len(resources)} resource{'s' if len(resources) > 1 else ''}</span>
                    </div>
                    <div class="kind-stats" style="display: flex; gap: 10px; align-items: center;">
                        <span class="stat-badge">{total_changes} total changes</span>
                        <button onclick="event.stopPropagation(); toggleKindResources('{kind_id}')" 
                                style="padding: 3px 6px; background: #667eea; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 0.75em; font-weight: 600; white-space: nowrap;"
                                title="Expand/Collapse all resources in this group">
                            +/−
                        </button>
                    </div>
                </div>
                <div class="kind-body collapsed" id="kind-body-{kind_id}">
                    {''.join(resources_html)}
                </div>
            </div>
        ''')
    
    # ========================================
    # 3. GENERAZIONE TABELLA TOP CHANGED KEYS
    # ========================================
    # Barra progressiva per visualizzare top-level keys più modificati
    top_keys_rows = []
    
    for k, cnt in sorted(counts_top.items(), key=lambda x: x[1], reverse=True)[:15]:
        # Calcola larghezza barra proporzionale al max
        bar_width = int((cnt / max(counts_top.values())) * 100) if counts_top else 0
        
        top_keys_rows.append(f'''
            <tr>
                <td><strong>{html_lib.escape(k)}</strong></td>
                <td>
                    <div class="bar-container">
                        <div class="bar" style="width: {bar_width}%;"></div>
                        <span class="bar-label">{cnt}</span>
                    </div>
                </td>
            </tr>
        ''')
    
    # ========================================
    # 4. ASSEMBLAGGIO HTML COMPLETO
    # ========================================
    # Template HTML con CSS embedded e JavaScript per interattività
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>kdiff - Detailed Comparison Report</title>
    
    <!-- jsdiff library for robust diff algorithm -->
    <script src="https://cdn.jsdelivr.net/npm/diff@5.1.0/dist/diff.min.js"></script>
    
    <style>
        /* =====================================
           CSS RESET E STILI BASE
           ===================================== */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            /* Gradient viola-blu di sfondo */
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1f2937;
            line-height: 1.6;
            padding: 20px;
        }}
        
        /* Search input styling */
        #resourceSearch {{
            font-family: inherit;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        #resourceSearch:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2), 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        #clearSearch {{
            transition: all 0.2s ease;
        }}
        
        #clearSearch:hover {{
            background: #dc2626;
            transform: scale(1.05);
        }}
        
        /* Search highlight style */
        .search-highlight {{
            background: #ffeb3b;
            color: #000;
            font-weight: 600;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        
        /* Container principale bianco con ombra */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        /* =====================================
           HEADER - Intestazione con Gradient
           ===================================== */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }}
        
        /* Logo kdiff */
        .header-logo {{
            display: inline-block;
            margin-bottom: 20px;
            transition: transform 0.3s ease, opacity 0.3s ease;
        }}
        
        .header-logo:hover {{
            transform: scale(1.05);
            opacity: 0.9;
        }}
        
        .header-logo img {{
            height: 80px;
            width: auto;
            filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.2));
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.95;
            margin-bottom: 20px;
        }}
        
        .header .metadata {{
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .header .metadata-item {{
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        
        /* =====================================
           STATS GRID - Dashboard Statistiche
           ===================================== */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f9fafb;
        }}
        
        /* Card statistiche con hover effect */
        .stat-card {{
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        /* Colori bordo sinistro per tipo card */
        .stat-card.resources {{ border-left-color: #3b82f6; }}  /* Blu */
        .stat-card.changes {{ border-left-color: #f59e0b; }}    /* Arancione */
        .stat-card.missing {{ 
            border-left-color: #dc2626; 
            cursor: pointer;
            position: relative;
        }}  /* Rosso */
        .stat-card.missing:hover {{ 
            background: #fef2f2;
            transform: translateY(-4px);
            box-shadow: 0 6px 16px rgba(220, 38, 38, 0.2);
            border-left-width: 6px;
        }}
        .stat-card.missing::after {{
            content: '';
            position: absolute;
            top: 20px;
            right: 20px;
            width: 24px;
            height: 24px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23dc2626' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z'%3E%3C/path%3E%3Ccircle cx='12' cy='12' r='3'%3E%3C/circle%3E%3C/svg%3E");
            background-size: contain;
            background-repeat: no-repeat;
            opacity: 0.5;
            transition: all 0.3s;
        }}
        .stat-card.missing:hover::after {{
            opacity: 1;
            transform: scale(1.15);
        }}
        
        .stat-card .stat-label {{
            font-size: 0.9em;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        .stat-card.missing .stat-label {{
            padding-right: 40px;
        }}
        .stat-card .stat-hint {{
            font-size: 0.75em;
            color: #9ca3af;
            margin-top: 8px;
            font-weight: 400;
            font-style: italic;
        }}
        .stat-card.missing .stat-hint {{
            transition: color 0.3s;
        }}
        .stat-card.missing:hover .stat-hint {{
            color: #dc2626;
            font-weight: 500;
        }}
        
        /* Valore numerico con gradient text */
        .stat-card .stat-value {{
            font-size: 2.5em;
            font-weight: 700;
            margin: 10px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        /* =====================================
           CONTENT - Contenuto Principale
           ===================================== */
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            font-weight: 700;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            color: #111827;
        }}
        
        /* =====================================
           LEGEND - Legenda Interattiva
           ===================================== */
        .legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 20px 25px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border-left: 4px solid;
        }}
        
        .legend-item:nth-child(1) {{
            border-left-color: #3b82f6;
        }}
        
        .legend-item:nth-child(2) {{
            border-left-color: #10b981;
        }}
        
        .legend-item:nth-child(3) {{
            border-left-color: #ef4444;
        }}
        
        .legend-item:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        }}
        
        .legend-item .badge {{
            font-size: 1.8em;
            min-width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
        }}
        
        .legend-item .legend-text {{
            flex: 1;
        }}
        
        .legend-item .legend-title {{
            font-weight: 700;
            font-size: 1.1em;
            color: #111827;
            margin-bottom: 4px;
        }}
        
        .legend-item .legend-description {{
            font-size: 0.9em;
            color: #6b7280;
            line-height: 1.4;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            cursor: help;
        }}
        
        .null-value {{
            color: #9ca3af;
            font-size: 1.2em;
            cursor: help;
            display: inline-block;
            transition: transform 0.2s;
        }}
        
        .null-value:hover {{
            transform: scale(1.3);
        }}
        
        .badge-add {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .badge-remove {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .badge-change {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .kind-group {{
            margin-bottom: 30px;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .kind-header {{
            padding: 20px 25px;
            background: linear-gradient(to right, #f9fafb 0%, white 100%);
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .kind-header:hover {{
            background: linear-gradient(to right, #f3f4f6 0%, #f9fafb 100%);
        }}
        
        .kind-title {{
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 1.3em;
            font-weight: 600;
        }}
        
        .toggle-icon {{
            font-size: 0.8em;
            transition: transform 0.3s;
            color: #6b7280;
        }}
        
        .toggle-icon.collapsed {{
            transform: rotate(-90deg);
        }}
        
        .kind-count {{
            color: #6b7280;
            font-size: 0.8em;
            font-weight: 500;
        }}
        
        .kind-stats {{
            display: flex;
            gap: 10px;
        }}
        
        .kind-body {{
            padding: 20px;
            background: #fafbfc;
            max-height: 10000px;
            overflow: hidden;
            transition: max-height 0.4s ease-in-out, padding 0.3s ease;
        }}
        
        .kind-body.collapsed {{
            max-height: 0;
            padding: 0 20px;
        }}
        
        .resource-section {{
            margin-bottom: 20px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }}
        
        .resource-header {{
            padding: 20px;
            background: linear-gradient(to right, #f9fafb 0%, white 100%);
            border-bottom: 2px solid #e5e7eb;
            display: flex;
            align-items: center;
            gap: 20px;
            user-select: none;
            transition: background 0.2s;
        }}
        
        .resource-header:hover {{
            background: linear-gradient(to right, #f3f4f6 0%, #f9fafb 100%);
        }}
        
        .resource-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}
        
        .toggle-icon-small {{
            font-size: 0.7em;
            transition: transform 0.3s;
            color: #6b7280;
        }}
        
        .toggle-icon-small.collapsed {{
            transform: rotate(-90deg);
        }}
        
        .kind-badge {{
            padding: 6px 14px;
            border-radius: 6px;
            color: white;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .resource-name {{
            font-size: 1.3em;
            font-weight: 600;
            color: #111827;
        }}
        
        .namespace-badge {{
            display: inline-block;
            margin-left: 12px;
            padding: 4px 12px;
            color: white;
            font-size: 0.75em;
            font-weight: 500;
            border-radius: 12px;
            text-transform: lowercase;
            letter-spacing: 0.3px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .namespace-badge:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        
        .resource-file {{
            font-size: 0.9em;
            color: #6b7280;
            font-family: 'Monaco', 'Courier New', monospace;
            margin-bottom: 8px;
        }}
        
        .resource-stats {{
            display: flex;
            gap: 10px;
        }}
        
        .stat-badge {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .info-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-size: 16px;
            cursor: help;
            transition: all 0.2s ease;
        }}
        
        .info-icon:hover {{
            color: #667eea;
            transform: scale(1.2);
        }}
        
        .view-diff-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .view-diff-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .view-diff-btn:active {{
            transform: translateY(0);
        }}
        
        .view-sidebyside-btn {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .view-sidebyside-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }}
        
        .view-sidebyside-btn:active {{
            transform: translateY(0);
        }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
        }}
        
        .modal-content {{
            background-color: #1e1e1e;
            margin: 3% auto;
            padding: 0;
            border-radius: 12px;
            width: 90%;
            max-width: 1200px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: slideDown 0.3s ease;
        }}
        
        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-50px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .modal-title {{
            font-size: 1.3em;
            font-weight: 600;
            flex: 1;
        }}
        
        .zoom-controls {{
            display: flex;
            gap: 10px;
            margin-right: 20px;
        }}
        
        .zoom-btn {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.5);
            width: 36px;
            height: 36px;
            border-radius: 6px;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .zoom-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            border-color: white;
            transform: scale(1.1);
        }}
        
        .zoom-btn:active {{
            transform: scale(0.95);
        }}
        
        .close {{
            color: white;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            line-height: 1;
        }}
        
        .close:hover {{
            transform: scale(1.2);
        }}
        
        .modal-body {{
            padding: 30px;
            background: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 70vh;
            overflow-y: auto;
            border-radius: 0 0 12px 12px;
        }}
        
        .diff-line {{
            white-space: pre-wrap;
            padding: 2px 10px;
            line-height: 1.6;
        }}
        
        .diff-line[title] {{
            cursor: help;
        }}
        
        .diff-add {{
            background-color: rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
        }}
        
        .diff-remove {{
            background-color: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
        }}
        
        .diff-context {{
            color: #9ca3af;
        }}
        
        .diff-header {{
            color: #60a5fa;
            font-weight: bold;
        }}
        
        .resource-body {{
            padding: 0;
            max-height: 5000px;
            overflow: hidden;
            transition: max-height 0.4s ease-in-out;
        }}
        
        .resource-body.collapsed {{
            max-height: 0;
        }}
        
        .missing-resources-section {{
            display: none;
            margin-top: 20px;
            padding: 30px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .missing-resources-section.visible {{
            display: block;
        }}
        
        .missing-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .missing-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .missing-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
        }}
        
        .missing-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .missing-table tbody tr:hover {{
            background: #f9fafb;
        }}
        
        .missing-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .missing-in-c1 {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .missing-in-c2 {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .diff-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .diff-table thead {{
            background: #f3f4f6;
        }}
        
        .diff-table th {{
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #d1d5db;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .diff-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
        }}
        
        .diff-table tbody tr:hover {{
            background: #f9fafb;
        }}
        
        .row-add {{
            background: rgba(209, 250, 229, 0.3);
        }}
        
        .row-remove {{
            background: rgba(254, 226, 226, 0.3);
        }}
        
        .row-change {{
            background: rgba(219, 234, 254, 0.3);
        }}
        
        .col-icon {{
            width: 100px;
        }}
        
        .col-path code {{
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            color: #6366f1;
            font-weight: 500;
        }}
        
        .col-value code {{
            display: block;
            background: #f9fafb;
            padding: 8px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
            color: #111827;
            word-break: break-word;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}
        
        .null-value {{
            color: #9ca3af;
            font-style: italic;
        }}
        
        .top-keys-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .top-keys-table td {{
            padding: 12px 20px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .top-keys-table tr:hover {{
            background: #f9fafb;
        }}
        
        .bar-container {{
            position: relative;
            height: 30px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .bar {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
        }}
        
        .bar-label {{
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            font-weight: 600;
            color: #111827;
            z-index: 1;
        }}
        
        .footer {{
            background: #f9fafb;
            padding: 30px;
            text-align: center;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }}
        
        /* =====================================
           SIDE-BY-SIDE DIFF MODAL STYLES
           ===================================== */
        .sidebyside-modal-content {{
            background-color: #1e1e1e;
            margin: 2% auto;
            padding: 0;
            border-radius: 12px;
            width: 95%;
            max-width: 1800px;
            height: 90vh;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: slideDown 0.3s ease;
            display: flex;
            flex-direction: column;
        }}
        
        .sidebyside-modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .zoom-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        
        .zoom-btn {{
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            font-size: 16px;
            min-width: 36px;
        }}
        
        .zoom-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .sidebyside-container {{
            display: flex;
            flex-direction: row;
            flex: 1;
            min-height: 0;
            overflow: hidden;
        }}
        
        .sidebyside-pane {{
            width: 50%;
            min-width: 0;
            display: flex;
            flex-direction: column;
            border-right: 2px solid #3d3d3d;
            background: #1e1e1e;
        }}
        
        .sidebyside-pane:last-child {{
            border-right: none;
        }}
        
        .sidebyside-pane-header {{
            background: #2d2d2d;
            color: #cccccc;
            padding: 12px 20px;
            font-weight: 600;
            border-bottom: 1px solid #3d3d3d;
            font-size: 0.9em;
        }}
        
        .sidebyside-pane-header.cluster1 {{
            background: #2d3748;
            color: #90cdf4;
        }}
        
        .sidebyside-pane-header.cluster2 {{
            background: #2d3a2d;
            color: #9ae6b4;
        }}
        
        .sidebyside-pane-content {{
            flex: 1;
            overflow-y: auto;
            overflow-x: auto;
            padding: 0;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            line-height: 1.6;
            background: #1e1e1e;
            min-height: 0;
        }}
        
        .code-line {{
            padding: 0 20px;
            min-height: 20px;
            display: flex;
            align-items: flex-start;
        }}
        
        .code-line-number {{
            display: inline-block;
            width: 50px;
            color: #858585;
            text-align: right;
            padding-right: 15px;
            padding-top: 0;
            user-select: none;
            flex-shrink: 0;
        }}
        
        .code-line-content {{
            color: #d4d4d4;
            white-space: pre-wrap;
            word-wrap: break-word;
            flex: 1;
        }}
        
        .code-line.added {{
            background: rgba(16, 185, 129, 0.15);
        }}
        
        .code-line.added .code-line-content {{
            background: rgba(16, 185, 129, 0.25);
        }}
        
        .code-line.removed {{
            background: rgba(239, 68, 68, 0.15);
        }}
        
        .code-line.removed .code-line-content {{
            background: rgba(239, 68, 68, 0.25);
        }}
        
        .code-line.modified {{
            background: rgba(59, 130, 246, 0.15);
        }}
        
        .code-line.modified .code-line-content {{
            background: rgba(59, 130, 246, 0.25);
        }}
        
        /* Inline diff highlighting within modified lines */
        .inline-diff-highlight {{
            background: rgba(251, 191, 36, 0.5);
            border-radius: 2px;
            padding: 1px 0;
            font-weight: 600;
            box-shadow: 0 0 0 1px rgba(251, 191, 36, 0.3);
        }}
        
        /* Filter box hover effect */
        .filter-box {{
            transition: all 0.2s ease;
        }}
        
        #filterLabelAdded:hover .filter-box,
        #filterLabelRemoved:hover .filter-box,
        #filterLabelModified:hover .filter-box,
        #filterLabelUnchanged:hover .filter-box {{
            transform: scale(1.1);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }}
        
        /* Disabled filter labels */
        [id^="filterLabel"][style*="opacity: 0.3"] {{
            pointer-events: none;
        }}
        
        [id^="filterLabel"][style*="opacity: 0.3"]:hover .filter-box {{
            transform: none;
            box-shadow: none;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
    <script>
        /* =====================================
           JAVASCRIPT - Interattività Report
           =====================================
           
           Funzioni principali:
           - Zoom in/out del diff modal
           - Apertura/chiusura modal diff
           - Toggle collapse/expand sezioni
           - Toggle missing resources section
           
           ===================================== */
        
        // ========================================
        // ZOOM CONTROLS - Modal Zoom Controls
        // ========================================
        let currentFontSize = 14;
        
        function zoomIn() {{
            currentFontSize += 2;
            document.getElementById('modalBody').style.fontSize = currentFontSize + 'px';
        }}
        
        function zoomOut() {{
            if (currentFontSize > 8) {{
                currentFontSize -= 2;
                document.getElementById('modalBody').style.fontSize = currentFontSize + 'px';
            }}
        }}
        
        function resetZoom() {{
            currentFontSize = 14;
            document.getElementById('modalBody').style.fontSize = currentFontSize + 'px';
        }}
        
        // ========================================
        // DIFF MODAL - View Diff Popup
        // ========================================
        
        // Show diff modal from button (decodifica base64)
        function showDiffFromButton(button) {{
            const base64Content = button.getAttribute('data-diff-content');
            const filename = button.getAttribute('data-filename');
            const cluster1 = button.getAttribute('data-cluster1');
            const cluster2 = button.getAttribute('data-cluster2');
            
            // Decode base64 diff content
            const diffContent = atob(base64Content);
            showDiff(diffContent, filename, cluster1, cluster2);
        }}
        
        // Show diff modal with color formatting
        function showDiff(diffContent, filename, cluster1, cluster2) {{
            const modal = document.getElementById('diffModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            
            modalTitle.textContent = filename;
            
            // ========================================
            // Format diff with colors by line type:
            // - Header (+++/---/@@): grigio
            // - Additions (+): verde
            // - Removals (-): rosso
            // - Context: nero
            // ========================================
            const lines = diffContent.split('\\n');
            let formattedHtml = '';
            
            for (const line of lines) {{
                // Determine CSS class based on first character
                let className = 'diff-context';
                let tooltip = '';
                
                if (line.startsWith('+++') || line.startsWith('---') || line.startsWith('@@')) {{
                    className = 'diff-header';
                }} else if (line.startsWith('+')) {{
                    className = 'diff-add';
                    tooltip = cluster2 || 'Cluster 2';  // Righe verdi = cluster2
                }} else if (line.startsWith('-')) {{
                    className = 'diff-remove';
                    tooltip = cluster1 || 'Cluster 1';  // Righe rosse = cluster1
                }}
                
                // Escape HTML to prevent XSS
                const escapedLine = line
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
                
                // Converti \\n letterali in newline reali per leggibilità
                const formattedLine = escapedLine.replace(/\\\\n/g, '\\n');
                
                // Genera div colorato per riga con tooltip se presente
                const titleAttr = tooltip ? ` title="${{tooltip}}"` : '';
                formattedHtml += `<div class="diff-line ${{className}}"${{titleAttr}}>${{formattedLine || '&nbsp;'}}</div>`;
            }}
            
            modalBody.innerHTML = formattedHtml;
            modal.style.display = 'block';
        }}
        
        // Close diff modal
        function closeDiffModal() {{
            const modal = document.getElementById('diffModal');
            const sideBySideModal = document.getElementById('sideBySideModal');
            if (modal) modal.style.display = 'none';
            if (sideBySideModal) sideBySideModal.style.display = 'none';
        }}
        
        // ========================================
        // SIDE-BY-SIDE DIFF - Full File Comparison
        // ========================================
        
        let sideBySideFontSize = 13;
        
        function zoomInSideBySide() {{
            sideBySideFontSize += 2;
            applySideBySideZoom();
        }}
        
        function zoomOutSideBySide() {{
            if (sideBySideFontSize > 8) {{
                sideBySideFontSize -= 2;
                applySideBySideZoom();
            }}
        }}
        
        function resetZoomSideBySide() {{
            sideBySideFontSize = 13;
            applySideBySideZoom();
        }}
        
        function applySideBySideZoom() {{
            document.getElementById('sideBySideLeftPane').style.fontSize = sideBySideFontSize + 'px';
            document.getElementById('sideBySideRightPane').style.fontSize = sideBySideFontSize + 'px';
        }}
        
        function showSideBySideDiff(button) {{
            const json1Base64 = button.getAttribute('data-json1');
            const json2Base64 = button.getAttribute('data-json2');
            const filename = button.getAttribute('data-filename');
            const cluster1 = button.getAttribute('data-cluster1');
            const cluster2 = button.getAttribute('data-cluster2');
            
            // Decode base64 JSON content
            const json1Raw = atob(json1Base64);
            const json2Raw = atob(json2Base64);
            
            // Parse and pretty-print JSON, then expand \\n sequences
            let json1Pretty, json2Pretty;
            try {{
                const obj1 = JSON.parse(json1Raw);
                json1Pretty = JSON.stringify(obj1, null, 2);
                // Replace literal \\n with actual newlines BEFORE splitting
                json1Pretty = json1Pretty.replace(/\\\\n/g, '\\n');
            }} catch(e) {{
                json1Pretty = json1Raw; // Use raw if parsing fails
            }}
            
            try {{
                const obj2 = JSON.parse(json2Raw);
                json2Pretty = JSON.stringify(obj2, null, 2);
                // Replace literal \\n with actual newlines BEFORE splitting
                json2Pretty = json2Pretty.replace(/\\\\n/g, '\\n');
            }} catch(e) {{
                json2Pretty = json2Raw; // Use raw if parsing fails
            }}
            
            // Show modal
            const modal = document.getElementById('sideBySideModal');
            const modalTitle = document.getElementById('sideBySideModalTitle');
            const leftPane = document.getElementById('sideBySideLeftPane');
            const rightPane = document.getElementById('sideBySideRightPane');
            const leftHeader = document.getElementById('sideBySideLeftHeader');
            const rightHeader = document.getElementById('sideBySideRightHeader');
            
            modalTitle.textContent = filename;
            leftHeader.textContent = cluster1;
            rightHeader.textContent = cluster2;
            
            // NOW split into lines for comparison (after \\n expansion)
            const lines1 = json1Pretty.split('\\n');
            const lines2 = json2Pretty.split('\\n');
            
            // Compute line-by-line diff
            const diff = computeLineDiff(lines1, lines2);
            
            // Render both panes with diff highlighting
            leftPane.innerHTML = renderDiffContent(diff, 'left');
            rightPane.innerHTML = renderDiffContent(diff, 'right');
            
            // Detect which line types are present in the diff
            detectAndDisableFilters(diff);
            
            // Apply current zoom level
            applySideBySideZoom();
            
            // Sync scrolling between panes
            syncPaneScrolling('sideBySideLeftPane', 'sideBySideRightPane');
            
            modal.style.display = 'block';
        }}
        
        function detectAndDisableFilters(diff) {{
            // Count each type of line
            const hasAdded = diff.some(item => item.type === 'added');
            const hasRemoved = diff.some(item => item.type === 'removed');
            const hasModified = diff.some(item => item.type === 'modified');
            const hasUnchanged = diff.some(item => item.type === 'unchanged');
            
            // Enable/disable filters based on presence
            updateFilterAvailability('added', hasAdded);
            updateFilterAvailability('removed', hasRemoved);
            updateFilterAvailability('modified', hasModified);
            updateFilterAvailability('unchanged', hasUnchanged);
        }}
        
        function updateFilterAvailability(filterType, isAvailable) {{
            const capitalizedType = filterType.charAt(0).toUpperCase() + filterType.slice(1);
            const label = document.getElementById('filterLabel' + capitalizedType);
            const box = document.getElementById('filterBox' + capitalizedType);
            
            if (!label || !box) return;
            
            if (!isAvailable) {{
                // Disable the filter
                label.style.opacity = '0.3';
                label.style.cursor = 'not-allowed';
                label.onclick = null;
                box.style.opacity = '0.3';
                
                // Uncheck if it was checked
                if (sideBySideFilters[filterType]) {{
                    sideBySideFilters[filterType] = false;
                    box.innerHTML = '';
                    box.style.borderWidth = '2px';
                }}
            }} else {{
                // Enable the filter
                label.style.opacity = '1';
                label.style.cursor = 'pointer';
                label.onclick = () => toggleSideBySideFilter(filterType);
                box.style.opacity = '1';
            }}
        }}
        
        function computeLineDiff(lines1, lines2) {{
            // Use jsdiff library for robust diff computation
            const text1 = lines1.join('\\n');
            const text2 = lines2.join('\\n');
            
            // Get line-based diff using jsdiff
            const changes = Diff.diffLines(text1, text2);
            
            // Convert jsdiff output to our format with smart merging
            const diff = [];
            let lineNum1 = 1;
            let lineNum2 = 1;
            
            for (let i = 0; i < changes.length; i++) {{
                const change = changes[i];
                const nextChange = i + 1 < changes.length ? changes[i + 1] : null;
                
                const lines = change.value.split('\\n');
                if (lines[lines.length - 1] === '') {{
                    lines.pop();
                }}
                
                // Check if this is a removed block followed by an added block
                if (change.removed && nextChange && nextChange.added) {{
                    const removedLines = lines;
                    const addedLines = nextChange.value.split('\\n');
                    if (addedLines[addedLines.length - 1] === '') {{
                        addedLines.pop();
                    }}
                    
                    const maxLen = Math.max(removedLines.length, addedLines.length);
                    
                    for (let j = 0; j < maxLen; j++) {{
                        const line1 = j < removedLines.length ? removedLines[j] : null;
                        const line2 = j < addedLines.length ? addedLines[j] : null;
                        
                        if (line1 !== null && line2 !== null) {{
                            // Both sides have content - modified
                            diff.push({{
                                type: 'modified',
                                line1: line1,
                                line2: line2,
                                lineNum1: lineNum1++,
                                lineNum2: lineNum2++
                            }});
                        }} else if (line1 !== null) {{
                            // Only removed side
                            diff.push({{
                                type: 'removed',
                                line1: line1,
                                line2: null,
                                lineNum1: lineNum1++,
                                lineNum2: null
                            }});
                        }} else {{
                            // Only added side
                            diff.push({{
                                type: 'added',
                                line1: null,
                                line2: line2,
                                lineNum1: null,
                                lineNum2: lineNum2++
                            }});
                        }}
                    }}
                    
                    i++; // Skip next change since we processed it
                }} else if (change.added) {{
                    lines.forEach((line) => {{
                        diff.push({{
                            type: 'added',
                            line1: null,
                            line2: line,
                            lineNum1: null,
                            lineNum2: lineNum2++
                        }});
                    }});
                }} else if (change.removed) {{
                    lines.forEach((line) => {{
                        diff.push({{
                            type: 'removed',
                            line1: line,
                            line2: null,
                            lineNum1: lineNum1++,
                            lineNum2: null
                        }});
                    }});
                }} else {{
                    lines.forEach((line) => {{
                        diff.push({{
                            type: 'unchanged',
                            line1: line,
                            line2: line,
                            lineNum1: lineNum1++,
                            lineNum2: lineNum2++
                        }});
                    }});
                }}
            }}
            
            return diff;
        }}
        
        function renderDiffContent(diff, side) {{
            let html = '';
            
            diff.forEach((item) => {{
                const lineNum = side === 'left' ? item.lineNum1 : item.lineNum2;
                const lineContent = side === 'left' ? item.line1 : item.line2;
                
                let cssClass = '';
                
                if (lineContent === null) {{
                    // Empty placeholder for alignment
                    html += '<div class="code-line empty-placeholder" style="background: #2d2d2d; opacity: 0.3;">' +
                                '<span class="code-line-number"></span>' +
                                '<span class="code-line-content">&nbsp;</span>' +
                             '</div>';
                }} else {{
                    // Determine CSS class based on diff type and side
                    if (item.type === 'added' && side === 'right') {{
                        cssClass = 'added';
                    }} else if (item.type === 'removed' && side === 'left') {{
                        cssClass = 'removed';
                    }} else if (item.type === 'modified') {{
                        cssClass = 'modified';
                    }}
                    
                    let contentHtml;
                    
                    // For modified lines, highlight the specific differences
                    if (item.type === 'modified' && item.line1 && item.line2) {{
                        contentHtml = highlightInlineDiff(item.line1, item.line2, side);
                    }} else {{
                        // Escape HTML for non-modified lines
                        contentHtml = lineContent
                            .replace(/&/g, '&amp;')
                            .replace(/</g, '&lt;')
                            .replace(/>/g, '&gt;')
                            .replace(/"/g, '&quot;')
                            .replace(/'/g, '&#039;');
                    }}
                    
                    html += '<div class="code-line ' + cssClass + '">' +
                                '<span class="code-line-number">' + (lineNum || '') + '</span>' +
                                '<span class="code-line-content">' + contentHtml + '</span>' +
                             '</div>';
                }}
            }});
            
            return html;
        }}
        
        function highlightInlineDiff(line1, line2, side) {{
            const lineToShow = side === 'left' ? line1 : line2;
            const otherLine = side === 'left' ? line2 : line1;
            
            // Use character-level diff to find exact differences
            const charDiff = Diff.diffChars(line1, line2);
            
            let html = '';
            let currentIndex = 0;
            
            charDiff.forEach((part) => {{
                const value = part.value;
                
                // Escape HTML
                const escaped = value
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
                
                if (side === 'left' && part.removed) {{
                    // Highlight removed parts on left side
                    html += '<mark class="inline-diff-highlight">' + escaped + '</mark>';
                }} else if (side === 'right' && part.added) {{
                    // Highlight added parts on right side
                    html += '<mark class="inline-diff-highlight">' + escaped + '</mark>';
                }} else if (!part.added && !part.removed) {{
                    // Unchanged parts - no highlight
                    html += escaped;
                }}
                // Skip parts that don't belong to this side (added on left, removed on right)
            }});
            
            return html;
        }}
        
        // Track which filters are active (none by default)
        const sideBySideFilters = {{
            added: false,
            removed: false,
            modified: false,
            unchanged: false
        }};
        
        function toggleSideBySideFilter(filterType) {{
            // Toggle the filter state
            sideBySideFilters[filterType] = !sideBySideFilters[filterType];
            
            // Update visual indicator (checkmark)
            const box = document.getElementById('filterBox' + filterType.charAt(0).toUpperCase() + filterType.slice(1));
            if (sideBySideFilters[filterType]) {{
                // Show checkmark
                box.innerHTML = '<span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 14px; font-weight: bold; color: #1f2937;">✓</span>';
                box.style.borderWidth = '3px';
            }} else {{
                // Remove checkmark
                box.innerHTML = '';
                box.style.borderWidth = '2px';
            }}
            
            // Apply filter
            applySideBySideFilter();
        }}
        
        function applySideBySideFilter() {{
            const leftPane = document.getElementById('sideBySideLeftPane');
            const rightPane = document.getElementById('sideBySideRightPane');
            
            if (!leftPane || !rightPane) return;
            
            // Check if any filter is active
            const anyFilterActive = Object.values(sideBySideFilters).some(v => v === true);
            
            const leftLines = leftPane.querySelectorAll('.code-line');
            const rightLines = rightPane.querySelectorAll('.code-line');
            
            // If no filters active, show all lines
            if (!anyFilterActive) {{
                leftLines.forEach(line => {{ line.style.display = ''; }});
                rightLines.forEach(line => {{ line.style.display = ''; }});
                return;
            }}
            
            // Check if added or removed filters are active (empty lines needed for alignment)
            const showEmptyLines = sideBySideFilters.added || sideBySideFilters.removed;
            
            // Otherwise, show only lines matching active filters (OR logic)
            leftLines.forEach((line) => {{
                const isAdded = line.classList.contains('added');
                const isRemoved = line.classList.contains('removed');
                const isModified = line.classList.contains('modified');
                const isEmpty = line.classList.contains('empty-placeholder');
                const isUnchanged = !isAdded && !isRemoved && !isModified && !isEmpty;
                
                let shouldShow = false;
                if (isAdded && sideBySideFilters.added) shouldShow = true;
                if (isRemoved && sideBySideFilters.removed) shouldShow = true;
                if (isModified && sideBySideFilters.modified) shouldShow = true;
                if (isUnchanged && sideBySideFilters.unchanged) shouldShow = true;
                
                // Show empty placeholders ONLY when added or removed filters are active
                if (isEmpty && showEmptyLines) {{
                    shouldShow = true;
                }}
                
                line.style.display = shouldShow ? '' : 'none';
            }});
            
            rightLines.forEach((line) => {{
                const isAdded = line.classList.contains('added');
                const isRemoved = line.classList.contains('removed');
                const isModified = line.classList.contains('modified');
                const isEmpty = line.classList.contains('empty-placeholder');
                const isUnchanged = !isAdded && !isRemoved && !isModified && !isEmpty;
                
                let shouldShow = false;
                if (isAdded && sideBySideFilters.added) shouldShow = true;
                if (isRemoved && sideBySideFilters.removed) shouldShow = true;
                if (isModified && sideBySideFilters.modified) shouldShow = true;
                if (isUnchanged && sideBySideFilters.unchanged) shouldShow = true;
                
                // Show empty placeholders ONLY when added or removed filters are active
                if (isEmpty && showEmptyLines) {{
                    shouldShow = true;
                }}
                
                line.style.display = shouldShow ? '' : 'none';
            }});
        }}
        
        function resetSideBySideFilter() {{
            // Uncheck all filters
            sideBySideFilters.added = false;
            sideBySideFilters.removed = false;
            sideBySideFilters.modified = false;
            sideBySideFilters.unchanged = false;
            
            // Remove all checkmarks
            ['Added', 'Removed', 'Modified', 'Unchanged'].forEach(type => {{
                const box = document.getElementById('filterBox' + type);
                if (box) {{
                    box.innerHTML = '';
                    box.style.borderWidth = '2px';
                }}
            }});
            
            // Apply filter (will show all lines since no filter is active)
            applySideBySideFilter();
        }}
        
        function syncPaneScrolling(leftPaneId, rightPaneId) {{
            const leftPane = document.getElementById(leftPaneId);
            const rightPane = document.getElementById(rightPaneId);
            
            let isLeftScrolling = false;
            let isRightScrolling = false;
            
            leftPane.addEventListener('scroll', function() {{
                if (!isRightScrolling) {{
                    isLeftScrolling = true;
                    rightPane.scrollTop = leftPane.scrollTop;
                    setTimeout(() => {{ isLeftScrolling = false; }}, 10);
                }}
            }});
            
            rightPane.addEventListener('scroll', function() {{
                if (!isLeftScrolling) {{
                    isRightScrolling = true;
                    leftPane.scrollTop = rightPane.scrollTop;
                    setTimeout(() => {{ isRightScrolling = false; }}, 10);
                }}
            }});
        }}
        
        // Close modal by clicking outside content
        window.onclick = function(event) {{
            const modal = document.getElementById('diffModal');
            const sideBySideModal = document.getElementById('sideBySideModal');
            if (event.target === modal) {{
                closeDiffModal();
            }}
            if (event.target === sideBySideModal) {{
                closeDiffModal();
            }}
        }}
        
        // Chiudi modal con tasto Escape
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeDiffModal();
            }}
        }});
        
        // ========================================
        // COLLAPSE/EXPAND - Toggle Sezioni
        // ========================================
        
        // Toggle gruppo Kind (Deployment, ConfigMap, etc)
        function toggleKind(kindId) {{
            const body = document.getElementById('kind-body-' + kindId);
            const icon = document.getElementById('toggle-' + kindId);
            
            if (body.classList.contains('collapsed')) {{
                // Espandi sezione
                body.classList.remove('collapsed');
                icon.classList.remove('collapsed');
                icon.textContent = '▼';
            }} else {{
                // Collassa sezione
                body.classList.add('collapsed');
                icon.classList.add('collapsed');
                icon.textContent = '▶';
            }}
        }}
        
        // Toggle singola risorsa dentro un Kind
        function toggleResource(resourceId) {{
            const body = document.getElementById('res-body-' + resourceId);
            const icon = document.getElementById('toggle-res-' + resourceId);
            
            if (body.classList.contains('collapsed')) {{
                body.classList.remove('collapsed');
                icon.classList.remove('collapsed');
                icon.textContent = '▼';
            }} else {{
                body.classList.add('collapsed');
                icon.classList.add('collapsed');
                icon.textContent = '▶';
            }}
        }}
        
        // Toggle intelligente di tutte le sezioni (Kind + Risorse)
        function toggleAll() {{
            // Determina lo stato: se almeno un gruppo o una risorsa è collapsed, espandi tutto
            let hasCollapsed = false;
            
            document.querySelectorAll('.kind-body').forEach(body => {{
                if (body.classList.contains('collapsed')) {{
                    hasCollapsed = true;
                }}
            }});
            
            if (!hasCollapsed) {{
                document.querySelectorAll('.resource-body').forEach(body => {{
                    if (body.classList.contains('collapsed')) {{
                        hasCollapsed = true;
                    }}
                }});
            }}
            
            if (hasCollapsed) {{
                // Espandi tutto
                document.querySelectorAll('.kind-body').forEach(body => {{
                    body.classList.remove('collapsed');
                }});
                document.querySelectorAll('.toggle-icon').forEach(icon => {{
                    icon.classList.remove('collapsed');
                    icon.textContent = '▼';
                }});
                document.querySelectorAll('.resource-body').forEach(body => {{
                    body.classList.remove('collapsed');
                }});
                document.querySelectorAll('.toggle-icon-small').forEach(icon => {{
                    icon.classList.remove('collapsed');
                    icon.textContent = '▼';
                }});
            }} else {{
                // Collassa tutto
                document.querySelectorAll('.kind-body').forEach(body => {{
                    body.classList.add('collapsed');
                }});
                document.querySelectorAll('.toggle-icon').forEach(icon => {{
                    icon.classList.add('collapsed');
                    icon.textContent = '▶';
                }});
                document.querySelectorAll('.resource-body').forEach(body => {{
                    body.classList.add('collapsed');
                }});
                document.querySelectorAll('.toggle-icon-small').forEach(icon => {{
                    icon.classList.add('collapsed');
                    icon.textContent = '▶';
                }});
            }}
        }}
        
        // Store original state of kind groups
        let originalKindGroupsState = null;
        
        // Filter resources by name in real-time
        function filterResources(searchText) {{
            const search = searchText.toLowerCase().trim();
            const clearBtn = document.getElementById('clearSearch');
            const searchInput = document.getElementById('resourceSearch');
            
            // Save original state on first filter
            if (search && !originalKindGroupsState) {{
                originalKindGroupsState = new Map();
                document.querySelectorAll('.kind-body').forEach(body => {{
                    originalKindGroupsState.set(body.id, body.classList.contains('collapsed'));
                }});
            }}
            
            // Show/hide clear button
            if (search) {{
                clearBtn.style.display = 'block';
            }} else {{
                clearBtn.style.display = 'none';
            }}
            
            // Get all kind groups
            const kindGroups = document.querySelectorAll('.kind-group');
            
            kindGroups.forEach(group => {{
                const resourceSections = group.querySelectorAll('.resource-section');
                const kindBody = group.querySelector('.kind-body');
                const toggleIcon = group.querySelector('.toggle-icon');
                let hasVisibleResources = false;
                
                resourceSections.forEach(section => {{
                    const resourceName = section.querySelector('.resource-name');
                    if (resourceName) {{
                        // Get or store original text
                        if (!resourceName.hasAttribute('data-original-text')) {{
                            resourceName.setAttribute('data-original-text', resourceName.textContent);
                        }}
                        const originalText = resourceName.getAttribute('data-original-text');
                        const name = originalText.toLowerCase();
                        
                        if (!search || name.includes(search)) {{
                            section.style.display = 'block';
                            hasVisibleResources = true;
                            
                            // Highlight matching text
                            if (search) {{
                                const index = name.indexOf(search);
                                if (index !== -1) {{
                                    const before = originalText.substring(0, index);
                                    const match = originalText.substring(index, index + search.length);
                                    const after = originalText.substring(index + search.length);
                                    resourceName.innerHTML = before + '<mark class="search-highlight">' + match + '</mark>' + after;
                                }} else {{
                                    resourceName.textContent = originalText;
                                }}
                            }} else {{
                                resourceName.textContent = originalText;
                            }}
                        }} else {{
                            section.style.display = 'none';
                            resourceName.textContent = originalText;
                        }}
                    }}
                }});
                
                // Handle kind group visibility and expansion
                if (search) {{
                    if (hasVisibleResources) {{
                        group.style.display = 'block';
                        // Expand kind group to show matching resources
                        if (kindBody) {{
                            kindBody.classList.remove('collapsed');
                        }}
                        if (toggleIcon) {{
                            toggleIcon.classList.remove('collapsed');
                            toggleIcon.textContent = '▼';
                        }}
                    }} else {{
                        group.style.display = 'none';
                    }}
                }} else {{
                    // Restore to initial collapsed state when search is cleared
                    group.style.display = 'block';
                    if (kindBody) {{
                        kindBody.classList.add('collapsed');
                        if (toggleIcon) {{
                            toggleIcon.classList.add('collapsed');
                            toggleIcon.textContent = '▶';
                        }}
                    }}
                    // Clear saved state
                    originalKindGroupsState = null;
                }}
            }});
            
            // Update search input border color
            if (search) {{
                searchInput.style.borderColor = '#667eea';
            }} else {{
                searchInput.style.borderColor = '#e5e7eb';
            }}
        }}
        
        // Clear filter
        function clearFilter() {{
            const searchInput = document.getElementById('resourceSearch');
            searchInput.value = '';
            filterResources('');
            searchInput.focus();
        }}
        
        // Espandi/Collassa tutte le risorse di un gruppo specifico
        function toggleKindResources(kindId) {{
            const kindBody = document.getElementById('kind-body-' + kindId);
            if (!kindBody) return;
            
            // Se il gruppo è collapsed, espandilo prima
            if (kindBody.classList.contains('collapsed')) {{
                toggleKind(kindId);
            }}
            
            // Ottieni tutte le risorse all'interno di questo gruppo
            const resourceBodies = kindBody.querySelectorAll('.resource-body');
            const resourceIcons = kindBody.querySelectorAll('.toggle-icon-small');
            
            // Determina lo stato: se almeno una risorsa è collapsed, espandi tutte, altrimenti collassa tutte
            let hasCollapsed = false;
            resourceBodies.forEach(body => {{
                if (body.classList.contains('collapsed')) {{
                    hasCollapsed = true;
                }}
            }});
            
            if (hasCollapsed) {{
                // Espandi tutte le risorse del gruppo
                resourceBodies.forEach(body => {{
                    body.classList.remove('collapsed');
                }});
                resourceIcons.forEach(icon => {{
                    icon.classList.remove('collapsed');
                    icon.textContent = '▼';
                }});
            }} else {{
                // Collassa tutte le risorse del gruppo
                resourceBodies.forEach(body => {{
                    body.classList.add('collapsed');
                }});
                resourceIcons.forEach(icon => {{
                    icon.classList.add('collapsed');
                    icon.textContent = '▶';
                }});
            }}
        }}
        
        // ========================================
        // MISSING RESOURCES - Toggle Tabella
        // ========================================
        
        // Mostra/nascondi sezione risorse presenti solo in un cluster
        function toggleMissingResources() {{
            const section = document.getElementById('missingResourcesSection');
            section.classList.toggle('visible');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="https://github.com/mabombo/kdiff" target="_blank" class="header-logo" title="View kdiff on GitHub">
                <img src="https://raw.githubusercontent.com/mabombo/kdiff/main/images/kdiff_logo_3.png" alt="kdiff logo" />
            </a>
            <h1>kdiff - Detailed Comparison Report</h1>
            <div class="subtitle">Kubernetes Resource Differences Analysis</div>
            <div class="metadata">
                <div class="metadata-item">
                    <strong>Cluster 1:</strong> {cluster1}
                </div>
                <div class="metadata-item">
                    <strong>Cluster 2:</strong> {cluster2}
                </div>
                <div class="metadata-item">
                    <strong>Generated:</strong> {timestamp}
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card resources">
                <div class="stat-label">Resources with Differences</div>
                <div class="stat-value">{total_resources}</div>
            </div>
            <div class="stat-card changes">
                <div class="stat-label">Total Changed Fields</div>
                <div class="stat-value">{total_paths}</div>
            </div>
            <div class="stat-card missing" onclick="toggleMissingResources()" title="Click to view details">
                <div class="stat-label">Resources Only in One Cluster</div>
                <div class="stat-value">{summary['counts']['missing_in_1'] + summary['counts']['missing_in_2']}</div>
                <div class="stat-hint">Click to view details</div>
            </div>
        </div>
        
        <div id="missingResourcesSection" class="missing-resources-section">
            <h3 style="margin-bottom: 20px; color: #111827; font-size: 1.5em;">Resources Present in Only One Cluster</h3>
            {generate_missing_resources_table(summary, cluster1, cluster2, c1_dir, c2_dir)}
        </div>
        
        <div class="content">
            <div class="section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; gap: 20px;">
                    <h2 class="section-title" style="margin-bottom: 0;">Resource Details</h2>
                    <div style="display: flex; align-items: center; gap: 10px; flex: 1; max-width: 500px;">
                        <span class="info-icon" title="Search filters resources by name only, not by resource content">ⓘ</span>
                        <input type="text" 
                               id="resourceSearch" 
                               placeholder="Filter resources by name..." 
                               oninput="filterResources(this.value)"
                               style="flex: 1; padding: 10px 14px; border: 2.5px solid #9ca3af; border-radius: 8px; font-size: 15px; font-weight: 500; outline: none; transition: all 0.2s;">
                        <button id="clearSearch" onclick="clearFilter()" style="padding: 10px 14px; background: #ef4444; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; display: none;">✕ Clear</button>
                    </div>
                    <button onclick="toggleAll()" style="padding: 3px 8px; background: #667eea; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 0.75em; font-weight: 600; white-space: nowrap;" title="Expand/Collapse all groups and resources">
                        +/− All
                    </button>
                </div>
                {''.join(kind_groups_html)}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by <strong>kdiff</strong> - Kubernetes Cluster Comparison Tool</p>
        </div>
    </div>
    
    <!-- Diff Modal -->
    <div id="diffModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title" id="modalTitle">Diff File</h2>
                <div class="zoom-controls">
                    <button class="zoom-btn" onclick="zoomOut()" title="Zoom Out">-</button>
                    <button class="zoom-btn" onclick="resetZoom()" title="Reset Zoom">⟲</button>
                    <button class="zoom-btn" onclick="zoomIn()" title="Zoom In">+</button>
                </div>
                <span class="close" onclick="closeDiffModal()">&times;</span>
            </div>
            <div style="padding: 10px 20px; background: #f8fafc; border-bottom: 1px solid #e5e7eb; display: flex; gap: 20px; align-items: center; font-size: 0.85em;">
                <span style="font-weight: 600; color: #64748b;">Legend:</span>
                <div style="display: flex; gap: 15px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 16px; height: 16px; background: #dcfce7; border: 1px solid #86efac; border-radius: 3px;"></div>
                        <span style="color: #059669;">Added</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 16px; height: 16px; background: #fee2e2; border: 1px solid #fca5a5; border-radius: 3px;"></div>
                        <span style="color: #dc2626;">Removed</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 16px; height: 16px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 3px;"></div>
                        <span style="color: #475569;">Unchanged</span>
                    </div>
                </div>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Diff content will be inserted here -->
            </div>
        </div>
    </div>
    
    <!-- Side-by-Side Diff Modal -->
    <div id="sideBySideModal" class="modal">
        <div class="sidebyside-modal-content">
            <div class="sidebyside-modal-header">
                <h2 id="sideBySideModalTitle" style="margin: 0; font-size: 1.3em;"></h2>
                <div style="display: flex; gap: 15px; align-items: center;">
                    <div class="zoom-controls">
                        <button class="zoom-btn" onclick="zoomOutSideBySide()" title="Zoom Out">−</button>
                        <button class="zoom-btn" onclick="resetZoomSideBySide()" title="Reset Zoom">⟲</button>
                        <button class="zoom-btn" onclick="zoomInSideBySide()" title="Zoom In">+</button>
                    </div>
                    <span class="close" onclick="closeDiffModal()">&times;</span>
                </div>
            </div>
            <div style="padding: 10px 20px; background: #f8fafc; border-bottom: 1px solid #e5e7eb; display: flex; gap: 20px; align-items: center; font-size: 0.85em; flex-wrap: wrap;">
                <span style="font-weight: 600; color: #64748b;">Filter:</span>
                <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    <div onclick="toggleSideBySideFilter('added')" id="filterLabelAdded" style="display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none;">
                        <div class="filter-box" id="filterBoxAdded" style="width: 20px; height: 20px; background: #dcfce7; border: 2px solid #86efac; border-radius: 3px; position: relative;"></div>
                        <span style="color: #059669;">Added</span>
                    </div>
                    <div onclick="toggleSideBySideFilter('removed')" id="filterLabelRemoved" style="display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none;">
                        <div class="filter-box" id="filterBoxRemoved" style="width: 20px; height: 20px; background: #fee2e2; border: 2px solid #fca5a5; border-radius: 3px; position: relative;"></div>
                        <span style="color: #dc2626;">Removed</span>
                    </div>
                    <div onclick="toggleSideBySideFilter('modified')" id="filterLabelModified" style="display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none;">
                        <div class="filter-box" id="filterBoxModified" style="width: 20px; height: 20px; background: #dbeafe; border: 2px solid #93c5fd; border-radius: 3px; position: relative;"></div>
                        <span style="color: #3b82f6;">Modified</span>
                    </div>
                    <div onclick="toggleSideBySideFilter('unchanged')" id="filterLabelUnchanged" style="display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none;">
                        <div class="filter-box" id="filterBoxUnchanged" style="width: 20px; height: 20px; background: #ffffff; border: 2px solid #e5e7eb; border-radius: 3px; position: relative;"></div>
                        <span style="color: #475569;">Unchanged</span>
                    </div>
                    <button onclick="resetSideBySideFilter()" style="padding: 4px 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9em; font-weight: 500; margin-left: 10px;">
                        Reset Filters
                    </button>
                </div>
            </div>
            <div class="sidebyside-container">
                <div class="sidebyside-pane">
                    <div class="sidebyside-pane-header cluster1" id="sideBySideLeftHeader">Cluster 1</div>
                    <div class="sidebyside-pane-content" id="sideBySideLeftPane">
                        <!-- Left pane content -->
                    </div>
                </div>
                <div class="sidebyside-pane">
                    <div class="sidebyside-pane-header cluster2" id="sideBySideRightHeader">Cluster 2</div>
                    <div class="sidebyside-pane-content" id="sideBySideRightPane">
                        <!-- Right pane content -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    (outdir / "diff-details.html").write_text(html_content, encoding="utf-8")


if __name__ == "__main__":
    main()
