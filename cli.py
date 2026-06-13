#!/usr/bin/env python3
"""
Command Line Interface for Code Review System
Provides line-by-line analysis and suggestions for Python files
Also supports command-line prompt analysis and code execution
"""

import argparse
import sys
import os
import subprocess
import tempfile

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer import analyze_code
from command_analyzer import analyze_command
from report_generator import generate_txt_report, generate_pdf_report

def print_colored(text, color):
    """Print colored text in terminal"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")

def display_analysis(result):
    """Display analysis results in CLI format"""
    print(f"\n{'='*60}")
    print(f"Code Review Analysis for: {result['filename']}")
    print(f"Quality Score: {result['score']}/100")
    print(f"{'='*60}\n")

    # Display issues summary
    if result['issues']:
        print("ISSUES FOUND:")
        for issue in result['issues']:
            color = {'error': 'red', 'warning': 'yellow', 'info': 'blue'}.get(issue['type'], 'reset')
            print_colored(f"  Line {issue['line']}: {issue['type'].upper()} - {issue['message']}", color)
        print()
    else:
        print_colored("✓ No issues found!", 'green')
        print()

    # Display suggestions
    if result['suggestions']:
        print("SUGGESTIONS:")
        for suggestion in result['suggestions']:
            print(f"  • {suggestion}")
        print()

    # Display code with line-by-line suggestions
    print("SOURCE CODE WITH LINE-BY-LINE ANALYSIS:")
    print("-" * 60)

    for i, line in enumerate(result['code_lines'], 1):
        # Print line number and code
        line_str = f"{i:3d}: {line.rstrip()}"
        print(line_str)

        # Print suggestions for this line
        if i in result['line_suggestions']:
            for suggestion in result['line_suggestions'][i]:
                color = {'ERROR': 'red', 'WARNING': 'yellow', 'INFO': 'blue'}.get(suggestion.split(':')[0], 'reset')
                print_colored(f"      → {suggestion}", color)

    print(f"\n{'='*60}")

def display_command_analysis(result):
    """Display command analysis results in CLI format"""
    print(f"\n{'='*60}")
    print(f"Command Analysis: {result['command'][:50]}{'...' if len(result['command']) > 50 else ''}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Issues: {result['total_issues']} | Suggestions: {result['total_suggestions']}")
    print(f"{'='*60}\n")

    # Display issues
    if result['issues']:
        print("ISSUES FOUND:")
        for issue in result['issues']:
            risk_color = {'CRITICAL': 'red', 'HIGH': 'red', 'MEDIUM': 'yellow', 'LOW': 'blue'}.get(issue.get('risk', 'LOW'), 'reset')
            print_colored(f"  [{issue.get('risk', 'LOW')}] {issue['type']}: {issue['message']}", risk_color)
            if 'command_part' in issue:
                print_colored(f"      → Problematic part: {issue['command_part']}", 'yellow')
        print()

    # Display suggestions
    if result['suggestions']:
        print("SUGGESTIONS:")
        for suggestion in result['suggestions']:
            print(f"  • {suggestion}")
        print()

    print(f"{'='*60}")

def execute_code_cli(code):
    """Execute Python code in CLI and display results with analysis"""
    print(f"\n{'='*80}")
    print("CODE EXECUTION & ANALYSIS")
    print(f"{'='*80}\n")

    # Terminal 1: Original Code
    print("TERMINAL 1 - ORIGINAL CODE:")
    print("-" * 40)
    print(code)
    print("-" * 40)

    # Analyze the code for issues
    print("\nCODE ANALYSIS:")
    print("-" * 40)

    # Create temporary file for analysis
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        # Analyze the code
        analysis_result = analyze_code(temp_file)

        if analysis_result['issues']:
            print("ISSUES FOUND:")
            for issue in analysis_result['issues']:
                color = {'error': 'red', 'warning': 'yellow', 'info': 'blue'}.get(issue['type'], 'reset')
                print_colored(f"  Line {issue['line']}: {issue['type'].upper()} - {issue['message']}", color)
        else:
            print_colored("✓ No issues found in the code!", 'green')

        print(f"\nQuality Score: {analysis_result['score']}/100")

        if analysis_result['suggestions']:
            print("\nSUGGESTIONS:")
            for suggestion in analysis_result['suggestions']:
                print(f"  • {suggestion}")

        # Terminal 2: Corrected/Suggested Code
        print(f"\n{'='*80}")
        print("TERMINAL 2 - SUGGESTED CORRECTIONS:")
        print("-" * 40)

        corrected_code = generate_corrected_code(code, analysis_result)
        if corrected_code != code:
            print(corrected_code)
        else:
            print("No corrections needed - code follows best practices!")

        print("-" * 40)

    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass

    # Terminal 3: Execution Results
    print(f"\n{'='*80}")
    print("TERMINAL 3 - EXECUTION RESULTS:")
    print("-" * 40)

    try:
        # Execute code in a subprocess with timeout for safety
        result = subprocess.run(['python', '-c', code],
                              capture_output=True, text=True, timeout=10)

        if result.stdout:
            print("STDOUT:")
            print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print_colored(result.stderr, 'red')

        print(f"\nReturn Code: {result.returncode}")

    except subprocess.TimeoutExpired:
        print_colored("Error: Code execution timed out (10 seconds limit)", 'red')
    except Exception as e:
        print_colored(f"Error executing code: {str(e)}", 'red')

    print(f"\n{'='*80}")

def generate_corrected_code(original_code, analysis_result):
    """Generate corrected version of the code based on analysis"""
    corrected_code = original_code

    # Apply basic corrections based on issues found
    for issue in analysis_result['issues']:
        if 'snake_case' in issue['message'].lower():
            # Simple snake_case correction (basic implementation)
            if 'Function name' in issue['message']:
                # This is a simplified correction - in practice, you'd need more sophisticated parsing
                pass
        elif 'PascalCase' in issue['message'].lower():
            # Simple PascalCase correction
            pass

    # Add docstrings if missing
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

def main():
    parser = argparse.ArgumentParser(description='Automated Code Review CLI Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # File analysis subcommand
    file_parser = subparsers.add_parser('analyze', help='Analyze a Python file')
    file_parser.add_argument('file', help='Path to Python file to analyze')
    file_parser.add_argument('--score-only', action='store_true', help='Show only the quality score')
    file_parser.add_argument('--report', choices=['txt', 'pdf'], help='Generate a report file')

    # Command analysis subcommand
    cmd_parser = subparsers.add_parser('command', help='Analyze a command-line prompt')
    cmd_parser.add_argument('cmd', help='Command-line prompt to analyze')

    # Code execution subcommand
    exec_parser = subparsers.add_parser('execute', help='Execute Python code')
    exec_parser.add_argument('code', help='Python code to execute')
    exec_parser.add_argument('--file', help='Read code from file instead of command line')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'analyze':
        if not os.path.exists(args.file):
            print_colored(f"Error: File '{args.file}' not found!", 'red')
            sys.exit(1)

        if not args.file.endswith('.py'):
            print_colored("Error: Only Python (.py) files are supported!", 'red')
            sys.exit(1)

        try:
            result = analyze_code(args.file)

            if args.score_only:
                print(f"Quality Score: {result['score']}/100")
            else:
                display_analysis(result)

            # Generate report if requested
            if args.report:
                if args.report == 'txt':
                    report_path = generate_txt_report(result)
                    print(f"\nReport saved to: {report_path}")
                elif args.report == 'pdf':
                    report_path = generate_pdf_report(result)
                    print(f"\nReport saved to: {report_path}")

        except Exception as e:
            print_colored(f"Error analyzing file: {str(e)}", 'red')
            sys.exit(1)

    elif args.command == 'command':
        result = analyze_command(args.cmd)
        display_command_analysis(result)

    elif args.command == 'execute':
        code = args.code
        if args.file:
            if not os.path.exists(args.file):
                print_colored(f"Error: File '{args.file}' not found!", 'red')
                sys.exit(1)
            with open(args.file, 'r') as f:
                code = f.read()

        execute_code_cli(code)

if __name__ == '__main__':
    main()
