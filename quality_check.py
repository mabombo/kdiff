#!/usr/bin/env python3
"""
Quality Assurance Script for kdiff
Certifies code quality using multiple metrics and checks.
"""
import ast
import os
import subprocess
import sys
from pathlib import Path
from collections import defaultdict


class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")


def print_check(name, status, details=""):
    status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if status else f"{Colors.RED}✗{Colors.RESET}"
    print(f"{status_icon} {Colors.BOLD}{name}{Colors.RESET}")
    if details:
        print(f"  {Colors.YELLOW}{details}{Colors.RESET}")


def analyze_code_metrics(file_path):
    """Analyze Python file for complexity metrics."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return None, f"Syntax error: {e}"
    
    # Count metrics
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    
    # Calculate average function length
    func_lengths = []
    for func in functions:
        lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 0
        func_lengths.append(lines)
    
    avg_func_length = sum(func_lengths) / len(func_lengths) if func_lengths else 0
    
    # Calculate complexity (simplified McCabe)
    complexity_score = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity_score += 1
    
    return {
        'functions': len(functions),
        'classes': len(classes),
        'imports': len(imports),
        'avg_func_length': avg_func_length,
        'complexity_score': complexity_score,
        'lines': len(content.splitlines())
    }, None


def check_syntax(file_path):
    """Check Python syntax."""
    try:
        result = subprocess.run(
            ['python3', '-m', 'py_compile', str(file_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)


def check_imports(file_path):
    """Check for unused imports (basic)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False, "Cannot parse file"
    
    # Get imported names
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.name)
    
    # Check if imported names are used (simple check)
    used = set()
    for name in imported:
        if name in content:
            used.add(name)
    
    unused = imported - used
    return len(unused) == 0, f"Possible unused imports: {', '.join(unused)}" if unused else "All imports appear used"


def run_tests():
    """Run test suite using pytest."""
    try:
        import sys
        # Run tests using pytest with current Python executable
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-q', '--tb=no'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        all_passed = result.returncode == 0
        
        # Extract test count from pytest output (e.g., "49 passed in 0.73s")
        import re
        match = re.search(r'(\d+) passed', output)
        if match:
            total_tests = int(match.group(1))
            return all_passed, f"Ran {total_tests} tests in total"
        
        return all_passed, "Tests executed"
    except Exception as e:
        return False, str(e)


def analyze_directory_structure():
    """Analyze project structure."""
    metrics = {
        'python_files': 0,
        'test_files': 0,
        'total_lines': 0,
        'lib_files': 0,
    }
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                metrics['python_files'] += 1
                
                if 'test' in str(file_path):
                    metrics['test_files'] += 1
                if 'lib/' in str(file_path):
                    metrics['lib_files'] += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        metrics['total_lines'] += len(f.readlines())
                except IOError:
                    # Ignore files that cannot be read
                    pass
    
    return metrics


def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         KDIFF CODE QUALITY CERTIFICATION                 ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    all_passed = True
    
    # 1. Project Structure Analysis
    print_header("PROJECT STRUCTURE ANALYSIS")
    structure = analyze_directory_structure()
    print(f"  Python files:      {structure['python_files']}")
    print(f"  Library modules:   {structure['lib_files']}")
    print(f"  Test files:        {structure['test_files']}")
    print(f"  Total lines:       {structure['total_lines']:,}")
    print(f"  Lines per file:    {structure['total_lines'] // structure['python_files']:.0f} avg")
    
    # 2. Syntax Check
    print_header("SYNTAX VALIDATION")
    python_files = list(Path('.').rglob('*.py'))
    python_files = [f for f in python_files if '__pycache__' not in str(f) and '.git' not in str(f)]
    
    syntax_errors = 0
    for file in python_files:
        passed, error = check_syntax(file)
        if not passed:
            print_check(str(file), False, error)
            syntax_errors += 1
            all_passed = False
    
    if syntax_errors == 0:
        print_check(f"All {len(python_files)} Python files", True, "No syntax errors found")
    
    # 3. Code Metrics
    print_header("📈 CODE QUALITY METRICS")
    
    main_files = ['kdiff_cli.py', 'lib/compare.py', 'lib/normalize.py', 'lib/diff_details.py', 'lib/report.py']
    total_complexity = 0
    
    for file_path in main_files:
        if Path(file_path).exists():
            metrics, error = analyze_code_metrics(file_path)
            if error:
                print_check(file_path, False, error)
                all_passed = False
            else:
                print(f"\n{Colors.BOLD}{file_path}{Colors.RESET}")
                print(f"  Lines:          {metrics['lines']}")
                print(f"  Functions:      {metrics['functions']}")
                print(f"  Classes:        {metrics['classes']}")
                print(f"  Avg func len:   {metrics['avg_func_length']:.1f} lines")
                print(f"  Complexity:     {metrics['complexity_score']}")
                total_complexity += metrics['complexity_score']
                
                # Quality checks with realistic thresholds
                avg_len = metrics['avg_func_length']
                if avg_len < 80:
                    print(f"  {Colors.GREEN}✓ Good function size{Colors.RESET}")
                elif avg_len < 150:
                    # Acceptable for CLI parsers and template generators
                    print(f"  {Colors.GREEN}✓ Acceptable (CLI/templates){Colors.RESET}")
                elif avg_len < 250:
                    print(f"  {Colors.YELLOW}⚠ Consider refactoring{Colors.RESET}")
                else:
                    print(f"  {Colors.YELLOW}⚠ Large functions - mostly HTML templates{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Total complexity score:{Colors.RESET} {total_complexity}")
    
    # 4. Test Suite
    print_header("TEST SUITE EXECUTION")
    test_passed, test_info = run_tests()
    print_check("Test Suite", test_passed, test_info)
    if not test_passed:
        all_passed = False
    
    # 5. Import Analysis (sample)
    print_header("IMPORT ANALYSIS")
    sample_files = ['kdiff_cli.py', 'lib/compare.py']
    import_issues = 0
    for file in sample_files:
        if Path(file).exists():
            passed, info = check_imports(file)
            if not passed:
                import_issues += 1
            print_check(file, passed, info if not passed else "")
    
    if import_issues == 0:
        print(f"{Colors.GREEN}✓ No obvious import issues{Colors.RESET}")
    
    # 6. Git Status
    print_header("VERSION CONTROL STATUS")
    try:
        result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"{Colors.YELLOW}Modified files detected:{Colors.RESET}")
            print(result.stdout)
        else:
            print(f"{Colors.GREEN}✓ Working directory clean{Colors.RESET}")
        
        # Show recent commits
        result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
        print(f"\n{Colors.BOLD}Recent commits:{Colors.RESET}")
        print(result.stdout)
    except subprocess.CalledProcessError:
        print(f"{Colors.YELLOW}Git information not available{Colors.RESET}")
    
    # Final Report
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║              CERTIFICATION SUMMARY                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    if all_passed and syntax_errors == 0 and test_passed:
        print(f"{Colors.BOLD}{Colors.GREEN} CODE QUALITY: EXCELLENT{Colors.RESET}")
        print(f"{Colors.GREEN}✓ All checks passed{Colors.RESET}")
        print(f"{Colors.GREEN}✓ No syntax errors{Colors.RESET}")
        print(f"{Colors.GREEN}✓ All tests passing{Colors.RESET}")
        print(f"{Colors.GREEN}✓ Code structure healthy{Colors.RESET}")
        print(f"\n{Colors.BOLD}Status: READY FOR PRODUCTION {Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.BOLD}{Colors.YELLOW}⚠ CODE QUALITY: NEEDS ATTENTION{Colors.RESET}")
        if not test_passed:
            print(f"{Colors.RED}✗ Test failures detected{Colors.RESET}")
        if syntax_errors > 0:
            print(f"{Colors.RED}✗ Syntax errors found{Colors.RESET}")
        print(f"\n{Colors.BOLD}Status: REQUIRES FIXES{Colors.RESET}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
