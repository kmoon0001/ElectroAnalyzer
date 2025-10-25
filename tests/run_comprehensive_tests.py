"""Comprehensive test runner and configuration for document processing tests.

This module provides:
- Test discovery and execution
- Test configuration and setup
- Test reporting and analysis
- Performance monitoring
- Coverage reporting
- Test data management
"""

import pytest
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json


class DocumentProcessingTestRunner:
    """Comprehensive test runner for document processing tests."""

    def __init__(self, test_dir: str = "tests"):
        self.test_dir = Path(test_dir)
        self.results = {}
        self.coverage_data = {}

    def discover_tests(self) -> List[str]:
        """Discover all test files in the test directory."""
        test_files = []

        # Discover test files in different categories
        categories = [
            "unit/test_comprehensive_document_processing.py",
            "unit/test_comprehensive_security_validation.py",
            "unit/test_comprehensive_error_handling.py",
            "integration/test_comprehensive_document_processing_integration.py",
            "performance/test_comprehensive_document_processing_performance.py",
        ]

        for category in categories:
            test_file = self.test_dir / category
            if test_file.exists():
                test_files.append(str(test_file))

        return test_files

    def run_tests(self, test_files: List[str], verbose: bool = True) -> Dict[str, Any]:
        """Run tests and collect results."""
        results = {}

        for test_file in test_files:
            print(f"\n{'='*60}")
            print(f"Running tests in: {test_file}")
            print(f"{'='*60}")

            start_time = time.time()

            # Run pytest with specific options
            cmd = [
                sys.executable, "-m", "pytest",
                test_file,
                "-v" if verbose else "",
                "--tb=short",
                "--durations=10",
                "--maxfail=5",
                "--disable-warnings",
            ]

            # Remove empty strings
            cmd = [arg for arg in cmd if arg]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )

                end_time = time.time()
                duration = end_time - start_time

                results[test_file] = {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "duration": duration,
                    "success": result.returncode == 0,
                }

                print(f"Test completed in {duration:.2f} seconds")
                print(f"Return code: {result.returncode}")

                if result.stdout:
                    print("STDOUT:")
                    print(result.stdout)

                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)

            except subprocess.TimeoutExpired:
                results[test_file] = {
                    "returncode": -1,
                    "stdout": "",
                    "stderr": "Test timed out after 5 minutes",
                    "duration": 300,
                    "success": False,
                }
                print("Test timed out after 5 minutes")

            except Exception as e:
                results[test_file] = {
                    "returncode": -1,
                    "stdout": "",
                    "stderr": str(e),
                    "duration": 0,
                    "success": False,
                }
                print(f"Error running test: {e}")

        return results

    def run_coverage_analysis(self, test_files: List[str]) -> Dict[str, Any]:
        """Run coverage analysis on tests."""
        print(f"\n{'='*60}")
        print("Running coverage analysis")
        print(f"{'='*60}")

        # Run coverage analysis
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=src.core.parsing",
            "--cov=src.core.file_upload_validator",
            "--cov=src.core.security_validator",
            "--cov=src.core.analysis_service",
            "--cov-report=json",
            "--cov-report=html",
            "--cov-report=term",
        ] + test_files

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )

            # Parse coverage results
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)

                return {
                    "success": result.returncode == 0,
                    "coverage_data": coverage_data,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            else:
                return {
                    "success": False,
                    "coverage_data": {},
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "coverage_data": {},
                "stdout": "",
                "stderr": "Coverage analysis timed out after 10 minutes",
            }
        except Exception as e:
            return {
                "success": False,
                "coverage_data": {},
                "stdout": "",
                "stderr": str(e),
            }

    def run_performance_analysis(self, test_files: List[str]) -> Dict[str, Any]:
        """Run performance analysis on tests."""
        print(f"\n{'='*60}")
        print("Running performance analysis")
        print(f"{'='*60}")

        # Run performance tests
        performance_tests = [f for f in test_files if "performance" in f]

        if not performance_tests:
            return {"success": True, "message": "No performance tests found"}

        cmd = [
            sys.executable, "-m", "pytest",
            "--durations=0",
            "--tb=short",
            "-v",
        ] + performance_tests

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900  # 15 minutes timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Performance analysis timed out after 15 minutes",
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
            }

    def generate_report(self, test_results: Dict[str, Any], coverage_results: Dict[str, Any], performance_results: Dict[str, Any]) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("# Comprehensive Document Processing Test Report")
        report.append("=" * 60)
        report.append("")

        # Test Results Summary
        report.append("## Test Results Summary")
        report.append("")

        total_tests = len(test_results)
        successful_tests = sum(1 for result in test_results.values() if result["success"])
        failed_tests = total_tests - successful_tests

        report.append(f"- Total test files: {total_tests}")
        report.append(f"- Successful tests: {successful_tests}")
        report.append(f"- Failed tests: {failed_tests}")
        report.append(f"- Success rate: {(successful_tests/total_tests)*100:.1f}%")
        report.append("")

        # Individual Test Results
        report.append("## Individual Test Results")
        report.append("")

        for test_file, result in test_results.items():
            status = "[OK] PASS" if result["success"] else "[FAIL] FAIL"
            report.append(f"### {test_file}")
            report.append(f"- Status: {status}")
            report.append(f"- Duration: {result['duration']:.2f} seconds")
            report.append(f"- Return code: {result['returncode']}")

            if not result["success"] and result["stderr"]:
                report.append(f"- Error: {result['stderr']}")

            report.append("")

        # Coverage Results
        if coverage_results["success"]:
            report.append("## Coverage Analysis")
            report.append("")

            if "coverage_data" in coverage_results and coverage_results["coverage_data"]:
                coverage_data = coverage_results["coverage_data"]
                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                report.append(f"- Total coverage: {total_coverage:.1f}%")
                report.append("")

                # Coverage by module
                files = coverage_data.get("files", {})
                for file_path, file_data in files.items():
                    coverage_percent = file_data.get("summary", {}).get("percent_covered", 0)
                    report.append(f"- {file_path}: {coverage_percent:.1f}%")
            else:
                report.append("- Coverage data not available")
        else:
            report.append("## Coverage Analysis")
            report.append("- Coverage analysis failed")
            if coverage_results["stderr"]:
                report.append(f"- Error: {coverage_results['stderr']}")

        report.append("")

        # Performance Results
        if performance_results["success"]:
            report.append("## Performance Analysis")
            report.append("- Performance tests completed successfully")
            if performance_results["stdout"]:
                report.append("- Performance metrics available in output")
        else:
            report.append("## Performance Analysis")
            report.append("- Performance analysis failed")
            if performance_results["stderr"]:
                report.append(f"- Error: {performance_results['stderr']}")

        report.append("")

        # Recommendations
        report.append("## Recommendations")
        report.append("")

        if failed_tests > 0:
            report.append("- Review failed tests and fix issues")

        if coverage_results["success"] and "coverage_data" in coverage_results:
            coverage_data = coverage_results["coverage_data"]
            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
            if total_coverage < 80:
                report.append("- Increase test coverage to at least 80%")

        report.append("- Run tests regularly to catch regressions")
        report.append("- Monitor performance metrics for degradation")
        report.append("- Update tests when adding new features")

        return "\n".join(report)

    def run_all_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """Run all tests with comprehensive analysis."""
        print("Starting comprehensive document processing test suite...")
        print("=" * 60)

        # Discover tests
        test_files = self.discover_tests()
        print(f"Discovered {len(test_files)} test files:")
        for test_file in test_files:
            print(f"  - {test_file}")

        if not test_files:
            print("No test files found!")
            return {"success": False, "message": "No test files found"}

        # Run tests
        test_results = self.run_tests(test_files, verbose)

        # Run coverage analysis
        coverage_results = self.run_coverage_analysis(test_files)

        # Run performance analysis
        performance_results = self.run_performance_analysis(test_files)

        # Generate report
        report = self.generate_report(test_results, coverage_results, performance_results)

        # Save report
        report_file = Path("test_report.md")
        with open(report_file, 'w') as f:
            f.write(report)

        print(f"\nTest report saved to: {report_file}")

        return {
            "success": all(result["success"] for result in test_results.values()),
            "test_results": test_results,
            "coverage_results": coverage_results,
            "performance_results": performance_results,
            "report": report,
        }


def main():
    """Main entry point for test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive document processing test runner")
    parser.add_argument("--test-dir", default="tests", help="Test directory path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--coverage-only", action="store_true", help="Run only coverage analysis")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance analysis")

    args = parser.parse_args()

    runner = DocumentProcessingTestRunner(args.test_dir)

    if args.coverage_only:
        test_files = runner.discover_tests()
        results = runner.run_coverage_analysis(test_files)
        print("Coverage analysis completed")
        return results["success"]

    elif args.performance_only:
        test_files = runner.discover_tests()
        results = runner.run_performance_analysis(test_files)
        print("Performance analysis completed")
        return results["success"]

    else:
        results = runner.run_all_tests(args.verbose)
        print("All tests completed")
        return results["success"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
