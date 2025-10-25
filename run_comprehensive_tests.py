#!/usr/bin/env python3
"""
Comprehensive Test Runner

Runs all test suites with proper configuration:
- Unit tests
- Integration tests
- Performance tests
- Coverage analysis
- Test reporting
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import argparse

class TestRunner:
    """Comprehensive test runner for ElectroAnalyzer."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {}
        self.start_time = time.time()

    def run_command(self, command: List[str], description: str) -> Dict[str, Any]:
        """Run a command and return results."""
        print(f"\n🧪 {description}")
        print(f"Command: {' '.join(command)}")

        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            execution_time = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "description": description
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out after 5 minutes",
                "execution_time": time.time() - start_time,
                "description": description
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": time.time() - start_time,
                "description": description
            }

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests."""
        command = [
            "python", "-m", "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=json:coverage_unit.json"
        ]

        return self.run_command(command, "Running Unit Tests")

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        command = [
            "python", "-m", "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            "--timeout=300"
        ]

        return self.run_command(command, "Running Integration Tests")

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        command = [
            "python", "-m", "pytest",
            "tests/performance/",
            "-v",
            "--tb=short",
            "-m", "performance"
        ]

        return self.run_command(command, "Running Performance Tests")

    def run_api_tests(self) -> Dict[str, Any]:
        """Run API tests."""
        command = [
            "python", "-m", "pytest",
            "tests/api/",
            "-v",
            "--tb=short"
        ]

        return self.run_command(command, "Running API Tests")

    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests."""
        command = [
            "python", "-m", "pytest",
            "tests/e2e/",
            "-v",
            "--tb=short",
            "--timeout=600"
        ]

        return self.run_command(command, "Running End-to-End Tests")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests."""
        command = [
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=src",
            "--cov-report=html:htmlcov",
            "--cov-report=json:coverage_all.json",
            "--junitxml=test_results.xml"
        ]

        return self.run_command(command, "Running All Tests")

    def run_specific_tests(self, test_pattern: str) -> Dict[str, Any]:
        """Run specific tests matching pattern."""
        command = [
            "python", "-m", "pytest",
            test_pattern,
            "-v",
            "--tb=short"
        ]

        return self.run_command(command, f"Running Tests Matching: {test_pattern}")

    def check_test_environment(self) -> Dict[str, Any]:
        """Check if test environment is ready."""
        checks = {}

        # Check if API is running
        try:
            import requests
            response = requests.get("http://localhost:8001/health", timeout=5)
            checks["api_running"] = response.status_code == 200
        except Exception:
            checks["api_running"] = False

        # Check if frontend is running
        try:
            import requests
            response = requests.get("http://localhost:3000", timeout=5)
            checks["frontend_running"] = response.status_code == 200
        except Exception:
            checks["frontend_running"] = False

        # Check Python environment
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True
            )
            checks["python_version"] = result.stdout.strip()
        except Exception:
            checks["python_version"] = "Unknown"

        # Check pytest installation
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True
            )
            checks["pytest_available"] = result.returncode == 0
        except Exception:
            checks["pytest_available"] = False

        return {
            "success": all(checks.values()),
            "checks": checks,
            "description": "Test Environment Check"
        }

    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        total_time = time.time() - self.start_time

        report = f"""
# 🧪 Comprehensive Test Report

## Summary
- **Total Execution Time**: {total_time:.2f} seconds
- **Tests Run**: {len(self.results)} test suites
- **Overall Success**: {sum(1 for r in self.results.values() if r['success'])}/{len(self.results)} suites passed

## Test Results

"""

        for test_name, result in self.results.items():
            status = "[OK] PASSED" if result["success"] else "[FAIL] FAILED"
            report += f"""
### {test_name}
- **Status**: {status}
- **Execution Time**: {result['execution_time']:.2f}s
- **Return Code**: {result['returncode']}

"""

            if not result["success"]:
                report += f"""
**Error Output**:
```
{result['stderr']}
```

"""

        # Coverage summary
        coverage_files = [
            "coverage_unit.json",
            "coverage_all.json"
        ]

        for coverage_file in coverage_files:
            if Path(coverage_file).exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)

                    total_coverage = coverage_data['totals']['percent_covered']
                    report += f"""
## Coverage Summary ({coverage_file})
- **Total Coverage**: {total_coverage:.1f}%
- **Lines Covered**: {coverage_data['totals']['covered_lines']}/{coverage_data['totals']['num_statements']}

"""
                except Exception as e:
                    report += f"Error reading coverage file {coverage_file}: {e}\n"

        # Recommendations
        report += """
## Recommendations

"""

        failed_tests = [name for name, result in self.results.items() if not result["success"]]

        if failed_tests:
            report += f"""
### Failed Tests
The following test suites failed and should be investigated:
- {', '.join(failed_tests)}

"""

        # Performance recommendations
        performance_result = self.results.get("Performance Tests")
        if performance_result and performance_result["success"]:
            report += """
### Performance
All performance tests passed. The system meets performance requirements.

"""
        elif performance_result and not performance_result["success"]:
            report += """
### Performance Issues
Performance tests failed. Consider:
- Checking system resources
- Optimizing slow operations
- Reviewing performance thresholds

"""

        # Integration recommendations
        integration_result = self.results.get("Integration Tests")
        if integration_result and integration_result["success"]:
            report += """
### Integration
All integration tests passed. System components work together correctly.

"""
        elif integration_result and not integration_result["success"]:
            report += """
### Integration Issues
Integration tests failed. Consider:
- Checking API connectivity
- Verifying database connections
- Reviewing component interactions

"""

        report += f"""
## Next Steps
1. Review failed tests and fix issues
2. Run specific test suites for focused testing
3. Monitor performance metrics in production
4. Update test coverage for new features

---
*Report generated at {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return report

    def run_tests(self, test_types: List[str] = None) -> Dict[str, Any]:
        """Run specified test types."""
        if test_types is None:
            test_types = ["all"]

        test_functions = {
            "unit": self.run_unit_tests,
            "integration": self.run_integration_tests,
            "performance": self.run_performance_tests,
            "api": self.run_api_tests,
            "e2e": self.run_e2e_tests,
            "all": self.run_all_tests
        }

        # Check environment first
        env_check = self.check_test_environment()
        self.results["Environment Check"] = env_check

        if not env_check["success"]:
            print("[FAIL] Test environment not ready. Please check:")
            for check, status in env_check["checks"].items():
                print(f"  - {check}: {'[OK]' if status else '[FAIL]'}")
            return self.results

        # Run requested tests
        for test_type in test_types:
            if test_type in test_functions:
                result = test_functions[test_type]()
                self.results[test_type.title() + " Tests"] = result
            else:
                print(f"[FAIL] Unknown test type: {test_type}")

        return self.results

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive Test Runner for ElectroAnalyzer")
    parser.add_argument(
        "--tests",
        nargs="+",
        choices=["unit", "integration", "performance", "api", "e2e", "all"],
        default=["all"],
        help="Test types to run"
    )
    parser.add_argument(
        "--pattern",
        help="Run tests matching specific pattern"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed test report"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check test environment only"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root)

    if args.check_env:
        env_check = runner.check_test_environment()
        print("[CHECK] Test Environment Check:")
        for check, status in env_check["checks"].items():
            print(f"  - {check}: {'[OK]' if status else '[FAIL]'}")
        return

    if args.pattern:
        result = runner.run_specific_tests(args.pattern)
        print(f"\n{'[OK]' if result['success'] else '[FAIL]'} Pattern test completed")
        if not result["success"]:
            print(f"Error: {result['stderr']}")
        return

    # Run tests
    results = runner.run_tests(args.tests)

    # Print summary
    print("\n[SUMMARY] Test Summary:")
    for test_name, result in results.items():
        status = "[OK] PASSED" if result["success"] else "[FAIL] FAILED"
        execution_time = result.get('execution_time', 0.0)
        print(f"  - {test_name}: {status} ({execution_time:.2f}s)")

    # Generate report if requested
    if args.report:
        report = runner.generate_report()

        report_file = project_root / "TEST_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n[REPORT] Detailed report saved to: {report_file}")

    # Exit with appropriate code
    failed_tests = [name for name, result in results.items() if not result["success"]]
    if failed_tests:
        print(f"\n[FAIL] {len(failed_tests)} test suite(s) failed")
        sys.exit(1)
    else:
        print("\n[OK] All test suites passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
