"""Code Quality Enhancement Utilities

Provides tools for improving code quality through:
- Type hint validation
- Documentation generation
- Code complexity analysis
- Performance profiling
"""

from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from dataclasses import dataclass
from pathlib import Path
import ast
import inspect
import time
import functools
from collections import defaultdict

T = TypeVar('T')

@dataclass
class CodeQualityMetrics:
    """Code quality metrics for a module."""
    file_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    type_hint_coverage: float
    docstring_coverage: float
    test_coverage: float
    performance_score: float

class TypeHintValidator:
    """Validates and improves type hints across the codebase."""

    def __init__(self):
        self.missing_type_hints = defaultdict(list)
        self.improvement_suggestions = defaultdict(list)

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for type hint coverage."""
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        analysis = {
            'total_functions': 0,
            'functions_with_type_hints': 0,
            'total_classes': 0,
            'classes_with_type_hints': 0,
            'missing_hints': [],
            'suggestions': []
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis['total_functions'] += 1
                if self._has_complete_type_hints(node):
                    analysis['functions_with_type_hints'] += 1
                else:
                    analysis['missing_hints'].append({
                        'type': 'function',
                        'name': node.name,
                        'line': node.lineno,
                        'suggestion': self._suggest_type_hints(node)
                    })

            elif isinstance(node, ast.ClassDef):
                analysis['total_classes'] += 1
                if self._has_class_type_hints(node):
                    analysis['classes_with_type_hints'] += 1

        return analysis

    def _has_complete_type_hints(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has complete type hints."""
        has_return_annotation = func_node.returns is not None
        has_param_annotations = all(
            arg.annotation is not None for arg in func_node.args.args
        )
        return has_return_annotation and has_param_annotations

    def _has_class_type_hints(self, class_node: ast.ClassDef) -> bool:
        """Check if class has type hints for attributes."""
        # Check for dataclass or TypedDict usage
        for decorator in class_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in ['dataclass', 'TypedDict']:
                return True
        return False

    def _suggest_type_hints(self, func_node: ast.FunctionDef) -> str:
        """Suggest type hints for a function."""
        suggestions = []

        # Analyze function body to infer types
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['str', 'int', 'float', 'bool']:
                        suggestions.append(f"Return type: {node.func.id}")

        return "; ".join(suggestions) if suggestions else "Add return type annotation"

class DocumentationGenerator:
    """Generates comprehensive documentation for modules."""

    def generate_module_docstring(self, module_path: Path) -> str:
        """Generate comprehensive module docstring."""
        module_name = module_path.stem

        return f'''"""
{module_name.title()} Module

This module provides [module functionality description].

## Classes
[Auto-generated class list]

## Functions
[Auto-generated function list]

## Examples
```python
# Basic usage example
from {module_path.parent.name}.{module_name} import MainClass

instance = MainClass()
result = instance.main_method()
```

## Performance Notes
- Average execution time: [calculated]
- Memory usage: [calculated]
- Thread safety: [analyzed]

## Dependencies
- [dependency list]

## Version History
- v1.0.0: Initial implementation
- v1.1.0: Performance improvements
"""

'''

class PerformanceProfiler:
    """Profiles function performance and suggests optimizations."""

    def __init__(self):
        self.profiles = defaultdict(list)

    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile function performance."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = self._get_memory_usage()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                end_memory = self._get_memory_usage()

                profile_data = {
                    'function': func.__name__,
                    'execution_time': end_time - start_time,
                    'memory_delta': end_memory - start_memory,
                    'timestamp': time.time()
                }

                self.profiles[func.__name__].append(profile_data)

        return wrapper

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        report = {}

        for func_name, profiles in self.profiles.items():
            if not profiles:
                continue

            execution_times = [p['execution_time'] for p in profiles]
            memory_deltas = [p['memory_delta'] for p in profiles]

            report[func_name] = {
                'call_count': len(profiles),
                'avg_execution_time': sum(execution_times) / len(execution_times),
                'max_execution_time': max(execution_times),
                'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
                'max_memory_delta': max(memory_deltas),
                'performance_score': self._calculate_performance_score(execution_times, memory_deltas)
            }

        return report

    def _calculate_performance_score(self, execution_times: List[float], memory_deltas: List[float]) -> float:
        """Calculate performance score (0-100)."""
        # Normalize execution time (lower is better)
        time_score = max(0, 100 - (sum(execution_times) / len(execution_times)) * 1000)

        # Normalize memory usage (lower is better)
        memory_score = max(0, 100 - abs(sum(memory_deltas) / len(memory_deltas)) * 10)

        return (time_score + memory_score) / 2

class CodeComplexityAnalyzer:
    """Analyzes code complexity and suggests refactoring."""

    def calculate_cyclomatic_complexity(self, file_path: Path) -> int:
        """Calculate cyclomatic complexity for a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def suggest_refactoring(self, file_path: Path) -> List[str]:
        """Suggest refactoring improvements."""
        suggestions = []
        complexity = self.calculate_cyclomatic_complexity(file_path)

        if complexity > 10:
            suggestions.append("Consider breaking down complex functions into smaller ones")

        if complexity > 20:
            suggestions.append("High complexity detected - refactoring strongly recommended")

        # Analyze for other patterns
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.count('if') > 10:
            suggestions.append("Consider using strategy pattern for multiple conditions")

        if content.count('for') > 5:
            suggestions.append("Consider using list comprehensions or generator expressions")

        return suggestions

class QualityImprovementEngine:
    """Main engine for improving code quality."""

    def __init__(self):
        self.type_validator = TypeHintValidator()
        self.doc_generator = DocumentationGenerator()
        self.profiler = PerformanceProfiler()
        self.complexity_analyzer = CodeComplexityAnalyzer()

    def analyze_codebase(self, src_path: Path) -> Dict[str, Any]:
        """Analyze entire codebase for quality improvements."""
        analysis = {
            'files_analyzed': 0,
            'total_issues': 0,
            'type_hint_coverage': 0,
            'docstring_coverage': 0,
            'performance_score': 0,
            'complexity_score': 0,
            'recommendations': []
        }

        python_files = list(src_path.rglob('*.py'))
        analysis['files_analyzed'] = len(python_files)

        total_type_coverage = 0
        total_doc_coverage = 0
        total_performance = 0
        total_complexity = 0

        for file_path in python_files:
            # Type hint analysis
            type_analysis = self.type_validator.analyze_file(file_path)
            type_coverage = (
                type_analysis['functions_with_type_hints'] /
                max(type_analysis['total_functions'], 1)
            )
            total_type_coverage += type_coverage

            # Documentation analysis
            doc_coverage = self._analyze_documentation(file_path)
            total_doc_coverage += doc_coverage

            # Complexity analysis
            complexity = self.complexity_analyzer.calculate_cyclomatic_complexity(file_path)
            complexity_score = max(0, 100 - complexity * 5)  # Lower complexity = higher score
            total_complexity += complexity_score

            # Collect recommendations
            if type_coverage < 0.8:
                analysis['recommendations'].append(
                    f"Improve type hints in {file_path.relative_to(src_path)}"
                )

            if doc_coverage < 0.7:
                analysis['recommendations'].append(
                    f"Add documentation to {file_path.relative_to(src_path)}"
                )

            if complexity > 15:
                analysis['recommendations'].append(
                    f"Reduce complexity in {file_path.relative_to(src_path)}"
                )

        # Calculate averages
        analysis['type_hint_coverage'] = total_type_coverage / len(python_files)
        analysis['docstring_coverage'] = total_doc_coverage / len(python_files)
        analysis['complexity_score'] = total_complexity / len(python_files)
        analysis['total_issues'] = len(analysis['recommendations'])

        return analysis

    def _analyze_documentation(self, file_path: Path) -> float:
        """Analyze documentation coverage for a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        total_functions = 0
        documented_functions = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_functions += 1
                if ast.get_docstring(node):
                    documented_functions += 1

        return documented_functions / max(total_functions, 1)

    def generate_improvement_plan(self, analysis: Dict[str, Any]) -> str:
        """Generate actionable improvement plan."""
        plan = f"""
# Code Quality Improvement Plan

## Current Status
- Files Analyzed: {analysis['files_analyzed']}
- Type Hint Coverage: {analysis['type_hint_coverage']:.1%}
- Documentation Coverage: {analysis['docstring_coverage']:.1%}
- Complexity Score: {analysis['complexity_score']:.1f}/100
- Total Issues: {analysis['total_issues']}

## Priority Actions

### High Priority (Week 1)
"""

        high_priority = [rec for rec in analysis['recommendations']
                        if 'type hints' in rec.lower()][:5]
        for rec in high_priority:
            plan += f"- {rec}\n"

        plan += """
### Medium Priority (Week 2-3)
"""

        medium_priority = [rec for rec in analysis['recommendations']
                          if 'documentation' in rec.lower()][:5]
        for rec in medium_priority:
            plan += f"- {rec}\n"

        plan += """
### Low Priority (Week 4)
"""

        low_priority = [rec for rec in analysis['recommendations']
                       if 'complexity' in rec.lower()][:5]
        for rec in low_priority:
            plan += f"- {rec}\n"

        plan += """
## Implementation Tools

### Type Hints
```python
# Use this tool to add type hints
from src.utils.quality_improvement import TypeHintValidator
validator = TypeHintValidator()
validator.analyze_file(Path("src/core/analysis_service.py"))
```

### Documentation
```python
# Use this tool to generate documentation
from src.utils.quality_improvement import DocumentationGenerator
doc_gen = DocumentationGenerator()
docstring = doc_gen.generate_module_docstring(Path("src/core/analysis_service.py"))
```

### Performance Profiling
```python
# Use this decorator to profile functions
from src.utils.quality_improvement import PerformanceProfiler
profiler = PerformanceProfiler()

@profiler.profile_function
def your_function():
    # Your code here
    pass
```
"""

        return plan
