#!/usr/bin/env bash
#
# Script di installazione per kdiff
# Installa kdiff in /usr/local o in un percorso personalizzato
#

set -e

# Configurazione
PREFIX="${PREFIX:-/usr/local}"
INSTALL_DIR="$PREFIX/lib/kdiff"
BIN_DIR="$PREFIX/bin"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

# Funzioni
print_info() {
    echo -e "${GREEN}==>${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}Warning:${RESET} $1"
}

print_error() {
    echo -e "${RED}Error:${RESET} $1" >&2
    exit 1
}

# Verifica prerequisiti
check_dependencies() {
    print_info "Verifica prerequisiti..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "python3 non trovato. Installalo e riprova."
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_info "Python version: $PYTHON_VERSION"
    
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl non trovato. kdiff richiede kubectl per funzionare."
    fi
}

# Crea directory di installazione
create_dirs() {
    print_info "Creazione directory in $PREFIX..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
}

# Copia file
install_files() {
    print_info "Copia file in $INSTALL_DIR..."
    
    # Copia librerie
    cp -r lib "$INSTALL_DIR/"
    
    # Copia script principale come modulo Python
    cp kdiff_cli.py "$INSTALL_DIR/"
    
    # Copia documentazione
    if [ -f README.md ]; then
        cp README.md "$INSTALL_DIR/"
    fi
    
    if [ -d docs ]; then
        cp -r docs "$INSTALL_DIR/"
    fi
}

# Crea wrapper script
create_wrapper() {
    print_info "Creazione script wrapper in $BIN_DIR/kdiff..."
    
    cat > "$BIN_DIR/kdiff" << 'EOF'
#!/usr/bin/env python3
"""kdiff wrapper script"""
import sys
from pathlib import Path

# Aggiungi directory installazione al path
install_dir = Path(__file__).resolve().parent.parent / 'lib' / 'kdiff'
sys.path.insert(0, str(install_dir))

# Importa e esegui main
from kdiff_cli import main

if __name__ == '__main__':
    main()
EOF
    
    chmod +x "$BIN_DIR/kdiff"
}

# Verifica installazione
verify_install() {
    print_info "Verifica installazione..."
    
    if [ -x "$BIN_DIR/kdiff" ]; then
        print_info "kdiff installato correttamente in $BIN_DIR/kdiff"
        
        # Verifica che sia nel PATH
        if [[ ":$PATH:" == *":$BIN_DIR:"* ]]; then
            print_info "✅ $BIN_DIR è nel PATH"
        else
            print_warning "$BIN_DIR non è nel PATH. Aggiungi al tuo .bashrc/.zshrc:"
            echo ""
            echo "    export PATH=\"$BIN_DIR:\$PATH\""
            echo ""
        fi
        
        # Test esecuzione
        if "$BIN_DIR/kdiff" --help &> /dev/null; then
            print_info "✅ Test esecuzione: OK"
        else
            print_warning "kdiff installato ma --help non funziona"
        fi
    else
        print_error "Installazione fallita"
    fi
}

# Main
main() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║   kdiff - Kubernetes Cluster Compare  ║"
    echo "║              Installer                  ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    
    # Verifica che siamo nella directory corretta
    if [ ! -f "kdiff_cli.py" ] || [ ! -d "lib" ]; then
        print_error "Esegui questo script dalla root del repository kdiff"
    fi
    
    check_dependencies
    create_dirs
    install_files
    create_wrapper
    verify_install
    
    echo ""
    print_info "Installazione completata!"
    echo ""
    echo "Uso: kdiff -c1 CLUSTER1 -c2 CLUSTER2 [opzioni]"
    echo ""
}

# Help
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Uso: $0 [PREFIX=/custom/path]"
    echo ""
    echo "Installa kdiff in PREFIX (default: /usr/local)"
    echo ""
    echo "Esempi:"
    echo "  $0                    # Installa in /usr/local (richiede sudo)"
    echo "  PREFIX=~/.local $0    # Installa in ~/.local"
    echo ""
    exit 0
fi

main
