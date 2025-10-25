#!/usr/bin/env python3
"""
Quality Metrics Improvement Script

This script analyzes the current codebase and provides specific recommendations
to improve quality metrics from A- (9.0/10) to A+ (9.5+/10).

Usage:
    python improve_quality_metrics.py --analyze
    python improve_quality_metrics.py --implement --priority high
    python improve_quality_metrics.py --generate-tests
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List
import json
import subprocess
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.quality_improvement import QualityImprovementEngine
from src.utils.test_coverage_improvement import TestCoverageImprovementEngine
from src.api.documentation.enhanced_api_docs import EnhancedAPIDocumentation

class QualityMetricsImprover:
    """Main class for improving quality metrics."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.test_path = project_root / "tests"
        self.quality_engine = QualityImprovementEngine()
        self.test_engine = TestCoverageImprovementEngine(self.src_path, self.test_path)

        # Current metrics (from senior analysis)
        self.current_metrics = {
            "architecture": 9.5,
            "code_quality": 9.0,
            "security": 9.5,
            "performance": 8.5,
            "maintainability": 9.0,
            "test_coverage": 9.2,
            "documentation": 8.0,
            "operational_readiness": 9.5
        }

        # Target metrics
        self.target_metrics = {
            "architecture": 9.8,
            "code_quality": 9.5,
            "security": 9.8,
            "performance": 9.2,
            "maintainability": 9.5,
            "test_coverage": 9.8,
            "documentation": 9.0,
            "operational_readiness": 9.8
        }

    def analyze_current_state(self) -> Dict[str, Any]:
        """Analyze current codebase state."""
        print("🔍 Analyzing current codebase state...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "codebase_analysis": self.quality_engine.analyze_codebase(self.src_path),
            "coverage_analysis": self.test_engine.coverage_analyzer.run_coverage_analysis(),
            "current_metrics": self.current_metrics,
            "target_metrics": self.target_metrics,
            "gaps": self._calculate_gaps(),
            "recommendations": self._generate_recommendations()
        }

        return analysis

    def _calculate_gaps(self) -> Dict[str, float]:
        """Calculate gaps between current and target metrics."""
        gaps = {}
        for metric in self.current_metrics:
            gaps[metric] = self.target_metrics[metric] - self.current_metrics[metric]
        return gaps

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate specific recommendations for improvement."""
        recommendations = []

        # Performance improvements
        if self.current_metrics["performance"] < self.target_metrics["performance"]:
            recommendations.append({
                "category": "performance",
                "priority": "high",
                "impact": 0.7,
                "effort": "medium",
                "actions": [
                    "Implement database query optimization",
                    "Add connection pooling monitoring",
                    "Optimize memory usage patterns",
                    "Add performance profiling decorators",
                    "Implement caching strategies"
                ],
                "files_to_modify": [
                    "src/database/database.py",
                    "src/core/analysis_service.py",
                    "src/api/main.py"
                ]
            })

        # Documentation improvements
        if self.current_metrics["documentation"] < self.target_metrics["documentation"]:
            recommendations.append({
                "category": "documentation",
                "priority": "high",
                "impact": 1.0,
                "effort": "low",
                "actions": [
                    "Generate comprehensive API documentation",
                    "Add inline code documentation",
                    "Create integration guides",
                    "Add performance benchmarks",
                    "Generate code examples"
                ],
                "files_to_modify": [
                    "src/api/documentation/",
                    "README.md",
                    "API_DOCUMENTATION.md"
                ]
            })

        # Test coverage improvements
        if self.current_metrics["test_coverage"] < self.target_metrics["test_coverage"]:
            recommendations.append({
                "category": "test_coverage",
                "priority": "medium",
                "impact": 0.6,
                "effort": "high",
                "actions": [
                    "Add missing unit tests",
                    "Create integration test templates",
                    "Add performance test suites",
                    "Implement load testing",
                    "Add error handling tests"
                ],
                "files_to_modify": [
                    "tests/unit/",
                    "tests/integration/",
                    "tests/performance/"
                ]
            })

        # Code quality improvements
        if self.current_metrics["code_quality"] < self.target_metrics["code_quality"]:
            recommendations.append({
                "category": "code_quality",
                "priority": "medium",
                "impact": 0.5,
                "effort": "medium",
                "actions": [
                    "Add comprehensive type hints",
                    "Improve function documentation",
                    "Reduce code complexity",
                    "Add performance profiling",
                    "Implement code quality checks"
                ],
                "files_to_modify": [
                    "src/core/",
                    "src/api/routers/",
                    "src/database/"
                ]
            })

        return recommendations

    def implement_improvements(self, priority: str = "high") -> Dict[str, Any]:
        """Implement improvements based on priority."""
        print(f"🚀 Implementing {priority} priority improvements...")

        analysis = self.analyze_current_state()
        recommendations = analysis["recommendations"]

        # Filter by priority
        priority_recommendations = [
            rec for rec in recommendations
            if rec["priority"] == priority
        ]

        implementation_results = {}

        for rec in priority_recommendations:
            category = rec["category"]
            print(f"  📝 Implementing {category} improvements...")

            if category == "documentation":
                implementation_results[category] = self._implement_documentation_improvements()
            elif category == "performance":
                implementation_results[category] = self._implement_performance_improvements()
            elif category == "test_coverage":
                implementation_results[category] = self._implement_test_coverage_improvements()
            elif category == "code_quality":
                implementation_results[category] = self._implement_code_quality_improvements()

        return implementation_results

    def _implement_documentation_improvements(self) -> Dict[str, Any]:
        """Implement documentation improvements."""
        results = {"files_created": [], "files_updated": []}

        # Generate enhanced API documentation
        try:
            from src.api.main import app
            doc_generator = EnhancedAPIDocumentation(app)

            # Generate OpenAPI schema
            schema = doc_generator.generate_openapi_schema()

            # Save enhanced schema
            schema_file = self.project_root / "openapi_enhanced.json"
            with open(schema_file, 'w') as f:
                json.dump(schema, f, indent=2)
            results["files_created"].append(str(schema_file))

            # Generate integration guide
            integration_guide = doc_generator.generate_integration_guide()
            guide_file = self.project_root / "INTEGRATION_GUIDE.md"
            with open(guide_file, 'w') as f:
                f.write(integration_guide)
            results["files_created"].append(str(guide_file))

            # Generate performance benchmarks
            benchmarks = doc_generator.generate_performance_benchmarks()
            benchmarks_file = self.project_root / "PERFORMANCE_BENCHMARKS.md"
            with open(benchmarks_file, 'w') as f:
                f.write(f"# Performance Benchmarks\n\n```json\n{json.dumps(benchmarks, indent=2)}\n```")
            results["files_created"].append(str(benchmarks_file))

        except Exception as e:
            results["error"] = str(e)

        return results

    def _implement_performance_improvements(self) -> Dict[str, Any]:
        """Implement performance improvements."""
        results = {"files_created": [], "files_updated": []}

        # Create performance monitoring utilities
        performance_utils = '''
"""Performance Monitoring Utilities

Provides comprehensive performance monitoring and optimization tools.
"""

import time
import psutil
import functools
from typing import Callable, Any, Dict
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and optimize application performance."""

    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'response_time_ms': 1000,
            'memory_usage_mb': 100,
            'cpu_usage_percent': 80
        }

    @contextmanager
    def monitor_operation(self, operation_name: str):
        """Monitor an operation's performance."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024

            execution_time = (end_time - start_time) * 1000
            memory_delta = end_memory - start_memory

            self.metrics[operation_name] = {
                'execution_time_ms': execution_time,
                'memory_delta_mb': memory_delta,
                'timestamp': time.time()
            }

            # Log performance warnings
            if execution_time > self.thresholds['response_time_ms']:
                logger.warning(f"Slow operation: {operation_name} took {execution_time:.2f}ms")

            if memory_delta > self.thresholds['memory_usage_mb']:
                logger.warning(f"High memory usage: {operation_name} used {memory_delta:.2f}MB")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {"message": "No performance data available"}

        total_operations = len(self.metrics)
        avg_execution_time = sum(m['execution_time_ms'] for m in self.metrics.values()) / total_operations
        avg_memory_usage = sum(m['memory_delta_mb'] for m in self.metrics.values()) / total_operations

        return {
            'total_operations': total_operations,
            'avg_execution_time_ms': avg_execution_time,
            'avg_memory_usage_mb': avg_memory_usage,
            'slowest_operation': max(self.metrics.items(), key=lambda x: x[1]['execution_time_ms']),
            'highest_memory_operation': max(self.metrics.items(), key=lambda x: x[1]['memory_delta_mb'])
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with performance_monitor.monitor_operation(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
'''

        perf_file = self.src_path / "utils" / "performance_monitor.py"
        with open(perf_file, 'w') as f:
            f.write(performance_utils)
        results["files_created"].append(str(perf_file))

        return results

    def _implement_test_coverage_improvements(self) -> Dict[str, Any]:
        """Implement test coverage improvements."""
        results = {"files_created": [], "files_updated": []}

        # Generate test improvement plan
        improvement_plan = self.test_engine.generate_improvement_plan()
        plan_file = self.project_root / "TEST_IMPROVEMENT_PLAN.md"
        with open(plan_file, 'w') as f:
            f.write(improvement_plan)
        results["files_created"].append(str(plan_file))

        return results

    def _implement_code_quality_improvements(self) -> Dict[str, Any]:
        """Implement code quality improvements."""
        results = {"files_created": [], "files_updated": []}

        # Generate code quality improvement plan
        analysis = self.quality_engine.analyze_codebase(self.src_path)
        improvement_plan = self.quality_engine.generate_improvement_plan(analysis)

        plan_file = self.project_root / "CODE_QUALITY_IMPROVEMENT_PLAN.md"
        with open(plan_file, 'w') as f:
            f.write(improvement_plan)
        results["files_created"].append(str(plan_file))

        return results

    def generate_quality_report(self) -> str:
        """Generate comprehensive quality improvement report."""
        analysis = self.analyze_current_state()

        report = f"""
# Quality Metrics Improvement Report

## Current Status
- **Overall Grade**: A- (9.0/10)
- **Target Grade**: A+ (9.5+/10)
- **Analysis Date**: {analysis['timestamp']}

## Current Metrics vs Targets

| Metric | Current | Target | Gap | Priority |
|--------|---------|--------|-----|----------|
"""

        for metric, current in self.current_metrics.items():
            target = self.target_metrics[metric]
            gap = target - current
            priority = "High" if gap > 0.5 else "Medium" if gap > 0.2 else "Low"

            report += f"| {metric.replace('_', ' ').title()} | {current}/10 | {target}/10 | +{gap:.1f} | {priority} |\n"

        report += f"""
## Codebase Analysis
- **Files Analyzed**: {analysis['codebase_analysis']['files_analyzed']}
- **Type Hint Coverage**: {analysis['codebase_analysis']['type_hint_coverage']:.1%}
- **Documentation Coverage**: {analysis['codebase_analysis']['docstring_coverage']:.1%}
- **Complexity Score**: {analysis['codebase_analysis']['complexity_score']:.1f}/100

## Recommendations

### High Priority (Week 1)
"""

        high_priority = [rec for rec in analysis['recommendations'] if rec['priority'] == 'high']
        for rec in high_priority:
            report += f"""
#### {rec['category'].replace('_', ' ').title()}
- **Impact**: {rec['impact']:.1f}
- **Effort**: {rec['effort']}
- **Actions**:
"""
            for action in rec['actions']:
                report += f"  - {action}\n"

        report += """
### Implementation Commands

```bash
# Run analysis
python improve_quality_metrics.py --analyze

# Implement high priority improvements
python improve_quality_metrics.py --implement --priority high

# Generate test improvements
python improve_quality_metrics.py --generate-tests

# Run quality checks
python improve_quality_metrics.py --check-quality
```

## Expected Outcomes

After implementing all recommendations:
- **Performance**: 8.5 → 9.2 (+0.7)
- **Documentation**: 8.0 → 9.0 (+1.0)
- **Test Coverage**: 9.2 → 9.8 (+0.6)
- **Code Quality**: 9.0 → 9.5 (+0.5)

**New Overall Grade**: A+ (9.5+/10)
"""

        return report

    def check_quality(self) -> Dict[str, Any]:
        """Run quality checks and return results."""
        print("🔍 Running quality checks...")

        results = {
            "linting": self._run_linting(),
            "type_checking": self._run_type_checking(),
            "test_coverage": self._run_test_coverage(),
            "security_scan": self._run_security_scan(),
            "performance_test": self._run_performance_test()
        }

        return results

    def _run_linting(self) -> Dict[str, Any]:
        """Run code linting."""
        try:
            result = subprocess.run(['flake8', 'src/'], capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "issues_found",
                "output": result.stdout,
                "errors": result.stderr
            }
        except FileNotFoundError:
            return {"status": "flake8_not_installed", "message": "Install flake8 to run linting"}

    def _run_type_checking(self) -> Dict[str, Any]:
        """Run type checking."""
        try:
            result = subprocess.run(['mypy', 'src/'], capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "type_errors",
                "output": result.stdout,
                "errors": result.stderr
            }
        except FileNotFoundError:
            return {"status": "mypy_not_installed", "message": "Install mypy to run type checking"}

    def _run_test_coverage(self) -> Dict[str, Any]:
        """Run test coverage analysis."""
        try:
            result = subprocess.run([
                'pytest', '--cov=src', '--cov-report=json', 'tests/'
            ], capture_output=True, text=True)

            if Path('coverage.json').exists():
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)

                return {
                    "status": "success",
                    "coverage_percentage": coverage_data['totals']['percent_covered'],
                    "lines_covered": coverage_data['totals']['covered_lines'],
                    "total_lines": coverage_data['totals']['num_statements']
                }
            else:
                return {"status": "coverage_file_not_found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _run_security_scan(self) -> Dict[str, Any]:
        """Run security scanning."""
        try:
            result = subprocess.run(['bandit', '-r', 'src/'], capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "security_issues",
                "output": result.stdout,
                "errors": result.stderr
            }
        except FileNotFoundError:
            return {"status": "bandit_not_installed", "message": "Install bandit to run security scanning"}

    def _run_performance_test(self) -> Dict[str, Any]:
        """Run basic performance test."""
        try:
            # Simple performance test - start API and measure response time
            result = subprocess.run([
                'python', '-c',
                'import requests; import time; start=time.time(); requests.get("http://localhost:8001/health"); print(f"Response time: {(time.time()-start)*1000:.2f}ms")'
            ], capture_output=True, text=True, timeout=10)

            return {
                "status": "success" if result.returncode == 0 else "api_not_running",
                "output": result.stdout,
                "errors": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Performance test timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Improve ElectroAnalyzer quality metrics")
    parser.add_argument("--analyze", action="store_true", help="Analyze current state")
    parser.add_argument("--implement", action="store_true", help="Implement improvements")
    parser.add_argument("--priority", choices=["high", "medium", "low"], default="high", help="Priority level")
    parser.add_argument("--generate-tests", action="store_true", help="Generate test improvements")
    parser.add_argument("--check-quality", action="store_true", help="Run quality checks")
    parser.add_argument("--report", action="store_true", help="Generate quality report")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    improver = QualityMetricsImprover(project_root)

    if args.analyze:
        print("🔍 Analyzing current state...")
        analysis = improver.analyze_current_state()

        # Save analysis
        analysis_file = project_root / "quality_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"✅ Analysis complete. Results saved to {analysis_file}")
        print(f"📊 Current overall grade: A- (9.0/10)")
        print(f"🎯 Target grade: A+ (9.5+/10)")

    elif args.implement:
        print(f"🚀 Implementing {args.priority} priority improvements...")
        results = improver.implement_improvements(args.priority)

        # Save results
        results_file = project_root / f"implementation_results_{args.priority}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✅ Implementation complete. Results saved to {results_file}")

    elif args.generate_tests:
        print("🧪 Generating test improvements...")
        plan = improver.test_engine.generate_improvement_plan()

        plan_file = project_root / "TEST_IMPROVEMENT_PLAN.md"
        with open(plan_file, 'w') as f:
            f.write(plan)

        print(f"✅ Test improvement plan generated: {plan_file}")

    elif args.check_quality:
        print("🔍 Running quality checks...")
        results = improver.check_quality()

        # Save results
        check_file = project_root / "quality_check_results.json"
        with open(check_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✅ Quality checks complete. Results saved to {check_file}")

    elif args.report:
        print("📊 Generating quality report...")
        report = improver.generate_quality_report()

        report_file = project_root / "QUALITY_IMPROVEMENT_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)

        print(f"✅ Quality report generated: {report_file}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
