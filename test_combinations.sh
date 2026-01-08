#!/bin/bash
# Test script for kdiff parameter combinations

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

echo "=========================================="
echo "Testing kdiff parameter combinations"
echo "=========================================="
echo ""

# Counter
SUCCESS=0
FAIL=0

run_test() {
    local desc="$1"
    shift
    echo -e "${YELLOW}TEST:${RESET} $desc"
    echo "Command: ./bin/kdiff $@"
    
    ./bin/kdiff "$@" > /dev/null 2>&1
    local exit_code=$?
    
    # Exit code 0 = no differences, 1 = differences found (both are success)
    # Exit code 2+ = actual error
    if [ $exit_code -eq 0 ] || [ $exit_code -eq 1 ]; then
        echo -e "${GREEN}✓ PASS (exit code: $exit_code)${RESET}"
        ((SUCCESS++))
    else
        echo -e "${RED}✗ FAIL (exit code: $exit_code)${RESET}"
        ((FAIL++))
    fi
    echo ""
}

# TWO-CLUSTER MODE TESTS
echo "=========================================="
echo "TWO-CLUSTER MODE"
echo "=========================================="
echo ""

run_test "Two-cluster: single namespace" \
    -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA -n connect -r configmap

run_test "Two-cluster: multiple namespaces" \
    -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA --namespaces siav,connect -r configmap

run_test "Two-cluster: with services and ingress" \
    -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA -n connect -r deployment,service --include-services-ingress

run_test "Two-cluster: multiple resource types" \
    -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA -n connect -r deployment,configmap,secret

run_test "Two-cluster: with metadata" \
    -c1 REEVO-BMW-PROD -c2 REEVO-BMW-QA -n connect -r configmap --show-metadata

# SINGLE-CLUSTER MODE TESTS
echo "=========================================="
echo "SINGLE-CLUSTER MODE"
echo "=========================================="
echo ""

run_test "Single-cluster: two namespaces" \
    -c REEVO-BMW-QA --namespaces siav,connect -r configmap

run_test "Single-cluster: three namespaces (pairwise)" \
    -c REEVO-BMW-QA --namespaces siav,connect,default -r configmap

run_test "Single-cluster: with services and ingress" \
    -c REEVO-BMW-QA --namespaces siav,connect -r deployment --include-services-ingress

run_test "Single-cluster: multiple resource types" \
    -c REEVO-BMW-QA --namespaces siav,connect -r deployment,configmap

run_test "Single-cluster: with metadata" \
    -c REEVO-BMW-QA --namespaces siav,connect -r configmap --show-metadata

# SUMMARY
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $SUCCESS${RESET}"
echo -e "${RED}Failed: $FAIL${RESET}"
echo -e "Total:  $((SUCCESS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${RESET}"
    exit 0
else
    echo -e "${RED}Some tests failed!${RESET}"
    exit 1
fi
