<div align="center">
  <img src="loghi/kdiff_logo_3.png" alt="kdiff logo" width="300"/>
</div>

# kdiff — Confronto Intelligente Risorse Kubernetes tra Due Cluster

## 📋 Panoramica

**kdiff** è uno strumento Python professionale per confrontare configurazioni Kubernetes tra due cluster remoti. Identifica rapidamente risorse mancanti, differenti o presenti solo in un cluster, con supporto per diff intelligenti e report interattivi HTML.

### 🎯 Casi d'uso principali

- **Verifica configurazioni tra ambienti** (dev vs prod, staging vs prod)
- **Audit pre-migrazione** (cluster vecchio vs nuovo)
- **Troubleshooting differenze** tra deployment che dovrebbero essere identici
- **Documentazione differenze** con report HTML navigabili
- **CI/CD validation** di configurazioni tra ambienti

### ✨ Caratteristiche chiave

- ✅ **Normalizzazione intelligente**: rimuove automaticamente campi volatili (uid, resourceVersion, timestamps, etc)
- ✅ **Diff ConfigMap intelligente**: mostra solo le linee modificate nei file di configurazione, non l'intero blob
- ✅ **Confronto env non-posizionale**: variabili d'ambiente confrontate per nome, non per posizione nell'array
- ✅ **Report HTML interattivi**: interfaccia web con sezioni collassabili, zoom, e visualizzazione diff inline
- ✅ **Visualizzatore side-by-side**: confronto a doppio pannello stile VS Code con scroll sincronizzato
  * Clicca sul pulsante "⚖️ Side-by-Side" su qualsiasi risorsa con differenze
  * Layout a due pannelli (split 50/50) con nomi cluster reali
  * Confronto riga per riga con evidenziazione colori:
    - 🔴 Sfondo rosso: righe presenti solo nel primo cluster (rimosse)
    - 🟢 Sfondo verde: righe presenti solo nel secondo cluster (aggiunte)
    - 🔵 Sfondo blu: righe modificate tra i cluster
  * Alimentato da [jsdiff](https://github.com/kpdecker/jsdiff) per algoritmo diff robusto
  * Controlli zoom (+, ⟲, -) per regolare dimensione font
  * Scroll sincronizzato tra i pannelli
  * Numeri di riga su entrambi i lati per riferimento facile
- ✅ **Card risorse interattive**: Card "Resources Only in One Cluster" migliorata con icona occhio e effetti hover per migliore visibilità
- ✅ **Riduzione rumore**: labels e annotations opzionali (default: rimossi per concentrarsi su modifiche sostanziali)
- ✅ **Cleanup automatico**: mantiene solo ultime 3 esecuzioni per risparmiare spazio
- ✅ **Filtri flessibili**: include/escludi specifiche risorse o tipi
- ✅ **Nomi cluster reali**: usa i nomi effettivi invece di generici "cluster1/cluster2"

---

## 📦 Installazione e Requisiti

### Requisiti

- **Python 3.8+** (testato su 3.8-3.13)
- **kubectl** configurato con accesso ai cluster da confrontare
- **Sistema operativo**: macOS, Linux (anche WSL su Windows)

### Installazione

#### Metodo 1: Installazione automatica (consigliato)

```bash
# Scarica il repository
git clone <repo-url>
cd kdiff

# Installa in ~/.local (non richiede sudo)
PREFIX=$HOME/.local ./install.sh

# Aggiungi ~/.local/bin al PATH (se non già presente)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # o ~/.zshrc
source ~/.bashrc  # o source ~/.zshrc

# Verifica installazione
kdiff --help
```

Per installazione system-wide (richiede sudo):

```bash
sudo ./install.sh  # Installa in /usr/local
```

#### Metodo 2: Installazione con pip (richiede virtual environment)

```bash
# Crea virtual environment
python3 -m venv venv
source venv/bin/activate

# Installa in modalità editable
pip install -e .

# Verifica
kdiff --help
```

#### Metodo 3: Uso diretto (senza installazione)

```bash
# Clona repository
git clone <repo-url>
cd kdiff

# Usa direttamente
./bin/kdiff --help
```

**Nessuna dipendenza Python esterna richiesta!** Usa solo librerie standard.

### Verifica installazione

```bash
# Controlla che kdiff sia installato
which kdiff

# Verifica dipendenze
python3 --version  # >= 3.8
kubectl version --client

# Esegui test
cd <repository-directory>
bash tests/run_tests.sh
```

---

## 🚀 Uso Rapido

### Esempio base

```bash
# Confronta due contesti kubectl (output console)
./bin/kdiff -c1 prod-cluster -c2 staging-cluster

# Output JSON in directory specifica
./bin/kdiff -c1 prod -c2 staging -f json -o ./reports/prod-vs-staging
```

### Esempi avanzati

```bash
# Solo deployment e configmap di un namespace specifico
./bin/kdiff -c1 prod -c2 dev \
    -n myapp \
    -r deployment,configmap

# Escludi risorse specifiche
./bin/kdiff -c1 prod -c2 staging \
    --exclude-resources deployment__ns__legacy-app

# Includi Service/Ingress (normalmente esclusi per ridurre rumore)
./bin/kdiff -c1 prod -c2 staging \
    --include-services-ingress

# Mantieni metadata (labels/annotations) per debug dettagliato
./bin/kdiff -c1 prod -c2 staging \
    --show-metadata
```

---

## 📊 Output e Report

### Struttura directory output

```
kdiff_output/
└── latest/                      # ← Directory fissa (sempre la stessa)
    ├── summary.json             # ← Summary machine-readable
    ├── diff-details.html        # ← Report interattivo HTML ⭐
    ├── diff-details.json        # ← Dettagli diff per automazione
    ├── diffs/                   # ← File .diff per ogni risorsa modificata
    │   ├── configmap__myns__app-config.json.diff
    │   └── deployment__myns__webapp.json.diff
    ├── prod-cluster/            # ← Risorse normalizzate cluster 1
    │   ├── configmap__myns__app-config.json
    │   └── deployment__myns__webapp.json
    └── staging-cluster/         # ← Risorse normalizzate cluster 2
        ├── configmap__myns__app-config.json
        └── service__myns__webapp-svc.json
```

**Nota importante:** kdiff usa sempre la directory `kdiff_output/latest/` (invece di creare timestamp). Questo permette di:
- Aprire il report HTML sempre allo stesso percorso: `kdiff_output/latest/diff-details.html`
- Aggiornare il report semplicemente con un refresh del browser (F5)
- Evitare l'accumulo di directory vecchie

La directory viene automaticamente pulita ad ogni esecuzione.

### 📄 summary.json

```json
{
  "missing_in_2": ["deployment__prod__legacy-app.json"],
  "missing_in_1": ["service__staging__new-feature-svc.json"],
  "different": ["configmap__shared__app-config.json"],
  "counts": {
    "missing_in_2": 1,
    "missing_in_1": 1,
    "different": 1
  },
  "by_kind": {
    "deployment": {"missing_in_2": 1, "missing_in_1": 0, "different": 0},
    "service": {"missing_in_2": 0, "missing_in_1": 1, "different": 0},
    "configmap": {"missing_in_2": 0, "missing_in_1": 0, "different": 1}
  }
}
```

### 🌐 Report HTML Interattivo

Il file `diff-details.html` fornisce:

- **Dashboard statistiche** con card colorate per ogni metrica
- **Sezioni collassabili** per tipo risorsa (Deployment, ConfigMap, etc)
- **Risorse expandable** con pulsante "View Diff"
- **Modal popup** per visualizzare diff con controlli zoom (+, -, reset)
- **Syntax highlighting** per JSON e YAML
- **Legenda colori** per tipi di risorse
- **Tabella risorse mancanti** cliccabile

---

## 📚 Risorse Gestite

```bash
✓ deployment          # Workload principale
✓ statefulset         # App stateful
✓ daemonset           # Agent system-wide
✓ configmap           # Configurazione
✓ secret              # Credenziali
✓ persistentvolumeclaim  # Storage
✓ serviceaccount      # Identity
✓ role / rolebinding  # RBAC
✓ horizontalpodautoscaler  # Autoscaling
✓ cronjob / job       # Scheduled tasks

⚠ service / ingress   # Esclusi di default (--include-services-ingress)
```

---

## 🧪 Testing

```bash
# Test completi (richiede Python 3.8+)
bash tests/run_tests.sh

# Oppure direttamente con Python
python3 tests/test_kdiff.py
```

### Coverage test suite

| Test Class | Descrizione | Test count |
|------------|-------------|------------|
| **TestNormalize** | Normalizzazione con/senza metadata | 2 |
| **TestEnvDictConversion** | Conversione env arrays → dict | 3 |
| **TestConfigMapDiff** | Diff intelligente ConfigMap | 2 |
| **TestCompare** | Rilevamento differenze | 1 |
| **TestEndToEnd** | E2E con mock kubectl | 1 |
| **TestReports** | Generazione report HTML | 1 |
| **TOTALE** | | **10 test** |

---

## 🔧 Opzioni Comando

```bash
./bin/kdiff \
    -c1 CLUSTER1_CONTEXT \        # Context kubectl cluster 1 (richiesto)
    -c2 CLUSTER2_CONTEXT \        # Context kubectl cluster 2 (richiesto)
    [-n NAMESPACE] \              # Namespace specifico (default: tutti)
    [-r RESOURCE_TYPES] \         # Lista comma-separated
    [-o OUTPUT_DIR] \             # Directory output (default: ./kdiff_output/<timestamp>)
    [-f FORMAT] \                 # text|json (default: text)
    [--show-metadata] \           # Mantieni labels/annotations
    [--include-services-ingress] \  # Includi Service/Ingress
    [--exclude-resources RES1,RES2]  # Escludi risorse specifiche
```

Vedi `docs/usage.md` per dettagli completi.

---

## 🏗️ Architettura

### File principali

```
kdiff/
├── bin/kdiff                    # CLI principale
├── lib/
│   ├── normalize.py             # Normalizzazione risorse
│   ├── compare.py               # Confronto e diff generation
│   ├── report.py                # Report console
│   ├── report_md.py             # Report Markdown/HTML
│   └── diff_details.py          # Report HTML interattivo ⭐
├── tests/
│   ├── test_kdiff.py            # Test suite completa
│   └── run_tests.sh
└── docs/
    ├── usage.md                 # Guida uso dettagliata
    └── diff_details.md          # Doc report HTML
```

### Flusso esecuzione

```
1. bin/kdiff → fetch risorse via kubectl
2. lib/normalize.py → rimuovi campi volatili
3. Salva JSON normalizzati
4. lib/compare.py → genera diff (ConfigMap intelligente + standard)
5. lib/report_md.py → report base
6. lib/diff_details.py → report HTML interattivo
7. Cleanup automatico (ultimi 3)
```

---

## 🔍 Funzionalità Avanzate

### Diff ConfigMap Intelligente

Invece di mostrare l'intero JSON come modificato, estrae ogni `data.*` field e lo confronta linea per linea:

```diff
=== data.application.yaml ===
--- data.application.yaml (prod)
+++ data.application.yaml (staging)
@@ -10,7 +10,7 @@
 server:
   port: 8080
-  max-connections: 100
+  max-connections: 200
   timeout: 30s
```

### Conversione Env Arrays → Dictionaries

Variabili d'ambiente confrontate per nome, non per posizione nell'array → **nessun falso positivo** da riordinamenti.

---

## 🗑️ Disinstallazione

### Se installato con install.sh

```bash
# Installazione in ~/.local
rm -rf ~/.local/lib/kdiff
rm ~/.local/bin/kdiff

# Installazione system-wide (/usr/local)
sudo rm -rf /usr/local/lib/kdiff
sudo rm /usr/local/bin/kdiff
```

### Se installato con pip

```bash
# All'interno del virtual environment
pip uninstall kdiff
```

---

## 📚 Documentazione Aggiuntiva

- [docs/usage.md](docs/usage.md) - Guida completa uso e parametri
- [docs/diff_details.md](docs/diff_details.md) - Documentazione report HTML

---

## 🐛 Troubleshooting

### kdiff: command not found

Verifica che il PATH includa la directory di installazione:

```bash
# Se installato in ~/.local
echo $PATH | grep -o "$HOME/.local/bin"

# Se non presente, aggiungi al ~/.bashrc o ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Errore "kubectl not found"

```bash
# Verifica installazione kubectl
which kubectl

# Su macOS (con Homebrew)
brew install kubectl

# Su Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### Python version incompatibile

```bash
# Verifica versione Python (richiede >= 3.8)
python3 --version

# Su macOS con Homebrew
brew install python@3.11

# Su Ubuntu/Debian
sudo apt update
sudo apt install python3.11
```

---

## 🤝 Contributi

Suggerimenti benvenuti! Apri una issue o invia una PR.

---

## 📝 License

MIT License - vedi [LICENSE](LICENSE)

---

**Versione**: 1.1.0  
**Data ultimo aggiornamento**: Gennaio 2026
