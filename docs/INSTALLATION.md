<div align="center">
  <img src="../loghi/kdiff_logo_3.png" alt="kdiff logo" width="300"/>
</div>

# Guida Installazione e Distribuzione kdiff

## Opzioni di Distribuzione

kdiff offre tre modalità principali per l'installazione, ordinate per semplicità:

### 1. 🚀 Installazione automatica con script (CONSIGLIATO)

**Vantaggi:**
- ✅ Funziona sempre (nessuna dipendenza Python)
- ✅ Non richiede pip/setuptools
- ✅ Installabile senza permessi root (PREFIX=~/.local)
- ✅ Compatibile con sistemi "externally-managed"
- ✅ Rapido e affidabile

**Come funziona:**

```bash
PREFIX=$HOME/.local ./install.sh
```

Lo script:
1. Copia `lib/` e `kdiff_cli.py` in `PREFIX/lib/kdiff/`
2. Crea wrapper eseguibile in `PREFIX/bin/kdiff`
3. Verifica installazione e suggerisce aggiunta al PATH

**Disinstallazione:**
```bash
rm -rf ~/.local/lib/kdiff ~/.local/bin/kdiff
```

---

### 2. 📦 Installazione con pip (virtual environment)

**Vantaggi:**
- ✅ Standard Python
- ✅ Gestione dipendenze (anche se kdiff non ne ha)
- ✅ Integrazione con requirements.txt

**Requisiti:**
- Python 3.8+
- Virtual environment (richiesto su sistemi managed)

**Come funziona:**

```bash
# Crea e attiva virtual environment
python3 -m venv venv
source venv/bin/activate

# Installa in modalità editable (per sviluppo)
pip install -e .

# Oppure build e installa wheel
pip install build
python -m build
pip install dist/kdiff-1.0.0-py3-none-any.whl
```

**Disinstallazione:**
```bash
pip uninstall kdiff
```

**File necessari:**
- `pyproject.toml` (metadata e build config)
- `MANIFEST.in` (inclusione file non-Python)
- `setup.py` (opzionale, per backwards compatibility)

---

### 3. 🔧 Uso diretto (senza installazione)

**Vantaggi:**
- ✅ Zero setup
- ✅ Perfetto per testing/sviluppo
- ✅ Nessuna modifica al sistema

**Come funziona:**

```bash
git clone <repo>
cd kdiff
./bin/kdiff --help
```

**Limitazioni:**
- Richiede eseguire da directory repository
- Non disponibile system-wide

---

## Sistemi "Externally-Managed" (macOS/Ubuntu moderna)

### Problema

Python moderni (3.11+) su macOS con Homebrew e Ubuntu 23.04+ bloccano pip install system-wide:

```
error: externally-managed-environment
```

### Soluzioni

#### Opzione A: Usa install.sh (RACCOMANDATO)
```bash
PREFIX=$HOME/.local ./install.sh
```

#### Opzione B: Virtual environment
```bash
python3 -m venv ~/venv/kdiff
source ~/venv/kdiff/bin/activate
pip install -e .
```

#### Opzione C: pipx (app isolate)
```bash
brew install pipx  # o apt install pipx
pipx install .
```

#### Opzione D: --break-system-packages (NON RACCOMANDATO)
```bash
pip install --break-system-packages -e .
# ⚠️ Può danneggiare installazione Python system
```

---

## Distribuzione del Tool

### Su macOS

```bash
# Per utente singolo
PREFIX=$HOME/.local ./install.sh

# System-wide (tutti gli utenti)
sudo PREFIX=/usr/local ./install.sh
```

### Su Linux

```bash
# Ubuntu/Debian
PREFIX=$HOME/.local ./install.sh

# RHEL/CentOS/Fedora
PREFIX=$HOME/.local ./install.sh

# System-wide
sudo PREFIX=/usr/local ./install.sh
```

### Creazione package distribuzione

```bash
# Crea tarball con installer
tar czf kdiff-1.0.0.tar.gz \
    kdiff_cli.py \
    lib/ \
    install.sh \
    README.md \
    LICENSE \
    docs/

# Distribuzione
# Gli utenti possono scaricare ed eseguire:
tar xzf kdiff-1.0.0.tar.gz
cd kdiff-1.0.0
PREFIX=$HOME/.local ./install.sh
```

---

## Sviluppo

### Setup ambiente sviluppo

```bash
# Clone
git clone <repo>
cd kdiff

# Virtual environment (opzionale)
python3 -m venv venv
source venv/bin/activate

# Install in editable mode (opzionale)
pip install -e .

# Run tests
python -m pytest tests/
# oppure
bash tests/run_tests.sh
```

### Build distribuzione

```bash
# Build wheel con pip
pip install build
python -m build

# Risultato:
# dist/kdiff-1.0.0-py3-none-any.whl
# dist/kdiff-1.0.0.tar.gz
```

---

## FAQ

### Quale metodo scegliere?

- **Utenti finali**: `install.sh` (semplice, affidabile)
- **Sviluppatori**: `pip install -e .` in venv (standard)
- **CI/CD**: `install.sh` o Docker image

### kdiff richiede dipendenze?

No! kdiff usa **solo stdlib Python**:
- `json`, `pathlib`, `subprocess`, `argparse`, ecc.
- Richiede solo `kubectl` (esterno) per fetch risorse K8s

### Posso usare kdiff in Docker?

Sì:

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y kubectl
COPY . /app/kdiff
WORKDIR /app/kdiff
RUN PREFIX=/usr/local ./install.sh
ENTRYPOINT ["kdiff"]
```

### Supporto Windows?

kdiff funziona su:
- ✅ WSL2 (Ubuntu/Debian)
- ✅ Git Bash (con Python Windows)
- ⚠️ PowerShell (modifiche minori necessarie a `install.sh`)

---

## Riferimenti

- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [PEP 668 - Externally Managed Environments](https://peps.python.org/pep-0668/)
- [Python Packaging User Guide](https://packaging.python.org/)
