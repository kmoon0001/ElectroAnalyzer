"""Code Quality Enhancement Utilities

Provides tools for improving code quality:
- Type hint validation
- Code complexity analysis
- Function documentation enhancement
- Code style improvements
"""

import ast
import inspect
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import re
from dataclasses import dataclass

@dataclass
class CodeQualityMetrics:
    """Code quality metrics for a file."""
    file_path: str
    lines_of_code: int
    functions_count: int
    classes_count: int
    type_hint_coverage: float
    docstring_coverage: float
    cyclomatic_complexity: int
    maintainability_index: float

class TypeHintAnalyzer:
    """Analyzes and improves type hints."""

    def __init__(self):
        self.missing_hints: Dict[str, List[str]] = {}
        self.improvement_suggestions: Dict[str, List[str]] = {}

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for type hint coverage."""
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError as e:
                return {"error": f"Syntax error: {e}"}

        analysis = {
            'file_path': str(file_path),
            'total_functions': 0,
            'functions_with_type_hints': 0,
            'total_classes': 0,
            'classes_with_type_hints': 0,
            'missing_hints': [],
            'suggestions': []
        }

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                analysis['total_functions'] += 1
                if self._has_complete_type_hints(node):
                    analysis['functions_with_type_hints'] += 1
                else:
                    missing = self._get_missing_type_hints(node)
                    analysis['missing_hints'].append({
                        'type': 'function',
                        'name': node.name,
                        'line': node.lineno,
                        'missing': missing,
                        'suggestion': self._suggest_type_hints(node)
                    })

            elif isinstance(node, ast.ClassDef):
                analysis['total_classes'] += 1
                if self._has_class_type_hints(node):
                    analysis['classes_with_type_hints'] += 1

        return analysis

    def _has_complete_type_hints(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has complete type hints."""
        # Check return annotation
        has_return_annotation = func_node.returns is not None

        # Check parameter annotations
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

        # Check for type annotations in class body
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign):
                return True

        return False

    def _get_missing_type_hints(self, func_node: ast.FunctionDef) -> List[str]:
        """Get list of missing type hints."""
        missing = []

        # Check parameters
        for arg in func_node.args.args:
            if arg.annotation is None:
                missing.append(f"parameter '{arg.arg}'")

        # Check return type
        if func_node.returns is None:
            missing.append("return type")

        return missing

    def _suggest_type_hints(self, func_node: ast.FunctionDef) -> str:
        """Suggest type hints for a function."""
        suggestions = []

        # Analyze function body to infer types
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['str', 'int', 'float', 'bool']:
                        suggestions.append(f"Return type: {node.func.id}")
                    elif node.func.id in ['list', 'dict', 'set']:
                        suggestions.append(f"Return type: {node.func.id}")

        # Check for common patterns
        if 'return' in [n.value for n in ast.walk(func_node) if isinstance(n, ast.Return)]:
            suggestions.append("Add return type annotation")

        return "; ".join(suggestions) if suggestions else "Add type annotations"

class ComplexityAnalyzer:
    """Analyzes code complexity."""

    def calculate_cyclomatic_complexity(self, file_path: Path) -> int:
        """Calculate cyclomatic complexity for a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return 0

        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp):
                complexity += 1

        return complexity

    def get_complex_functions(self, file_path: Path, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get functions with complexity above threshold."""
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return []

        complex_functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_complexity = self._calculate_function_complexity(node)
                if func_complexity > threshold:
                    complex_functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'complexity': func_complexity,
                        'suggestion': self._suggest_complexity_reduction(node)
                    })

        return complex_functions

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate complexity for a single function."""
        complexity = 1

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _suggest_complexity_reduction(self, func_node: ast.FunctionDef) -> str:
        """Suggest ways to reduce complexity."""
        suggestions = []

        # Count different complexity contributors
        if_count = sum(1 for node in ast.walk(func_node) if isinstance(node, ast.If))
        loop_count = sum(1 for node in ast.walk(func_node) if isinstance(node, (ast.For, ast.While)))
        except_count = sum(1 for node in ast.walk(func_node) if isinstance(node, ast.ExceptHandler))

        if if_count > 5:
            suggestions.append("Consider using strategy pattern for multiple conditions")
        if loop_count > 3:
            suggestions.append("Consider breaking down nested loops")
        if except_count > 2:
            suggestions.append("Consider consolidating exception handling")

        if not suggestions:
            suggestions.append("Consider breaking function into smaller functions")

        return "; ".join(suggestions)

class DocumentationEnhancer:
    """Enhances function documentation."""

    def analyze_documentation(self, file_path: Path) -> Dict[str, Any]:
        """Analyze documentation coverage."""
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return {"error": "Syntax error"}

        analysis = {
            'total_functions': 0,
            'documented_functions': 0,
            'total_classes': 0,
            'documented_classes': 0,
            'missing_docs': []
        }

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                analysis['total_functions'] += 1
                if ast.get_docstring(node):
                    analysis['documented_functions'] += 1
                else:
                    analysis['missing_docs'].append({
                        'type': 'function',
                        'name': node.name,
                        'line': node.lineno
                    })

            elif isinstance(node, ast.ClassDef):
                analysis['total_classes'] += 1
                if ast.get_docstring(node):
                    analysis['documented_classes'] += 1
                else:
                    analysis['missing_docs'].append({
                        'type': 'class',
                        'name': node.name,
                        'line': node.lineno
                    })

        return analysis

    def generate_docstring_template(self, func_node: ast.FunctionDef) -> str:
        """Generate docstring template for a function."""
        func_name = func_node.name

        # Analyze parameters
        params = []
        for arg in func_node.args.args:
            param_type = "Any"  # Default type
            if arg.annotation:
                param_type = ast.unparse(arg.annotation)
            params.append(f"    {arg.arg} ({param_type}): Description of {arg.arg}")

        # Analyze return type
        return_type = "Any"
        if func_node.returns:
            return_type = ast.unparse(func_node.returns)

        docstring = f'''"""
{self._generate_function_description(func_name)}.

Args:
{chr(10).join(params)}

Returns:
    {return_type}: Description of return value

Raises:
    ValueError: If input is invalid
    RuntimeError: If operation fails
"""'''

        return docstring

    def _generate_function_description(self, func_name: str) -> str:
        """Generate description based on function name."""
        # Convert snake_case to readable description
        words = func_name.split('_')
        description = ' '.join(word.capitalize() for word in words)

        # Add common patterns
        if func_name.startswith('get_'):
            return f"Get {description[4:].lower()}"
        elif func_name.startswith('set_'):
            return f"Set {description[4:].lower()}"
        elif func_name.startswith('is_'):
            return f"Check if {description[3:].lower()}"
        elif func_name.startswith('has_'):
            return f"Check if has {description[4:].lower()}"
        else:
            return description

class CodeQualityEnhancer:
    """Main class for enhancing code quality."""

    def __init__(self):
        self.type_analyzer = TypeHintAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.doc_enhancer = DocumentationEnhancer()

    def analyze_file(self, file_path: Path) -> CodeQualityMetrics:
        """Analyze a file for code quality metrics."""
        # Type hint analysis
        type_analysis = self.type_analyzer.analyze_file(file_path)

        # Documentation analysis
        doc_analysis = self.doc_enhancer.analyze_documentation(file_path)

        # Complexity analysis
        complexity = self.complexity_analyzer.calculate_cyclomatic_complexity(file_path)

        # Calculate coverage percentages
        type_coverage = (
            type_analysis['functions_with_type_hints'] /
            max(type_analysis['total_functions'], 1)
        )

        doc_coverage = (
            doc_analysis['documented_functions'] /
            max(doc_analysis['total_functions'], 1)
        )

        # Calculate maintainability index (simplified)
        maintainability = max(0, 100 - (complexity * 2) - ((1 - type_coverage) * 30) - ((1 - doc_coverage) * 20))

        return CodeQualityMetrics(
            file_path=str(file_path),
            lines_of_code=self._count_lines(file_path),
            functions_count=type_analysis['total_functions'],
            classes_count=type_analysis['total_classes'],
            type_hint_coverage=type_coverage,
            docstring_coverage=doc_coverage,
            cyclomatic_complexity=complexity,
            maintainability_index=maintainability
        )

    def _count_lines(self, file_path: Path) -> int:
        """Count lines of code in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except Exception:
            return 0

    def generate_improvement_suggestions(self, file_path: Path) -> List[str]:
        """Generate improvement suggestions for a file."""
        suggestions = []

        # Type hint suggestions
        type_analysis = self.type_analyzer.analyze_file(file_path)
        if type_analysis['missing_hints']:
            suggestions.append(f"Add type hints to {len(type_analysis['missing_hints'])} functions")

        # Complexity suggestions
        complex_functions = self.complexity_analyzer.get_complex_functions(file_path)
        if complex_functions:
            suggestions.append(f"Reduce complexity in {len(complex_functions)} functions")

        # Documentation suggestions
        doc_analysis = self.doc_enhancer.analyze_documentation(file_path)
        if doc_analysis['missing_docs']:
            suggestions.append(f"Add documentation to {len(doc_analysis['missing_docs'])} functions/classes")

        return suggestions

    def analyze_codebase(self, src_path: Path) -> Dict[str, Any]:
        """Analyze entire codebase for quality improvements."""
        python_files = list(src_path.rglob('*.py'))

        analysis = {
            'files_analyzed': len(python_files),
            'total_metrics': {
                'lines_of_code': 0,
                'functions_count': 0,
                'classes_count': 0,
                'type_hint_coverage': 0,
                'docstring_coverage': 0,
                'cyclomatic_complexity': 0,
                'maintainability_index': 0
            },
            'file_metrics': [],
            'improvement_priorities': []
        }

        for file_path in python_files:
            try:
                metrics = self.analyze_file(file_path)
                analysis['file_metrics'].append(metrics)

                # Aggregate metrics
                analysis['total_metrics']['lines_of_code'] += metrics.lines_of_code
                analysis['total_metrics']['functions_count'] += metrics.functions_count
                analysis['total_metrics']['classes_count'] += metrics.classes_count
                analysis['total_metrics']['cyclomatic_complexity'] += metrics.cyclomatic_complexity

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        # Calculate averages
        if analysis['file_metrics']:
            analysis['total_metrics']['type_hint_coverage'] = sum(
                m.type_hint_coverage for m in analysis['file_metrics']
            ) / len(analysis['file_metrics'])

            analysis['total_metrics']['docstring_coverage'] = sum(
                m.docstring_coverage for m in analysis['file_metrics']
            ) / len(analysis['file_metrics'])

            analysis['total_metrics']['maintainability_index'] = sum(
                m.maintainability_index for m in analysis['file_metrics']
            ) / len(analysis['file_metrics'])

        # Identify improvement priorities
        for metrics in analysis['file_metrics']:
            if metrics.type_hint_coverage < 0.8:
                analysis['improvement_priorities'].append({
                    'file': metrics.file_path,
                    'priority': 'high',
                    'issue': 'low_type_hint_coverage',
                    'score': metrics.type_hint_coverage
                })

            if metrics.cyclomatic_complexity > 15:
                analysis['improvement_priorities'].append({
                    'file': metrics.file_path,
                    'priority': 'high',
                    'issue': 'high_complexity',
                    'score': metrics.cyclomatic_complexity
                })

            if metrics.docstring_coverage < 0.7:
                analysis['improvement_priorities'].append({
                    'file': metrics.file_path,
                    'priority': 'medium',
                    'issue': 'low_docstring_coverage',
                    'score': metrics.docstring_coverage
                })

        return analysis
