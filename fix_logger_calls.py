#!/usr/bin/env python3
"""Script to identify and report problematic logger calls in standard logging files only."""

import re
import os
from pathlib import Path
from collections import defaultdict

# Reserved LogRecord fields that can be passed to logger methods
VALID_KWARGS = {'exc_info', 'extra', 'stack_info', 'stacklevel'}

# Pattern to match logger calls with keyword arguments
LOGGER_PATTERN = re.compile(
    r'logger\.(debug|info|warning|error|critical|exception)\s*\(\s*[^)]*?\s*,\s*(\w+)\s*=',
    re.MULTILINE
)

def uses_standard_logging(filepath):
    """Check if a file uses standard logging.getLogger (not structlog)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    
    # If it uses structlog, skip it
    if 'structlog.get_logger' in content or 'import structlog' in content:
        return False
    
    # Check if it uses standard logging
    if 'logging.getLogger' in content or 'from logging import' in content:
        return True
    
    return False

def scan_file(filepath):
    """Scan a file for problematic logger calls."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []
    
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('#'):
            continue
        
        if 'logger.' in line and ('=' in line) and any(method in line for method in ['debug', 'info', 'warning', 'error', 'critical', 'exception']):
            match = LOGGER_PATTERN.search(line)
            if match:
                method = match.group(1)
                kwarg = match.group(2)
                
                if kwarg not in VALID_KWARGS:
                    issues.append({
                        'line_num': i,
                        'line': line.strip(),
                        'method': method,
                        'kwarg': kwarg
                    })
    
    return issues

def main():
    """Main function to scan the codebase."""
    print("Scanning for problematic logger calls in standard logging files...\n")
    
    issues_by_file = defaultdict(list)
    
    # Check src directory
    src_dir = Path('src')
    for py_file in src_dir.rglob('*.py'):
        if uses_standard_logging(py_file):
            issues = scan_file(py_file)
            if issues:
                issues_by_file[py_file] = issues
    
    # Print results
    total_issues = 0
    for filepath, issues in sorted(issues_by_file.items()):
        print(f"\n{filepath} ({len(issues)} issues):")
        for issue in issues:
            total_issues += 1
            print(f"  Line {issue['line_num']}: {issue['method']}(..., {issue['kwarg']}=...)")
            print(f"    {issue['line']}")
    
    print(f"\n\nTotal problematic logger calls found: {total_issues}")
    
    if total_issues == 0:
        print("[OK] All standard logging calls are properly formatted!")

if __name__ == '__main__':
    main()
