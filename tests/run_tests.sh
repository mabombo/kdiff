#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Running Python test suite..."
python3 "$ROOT/tests/test_kdiff.py"

echo ""
echo "Running CR discovery test suite..."
python3 "$ROOT/tests/test_cr_discovery.py"

exit_code=$?

if [ $exit_code -eq 0 ]; then
  echo ""
  echo "All tests passed ✅"
  echo ""
  echo "Running code quality certification..."
  python3 "$ROOT/quality_check.py"
else
  echo ""
  echo "Some tests failed ❌"
  exit $exit_code
fi
