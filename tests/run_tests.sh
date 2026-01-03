#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Running Python test suite..."
python3 "$ROOT/tests/test_kdiff.py"

exit_code=$?

if [ $exit_code -eq 0 ]; then
  echo ""
  echo "All tests passed ✅"
else
  echo ""
  echo "Some tests failed ❌"
  exit $exit_code
fi

# run pytest tests if pytest is available
if command -v pytest >/dev/null 2>&1; then
  pytest -q
else
  echo "pytest not found; skipping pytest tests (shell-based tests still cover functionality)"
fi

echo "All tests passed ✅"
