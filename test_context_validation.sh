#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

echo "=========================================="
echo "Testing Context Validation"
echo "=========================================="
echo ""

SUCCESS=0
FAIL=0

echo "TEST 1: Invalid context should fail with exit code 2"
./bin/kdiff -c1 INVALID-CONTEXT-XYZ -c2 REEVO-BMW-QA -n connect -r configmap > /dev/null 2>&1
EXIT=$?
if [ $EXIT -eq 2 ]; then
    echo -e "${GREEN}✓ PASS${RESET} - Exit code 2 (as expected)"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - Exit code $EXIT (expected 2)"
    ((FAIL++))
fi

echo ""
echo "TEST 2: Invalid context should show error message"
OUTPUT=$(./bin/kdiff -c1 INVALID-CONTEXT-XYZ -c2 REEVO-BMW-QA -n connect -r configmap 2>&1)
if echo "$OUTPUT" | grep -q "Context 'INVALID-CONTEXT-XYZ' does not exist"; then
    echo -e "${GREEN}✓ PASS${RESET} - Error message shown"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - Error message not found"
    ((FAIL++))
fi

echo ""
echo "TEST 3: Invalid context should show available contexts"
if echo "$OUTPUT" | grep -q "Available contexts:"; then
    echo -e "${GREEN}✓ PASS${RESET} - Available contexts listed"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - Available contexts not listed"
    ((FAIL++))
fi

echo ""
echo "TEST 4: Invalid context should show suggestion"
if echo "$OUTPUT" | grep -q "Suggestion:"; then
    echo -e "${GREEN}✓ PASS${RESET} - Suggestion shown"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - Suggestion not shown"
    ((FAIL++))
fi

echo ""
echo "TEST 5: Valid context should pass validation"
./bin/kdiff -c REEVO-BMW-QA -n siav,connect -r configmap > /dev/null 2>&1
EXIT=$?
if [ $EXIT -eq 0 ] || [ $EXIT -eq 1 ]; then
    echo -e "${GREEN}✓ PASS${RESET} - Valid context accepted (exit code $EXIT)"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - Valid context rejected (exit code $EXIT)"
    ((FAIL++))
fi

echo ""
echo "TEST 6: Single-cluster mode with invalid context"
./bin/kdiff -c INVALID-SINGLE-CLUSTER -n siav,connect -r configmap > /dev/null 2>&1
EXIT=$?
if [ $EXIT -eq 2 ]; then
    echo -e "${GREEN}✓ PASS${RESET} - Invalid context rejected (exit code 2)"
    ((SUCCESS++))
else
    echo -e "${RED}✗ FAIL${RESET} - Exit code $EXIT (expected 2)"
    ((FAIL++))
fi

echo ""
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
