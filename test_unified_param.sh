#!/bin/bash
echo "TEST 1: Two-cluster with single namespace (-n connect)"
./bin/kdiff -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA -n connect -r configmap > /dev/null 2>&1
EXIT=$?
if [ $EXIT -eq 0 ] || [ $EXIT -eq 1 ]; then echo "✓ PASS"; elif [ $EXIT -eq 2 ]; then echo "⊘ SKIP (connection error)"; else echo "✗ FAIL"; fi

echo ""
echo "TEST 2: Two-cluster with multiple namespaces (-n siav,connect)"
./bin/kdiff -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA -n siav,connect -r configmap > /dev/null 2>&1
EXIT=$?
if [ $EXIT -eq 0 ] || [ $EXIT -eq 1 ]; then echo "✓ PASS"; elif [ $EXIT -eq 2 ]; then echo "⊘ SKIP (connection error)"; else echo "✗ FAIL"; fi

echo ""
echo "TEST 3: Single-cluster with multiple namespaces (-n siav,connect)"
./bin/kdiff -c REEVO-BMW-QA -n siav,connect -r configmap > /dev/null 2>&1
EXIT=$?
if [ $EXIT -eq 0 ] || [ $EXIT -eq 1 ]; then echo "✓ PASS"; elif [ $EXIT -eq 2 ]; then echo "⊘ SKIP (connection error)"; else echo "✗ FAIL"; fi

echo ""
echo "TEST 4: Single-cluster with --namespaces (alias)"
./bin/kdiff -c REEVO-BMW-QA --namespaces siav,connect -r configmap > /dev/null 2>&1
EXIT=$?
if [ $EXIT -eq 0 ] || [ $EXIT -eq 1 ]; then echo "✓ PASS"; elif [ $EXIT -eq 2 ]; then echo "⊘ SKIP (connection error)"; else echo "✗ FAIL"; fi

echo ""
echo "TEST 5: Verify parsing - single namespace"
OUTPUT=$(./bin/kdiff -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA -n connect -r configmap 2>&1 | grep "Namespaces:")
if echo "$OUTPUT" | grep -q "Namespaces: connect"; then echo "✓ PASS (parsing correct)"; else echo "✗ FAIL"; fi

echo ""
echo "TEST 6: Verify parsing - multiple namespaces"
OUTPUT=$(./bin/kdiff -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA -n siav,connect -r configmap 2>&1 | grep "Namespaces:")
if echo "$OUTPUT" | grep -q "Namespaces: siav, connect"; then echo "✓ PASS (parsing correct)"; else echo "✗ FAIL"; fi
