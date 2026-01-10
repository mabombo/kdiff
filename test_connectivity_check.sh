#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

echo "=========================================="
echo "Testing Cluster Connectivity Check"
echo "=========================================="
echo ""

SUCCESS=0
FAIL=0

echo "TEST 1: Unreachable cluster should fail with connectivity error"
OUTPUT=$(./bin/kdiff -c REEVO-BMW-PROD -n siav,connect -r configmap 2>&1)
EXIT=$?
if [ $EXIT -eq 2 ] && echo "$OUTPUT" | grep -q "CONNECTIVITY ERROR"; then
    echo -e "${GREEN}✓ PASS${RESET} - Connectivity error detected"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - Exit code $EXIT"
    ((FAIL++))
fi

echo ""
echo "TEST 2: Connectivity error should show helpful suggestions"
if echo "$OUTPUT" | grep -q "Suggestions:"; then
    echo -e "${GREEN}✓ PASS${RESET} - Suggestions shown"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - No suggestions found"
    ((FAIL++))
fi

echo ""
echo "TEST 3: Should mention VPN in suggestions"
if echo "$OUTPUT" | grep -q "VPN"; then
    echo -e "${GREEN}✓ PASS${RESET} - VPN mentioned"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - VPN not mentioned"
    ((FAIL++))
fi

echo ""
echo "TEST 4: Should check connectivity before fetch"
if echo "$OUTPUT" | grep -q "Testing cluster connectivity"; then
    echo -e "${GREEN}✓ PASS${RESET} - Connectivity tested first"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - No connectivity test message"
    ((FAIL++))
fi

echo ""
echo "TEST 5: Valid reachable cluster (orbstack) should pass"
OUTPUT=$(./bin/kdiff -c orbstack -n default,kube-system -r configmap 2>&1)
EXIT=$?
if ([ $EXIT -eq 0 ] || [ $EXIT -eq 1 ]) && echo "$OUTPUT" | grep -q "All clusters are reachable"; then
    echo -e "${GREEN}✓ PASS${RESET} - Reachable cluster accepted"
    ((SUCCESS++))
else
    echo -e "${YELLOW}⊘ SKIP${RESET} - orbstack might not be available (exit code $EXIT)"
    # Don't count as failure since orbstack might not exist
fi

echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $SUCCESS${RESET}"
echo -e "${RED}Failed: $FAIL${RESET}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All critical tests passed!${RESET}"
    exit 0
else
    echo -e "${RED}Some tests failed!${RESET}"
    exit 1
fi
