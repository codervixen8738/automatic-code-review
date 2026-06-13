from flask import Flask, request, render_template, send_file, jsonify, session
import os
import tempfile
import subprocess
from analyzer import analyze_code
from report_generator import generate_txt_report, generate_pdf_report, generate_command_txt_report, generate_command_pdf_report
from command_analyzer import analyze_command

app = Flask(__name__)
app.secret_key = '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'  # Required for session
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files uploaded'}), 400

    results = []
    for file in files:
        if file and file.filename.endswith('.py'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            result = analyze_code(filepath)
            results.append(result)

    # Store results in session for report generation
    session['last_analysis_results'] = results

    # If only one file, redirect to interactive review
    if len(results) == 1:
        return render_template('interactive_review.html', result=results[0])
    else:
        return render_template('results.html', results=results)

@app.route('/analyze_file')
def analyze_file_page():
    return render_template('analyze_file.html')

@app.route('/analyze_command_input')
def analyze_command_input_page():
    return render_template('analyze_command_input.html')

@app.route('/analyze_command', methods=['POST'])
def analyze_command_route():
    command = request.form.get('command', '').strip()
    if not command:
        return jsonify({'error': 'No command provided'}), 400

    result = analyze_command(command)
    # Store command analysis result in session for report generation
    session['last_command_analysis'] = result
    return render_template('command_results.html', result=result)

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.form.get('code', '').strip()
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    try:
        # Execute code in a subprocess with timeout for safety
        result = subprocess.run(['python', '-c', code],
                              capture_output=True, text=True, timeout=10)
        output = result.stdout
        error = result.stderr
        return_code = result.returncode

        # Format output for display
        formatted_output = ""
        if output:
            formatted_output += f"STDOUT:\n{output}"
        if error:
            if formatted_output:
                formatted_output += "\n"
            formatted_output += f"STDERR:\n{error}"
        if not output and not error:
            formatted_output = "No output generated"

        formatted_output += f"\n\nReturn Code: {return_code}"

        # Return HTML page instead of JSON for better display
        return render_template('code_execution.html',
                             original_code=code,
                             execution_output=formatted_output)

    except subprocess.TimeoutExpired:
        error_output = "Error: Code execution timed out (10 seconds limit)"
        return render_template('code_execution.html',
                             original_code=code,
                             execution_output=error_output)
    except Exception as e:
        error_output = f"Error: Execution failed: {str(e)}"
        return render_template('code_execution.html',
                             original_code=code,
                             execution_output=error_output)

@app.route('/download/<format>')
def download(format):
    # Get the last analyzed results from session
    results = session.get('last_analysis_results', [])
    if not results:
        # Fallback to sample data if no results in session
        sample_result = {
            'filename': 'sample.py',
            'issues': [{'type': 'warning', 'message': 'Sample issue', 'line': 1}],
            'score': 85,
            'suggestions': ['Sample suggestion']
        }
        results = [sample_result]

    # Use the first result (or the only result for single file analysis)
    result = results[0] if results else sample_result

    if format == 'txt':
        report_path = generate_txt_report(result)
        return send_file(report_path, as_attachment=True, download_name='code_review_report.txt')
    elif format == 'pdf':
        report_path = generate_pdf_report(result)
        return send_file(report_path, as_attachment=True, download_name='code_review_report.pdf')
    else:
        return jsonify({'error': 'Invalid format'}), 400

@app.route('/download_command_report/<format>')
def download_command_report(format):
    # Get the last command analysis result from session
    result = session.get('last_command_analysis')
    if not result:
        # Fallback to sample data if no results in session
        sample_result = {
            'command': 'sample command',
            'issues': [{'type': 'security', 'message': 'Sample security issue', 'risk': 'HIGH'}],
            'suggestions': ['Sample suggestion'],
            'risk_level': 'HIGH',
            'total_issues': 1,
            'total_suggestions': 1
        }
        result = sample_result

    if format == 'txt':
        report_path = generate_command_txt_report(result)
        return send_file(report_path, as_attachment=True, download_name='command_analysis_report.txt')
    elif format == 'pdf':
        report_path = generate_command_pdf_report(result)
        return send_file(report_path, as_attachment=True, download_name='command_analysis_report.pdf')
    else:
        return jsonify({'error': 'Invalid format'}), 400

if __name__ == '__main__':
    app.run(debug=True)
