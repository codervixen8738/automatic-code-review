import subprocess
import json
import radon.complexity as radon_complexity
import radon.metrics as radon_metrics
import ast
import os

def analyze_code(filepath):
    issues = []
    suggestions = []
    score = 100  # Start with perfect score

    # Run pylint
    try:
        result = subprocess.run(['pylint', '--output-format=json', filepath],
                              capture_output=True, text=True)
        pylint_output = json.loads(result.stdout)
        for issue in pylint_output:
            issues.append({
                'type': issue['type'],
                'message': issue['message'],
                'line': issue['line']
            })
            # Deduct points based on severity
            if issue['type'] == 'error':
                score -= 10
            elif issue['type'] == 'warning':
                score -= 5
            else:
                score -= 2
    except Exception as e:
        issues.append({'type': 'error', 'message': f'Pylint failed: {str(e)}', 'line': 0})

    # Analyze complexity with radon
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        complexity = radon_complexity.cc_visit(code)
        for func in complexity:
            if func.complexity > 10:
                issues.append({
                    'type': 'warning',
                    'message': f'High complexity in {func.name}: {func.complexity}',
                    'line': func.lineno
                })
                score -= 5
                suggestions.append(f'Refactor {func.name} to reduce complexity')

        # Raw metrics
        raw_metrics = radon_metrics.raw_metrics(code)
        if raw_metrics.loc > 100:  # Lines of code
            issues.append({'type': 'info', 'message': f'File is quite long: {raw_metrics.loc} lines', 'line': 0})
            score -= 5
            suggestions.append('Consider breaking down the file into smaller modules')
    except Exception as e:
        issues.append({'type': 'error', 'message': f'Complexity analysis failed: {str(e)}', 'line': 0})

    # Basic AST analysis for naming conventions
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower() or '_' not in node.name:
                    issues.append({
                        'type': 'warning',
                        'message': f'Function name {node.name} does not follow snake_case convention',
                        'line': node.lineno
                    })
                    score -= 2
                    suggestions.append(f'Rename {node.name} to follow snake_case')
            elif isinstance(node, ast.ClassDef):
                if not node.name.istitle():
                    issues.append({
                        'type': 'warning',
                        'message': f'Class name {node.name} does not follow PascalCase convention',
                        'line': node.lineno
                    })
                    score -= 2
                    suggestions.append(f'Rename {node.name} to follow PascalCase')
    except SyntaxError as e:
        issues.append({'type': 'error', 'message': f'Syntax error: {str(e)}', 'line': e.lineno})
        score -= 20

    score = max(0, score)  # Ensure score doesn't go below 0

    # Read code lines for display
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code_lines = f.read().splitlines()
    except Exception as e:
        code_lines = []

    return {
        'filename': os.path.basename(filepath),
        'issues': issues,
        'score': score,
        'suggestions': suggestions,
        'code_lines': code_lines,
        'line_suggestions': {}  # For future enhancement
    }
