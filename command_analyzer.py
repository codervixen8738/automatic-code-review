"""
Command Line Prompt Analyzer
Analyzes command-line prompts for security issues, best practices, and common mistakes
"""

import re
import ast

def analyze_command(command):
    """
    Analyze a command-line prompt for security issues and best practices

    Args:
        command (str): The command line prompt to analyze

    Returns:
        dict: Analysis results with issues, suggestions, and risk level
    """
    issues = []
    suggestions = []
    risk_level = "LOW"

    # Check if this looks like Python code
    if _looks_like_python(command):
        python_issues = _analyze_python_syntax(command)
        issues.extend(python_issues)
        if python_issues:
            risk_level = "MEDIUM"  # Syntax errors are medium risk

    # Common dangerous commands and patterns
    dangerous_patterns = [
        (r'rm\s+-rf\s+/', 'DANGER', 'Using rm -rf on root directory can delete entire system'),
        (r'rm\s+-rf\s+\*', 'DANGER', 'Using rm -rf * can delete all files in current directory'),
        (r'rm\s+-rf\s+/home', 'HIGH', 'Deleting /home directory affects all user data'),
        (r'chmod\s+777\s+', 'MEDIUM', 'Setting permissions to 777 gives full access to everyone'),
        (r'sudo\s+.*rm\s+-rf', 'CRITICAL', 'Combining sudo with rm -rf is extremely dangerous'),
        (r'>\s*/dev/sd[a-z]', 'CRITICAL', 'Writing to disk device can destroy partition'),
        (r'dd\s+if=.*of=/dev/sd[a-z]', 'CRITICAL', 'dd command can overwrite entire disks'),
        (r'curl\s+.*\|\s*bash', 'HIGH', 'Piping curl output to bash can execute malicious code'),
        (r'wget\s+.*\|\s*bash', 'HIGH', 'Piping wget output to bash can execute malicious code'),
        (r'ssh\s+.*-o\s+StrictHostKeyChecking=no', 'MEDIUM', 'Disabling host key checking is insecure'),
        (r'mysql\s+.*-p\s*[^-]', 'MEDIUM', 'Password in command line is visible in process list'),
        (r'psql\s+.*-W', 'MEDIUM', 'Password prompt might be insecure'),
        (r'find\s+.*-exec\s+rm', 'MEDIUM', 'find with -exec rm can be dangerous if not careful'),
        (r'chown\s+.*:\s*', 'LOW', 'Changing ownership - verify target is correct'),
        (r'mount\s+.*remount', 'MEDIUM', 'Remounting can affect system stability'),
    ]

    # Best practice checks
    best_practices = [
        (r'cp\s+.*\s+.*', 'Consider using rsync for large file operations'),
        (r'tar\s+.*', 'Consider using pigz for faster compression'),
        (r'grep\s+.*', 'Consider using ripgrep (rg) for faster searching'),
        (r'find\s+.*', 'Consider using fd for faster file finding'),
        (r'ls\s+-la', 'Consider using exa or lsd for better output'),
        (r'cat\s+.*\|\s*grep', 'Consider using grep directly on files'),
        (r'ps\s+aux', 'Consider using htop or btop for better process monitoring'),
    ]

    # Check for dangerous patterns
    for pattern, risk, message in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            issues.append({
                'type': 'SECURITY',
                'risk': risk,
                'message': message,
                'command_part': re.findall(pattern, command, re.IGNORECASE)[0]
            })
            if risk == 'CRITICAL':
                risk_level = 'CRITICAL'
            elif risk == 'HIGH' and risk_level != 'CRITICAL':
                risk_level = 'HIGH'
            elif risk == 'MEDIUM' and risk_level not in ['CRITICAL', 'HIGH']:
                risk_level = 'MEDIUM'

    # Check for best practices
    for pattern, suggestion in best_practices:
        if re.search(pattern, command, re.IGNORECASE):
            suggestions.append(suggestion)

    # Additional checks
    if 'sudo' in command.lower():
        if not any(word in command.lower() for word in ['apt', 'yum', 'dnf', 'pacman', 'systemctl']):
            suggestions.append('Verify if sudo is necessary for this command')

    if '|' in command:
        suggestions.append('Consider breaking complex piped commands into separate steps for clarity')

    if len(command.split()) > 10:
        suggestions.append('Command is quite long - consider using a script for complex operations')

    # Check for common typos
    common_typos = {
        'gerp': 'grep',
        'cd..': 'cd ..',
        'cd/': 'cd /',
        'ls-la': 'ls -la',
        'ps-aux': 'ps aux',
        'top|': 'top |',
    }

    for typo, correction in common_typos.items():
        if typo in command:
            issues.append({
                'type': 'TYPO',
                'risk': 'LOW',
                'message': f'Possible typo: {typo} should be {correction}',
                'command_part': typo
            })

    # Determine if this is Python code
    is_code = _looks_like_python(command)

    # Generate corrected code if it's Python
    corrected_code = ""
    if is_code:
        corrected_code = _generate_corrected_code(command)

    return {
        'command': command,
        'issues': issues,
        'suggestions': suggestions,
        'risk_level': risk_level,
        'total_issues': len(issues),
        'total_suggestions': len(suggestions),
        'is_code': is_code,
        'corrected_code': corrected_code
    }

def _looks_like_python(command):
    """Check if the command looks like Python code"""
    command = command.strip()
    # Common Python indicators
    python_indicators = [
        'print(',
        'print ',
        'def ',
        'class ',
        'import ',
        'from ',
        'if ',
        'for ',
        'while ',
        'try:',
        'except:',
        'with ',
        '.py',
        'len(',
        'str(',
        'int(',
        'list(',
        'dict(',
    ]

    return any(indicator in command for indicator in python_indicators)

def _analyze_python_syntax(command):
    """Analyze Python code for syntax errors"""
    issues = []

    try:
        ast.parse(command)
        # If we get here, syntax is valid, but check for common mistakes

        # Check for print statements without parentheses (Python 2 style)
        if re.search(r'\bprint\s+\w+', command):
            issues.append({
                'type': 'SYNTAX',
                'risk': 'MEDIUM',
                'message': 'Python 3 requires parentheses for print statements: print("hello")',
                'command_part': re.findall(r'\bprint\s+\w+', command)[0]
            })

        # Check for print() without quotes around string literals
        if re.search(r'print\([^"\']*\w+[^"\']*\)', command):
            print_match = re.findall(r'print\([^)]+\)', command)[0]
            if not ('"' in print_match or "'" in print_match):
                issues.append({
                    'type': 'SYNTAX',
                    'risk': 'MEDIUM',
                    'message': 'String literals in print statements should be enclosed in quotes',
                    'command_part': print_match
                })

    except SyntaxError as e:
        issues.append({
            'type': 'SYNTAX',
            'risk': 'MEDIUM',
            'message': f'Syntax error: {str(e)}',
            'command_part': command
        })
    except Exception as e:
        issues.append({
            'type': 'ERROR',
            'risk': 'MEDIUM',
            'message': f'Python parsing error: {str(e)}',
            'command_part': command
        })

    return issues

def _generate_corrected_code(command):
    """Generate corrected version of Python code"""
    corrected_code = command

    # Apply basic corrections
    lines = corrected_code.split('\n')
    corrected_lines = []

    for i, line in enumerate(lines):
        corrected_lines.append(line)

        # Check if this is a function/class definition without docstring
        stripped = line.strip()
        if stripped.startswith('def ') or stripped.startswith('class '):
            # Check if next non-empty line is a docstring
            has_docstring = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith(' ') and not next_line.startswith('\t'):
                    break
                if next_line.startswith('"""') or next_line.startswith("'''"):
                    has_docstring = True
                    break

            if not has_docstring:
                indent = len(line) - len(line.lstrip())
                corrected_lines.append(' ' * indent + '    """')
                if stripped.startswith('def '):
                    corrected_lines.append(' ' * indent + '    Function description.')
                else:
                    corrected_lines.append(' ' * indent + '    Class description.')
                corrected_lines.append(' ' * indent + '    """')

    return '\n'.join(corrected_lines)
