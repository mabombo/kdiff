#!/usr/bin/env bash
#
# Helper script per aprire il report HTML nel browser
#

REPORT="kdiff_output/latest/diff-details.html"

if [ ! -f "$REPORT" ]; then
    echo "❌ Report non trovato: $REPORT"
    echo "💡 Esegui prima kdiff per generare il report"
    exit 1
fi

echo "📊 Apertura report nel browser..."

# Apre nel browser predefinito
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$REPORT"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$REPORT" 2>/dev/null || sensible-browser "$REPORT" 2>/dev/null || echo "❌ Impossibile aprire il browser"
else
    echo "❌ Sistema operativo non supportato: $OSTYPE"
    exit 1
fi

echo "✅ Report aperto: $(pwd)/$REPORT"
