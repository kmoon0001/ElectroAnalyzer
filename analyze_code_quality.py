#!/usr/bin/env python3
"""
Code Quality Analysis and Enhancement Script

Analyzes code quality and provides specific recommendations:
- Type hint coverage analysis
- Code complexity analysis
- Documentation coverage
- Maintainability metrics
- Improvement suggestions
"""

import sys
from pathlib import Path
import json
from typing import Dict, Any, List
import argparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.code_quality_enhancer import CodeQualityEnhancer

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Code Quality Analysis for ElectroAnalyzer")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze code quality"
    )
    parser.add_argument(
        "--file",
        help="Analyze specific file"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report"
    )
    parser.add_argument(
        "--suggestions",
        action="store_true",
        help="Show improvement suggestions"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    enhancer = CodeQualityEnhancer()

    if args.file:
        # Analyze specific file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            return

        print(f"[CHECK] Analyzing {file_path}")

        try:
            metrics = enhancer.analyze_file(file_path)

            print(f"\n[SUMMARY] Code Quality Metrics:")
            print(f"  - Lines of Code: {metrics.lines_of_code}")
            print(f"  - Functions: {metrics.functions_count}")
            print(f"  - Classes: {metrics.classes_count}")
            print(f"  - Type Hint Coverage: {metrics.type_hint_coverage:.1%}")
            print(f"  - Docstring Coverage: {metrics.docstring_coverage:.1%}")
            print(f"  - Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
            print(f"  - Maintainability Index: {metrics.maintainability_index:.1f}/100")

            if args.suggestions:
                suggestions = enhancer.generate_improvement_suggestions(file_path)
                if suggestions:
                    print(f"\n💡 Improvement Suggestions:")
                    for suggestion in suggestions:
                        print(f"  - {suggestion}")
                else:
                    print(f"\n[OK] No major improvements needed")

        except Exception as e:
            print(f"Error analyzing file: {e}")

    elif args.analyze:
        # Analyze entire codebase
        print("[CHECK] Analyzing entire codebase...")

        try:
            analysis = enhancer.analyze_codebase(src_path)

            print(f"\n[SUMMARY] Codebase Analysis Summary:")
            print(f"  - Files Analyzed: {analysis['files_analyzed']}")
            print(f"  - Total Lines of Code: {analysis['total_metrics']['lines_of_code']}")
            print(f"  - Total Functions: {analysis['total_metrics']['functions_count']}")
            print(f"  - Total Classes: {analysis['total_metrics']['classes_count']}")
            print(f"  - Average Type Hint Coverage: {analysis['total_metrics']['type_hint_coverage']:.1%}")
            print(f"  - Average Docstring Coverage: {analysis['total_metrics']['docstring_coverage']:.1%}")
            print(f"  - Total Cyclomatic Complexity: {analysis['total_metrics']['cyclomatic_complexity']}")
            print(f"  - Average Maintainability Index: {analysis['total_metrics']['maintainability_index']:.1f}/100")

            # Show improvement priorities
            if analysis['improvement_priorities']:
                print(f"\n🎯 Improvement Priorities:")

                high_priority = [p for p in analysis['improvement_priorities'] if p['priority'] == 'high']
                medium_priority = [p for p in analysis['improvement_priorities'] if p['priority'] == 'medium']

                if high_priority:
                    print(f"\n  🔥 High Priority ({len(high_priority)} files):")
                    for priority in high_priority[:5]:  # Show top 5
                        print(f"    - {priority['file']}: {priority['issue']} (score: {priority['score']:.2f})")

                if medium_priority:
                    print(f"\n  🟡 Medium Priority ({len(medium_priority)} files):")
                    for priority in medium_priority[:5]:  # Show top 5
                        print(f"    - {priority['file']}: {priority['issue']} (score: {priority['score']:.2f})")
            else:
                print(f"\n[OK] No major improvement priorities identified")

            # Generate report if requested
            if args.report:
                report = generate_quality_report(analysis)

                report_file = project_root / "CODE_QUALITY_REPORT.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)

                print(f"\n[REPORT] Detailed report saved to: {report_file}")

            # Save analysis data
            analysis_file = project_root / "code_quality_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, default=str)

            print(f"[SUMMARY] Analysis data saved to: {analysis_file}")

        except Exception as e:
            print(f"Error analyzing codebase: {e}")

    else:
        parser.print_help()

def generate_quality_report(analysis: Dict[str, Any]) -> str:
    """Generate comprehensive quality report."""

    report = f"""# [SUMMARY] Code Quality Analysis Report

## Summary
- **Files Analyzed**: {analysis['files_analyzed']}
- **Total Lines of Code**: {analysis['total_metrics']['lines_of_code']:,}
- **Total Functions**: {analysis['total_metrics']['functions_count']:,}
- **Total Classes**: {analysis['total_metrics']['classes_count']:,}

## Quality Metrics

| Metric | Score | Status |
|--------|-------|--------|
| Type Hint Coverage | {analysis['total_metrics']['type_hint_coverage']:.1%} | {'[OK] Good' if analysis['total_metrics']['type_hint_coverage'] > 0.8 else '[WARNING] Needs Improvement'} |
| Docstring Coverage | {analysis['total_metrics']['docstring_coverage']:.1%} | {'[OK] Good' if analysis['total_metrics']['docstring_coverage'] > 0.7 else '[WARNING] Needs Improvement'} |
| Maintainability Index | {analysis['total_metrics']['maintainability_index']:.1f}/100 | {'[OK] Good' if analysis['total_metrics']['maintainability_index'] > 70 else '[WARNING] Needs Improvement'} |
| Total Complexity | {analysis['total_metrics']['cyclomatic_complexity']} | {'[OK] Good' if analysis['total_metrics']['cyclomatic_complexity'] < 1000 else '[WARNING] High'} |

## Improvement Priorities

"""

    # Group priorities by type
    high_priority = [p for p in analysis['improvement_priorities'] if p['priority'] == 'high']
    medium_priority = [p for p in analysis['improvement_priorities'] if p['priority'] == 'medium']

    if high_priority:
        report += f"### 🔥 High Priority ({len(high_priority)} files)\n\n"
        for priority in high_priority:
            report += f"- **{priority['file']}**: {priority['issue']} (score: {priority['score']:.2f})\n"
        report += "\n"

    if medium_priority:
        report += f"### 🟡 Medium Priority ({len(medium_priority)} files)\n\n"
        for priority in medium_priority:
            report += f"- **{priority['file']}**: {priority['issue']} (score: {priority['score']:.2f})\n"
        report += "\n"

    if not analysis['improvement_priorities']:
        report += "### [OK] No Major Issues Found\n\nAll files meet quality standards.\n\n"

    # Top files by maintainability
    file_metrics = analysis.get('file_metrics', [])
    if file_metrics:
        sorted_files = sorted(file_metrics, key=lambda x: x.maintainability_index, reverse=True)

        report += "## Top Files by Maintainability\n\n"
        for i, metrics in enumerate(sorted_files[:10], 1):
            report += f"{i}. **{metrics.file_path}** - {metrics.maintainability_index:.1f}/100\n"
        report += "\n"

        report += "## Files Needing Attention\n\n"
        low_maintainability = [m for m in sorted_files if m.maintainability_index < 60]
        for metrics in low_maintainability[:10]:
            report += f"- **{metrics.file_path}** - {metrics.maintainability_index:.1f}/100\n"
        report += "\n"

    # Recommendations
    report += """## Recommendations

### Immediate Actions (Week 1)
"""

    if analysis['total_metrics']['type_hint_coverage'] < 0.8:
        report += "- Add type hints to functions with missing annotations\n"

    if analysis['total_metrics']['docstring_coverage'] < 0.7:
        report += "- Add docstrings to undocumented functions and classes\n"

    if analysis['total_metrics']['cyclomatic_complexity'] > 1000:
        report += "- Refactor complex functions to reduce cyclomatic complexity\n"

    report += """
### Medium-term Actions (Week 2-4)
- Implement automated code quality checks in CI/CD
- Add pre-commit hooks for type checking and linting
- Establish code review guidelines for quality metrics

### Long-term Actions (Month 2+)
- Set up continuous quality monitoring
- Implement quality gates for new code
- Regular quality metric reviews and improvements

## Quality Standards

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Type Hint Coverage | >90% | {:.1%} | {} |
| Docstring Coverage | >80% | {:.1%} | {} |
| Maintainability Index | >80 | {:.1f} | {} |
| Max Function Complexity | <15 | {} | {} |

## Tools and Commands

### Type Checking
```bash
# Install mypy
pip install mypy

# Run type checking
mypy src/
```

### Code Linting
```bash
# Install flake8
pip install flake8

# Run linting
flake8 src/
```

### Documentation
```bash
# Generate documentation
sphinx-build -b html docs/ docs/_build/html
```

---
*Report generated by Code Quality Analyzer*
""".format(
        analysis['total_metrics']['type_hint_coverage'],
        '[OK]' if analysis['total_metrics']['type_hint_coverage'] > 0.9 else '[WARNING]',
        analysis['total_metrics']['docstring_coverage'],
        '[OK]' if analysis['total_metrics']['docstring_coverage'] > 0.8 else '[WARNING]',
        analysis['total_metrics']['maintainability_index'],
        '[OK]' if analysis['total_metrics']['maintainability_index'] > 80 else '[WARNING]',
        analysis['total_metrics']['cyclomatic_complexity'],
        '[OK]' if analysis['total_metrics']['cyclomatic_complexity'] < 1000 else '[WARNING]'
    )

    return report

if __name__ == "__main__":
    main()
