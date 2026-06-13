import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_txt_report(analysis_result):
    report_content = f"Code Review Report for {analysis_result.get('filename', 'Unknown')}\n\n"
    report_content += f"Quality Score: {analysis_result['score']}/100\n\n"
    report_content += "Issues:\n"
    for issue in analysis_result['issues']:
        report_content += f"- {issue['type'].upper()}: {issue['message']} (Line {issue['line']})\n"
    report_content += "\nSuggestions:\n"
    for suggestion in analysis_result['suggestions']:
        report_content += f"- {suggestion}\n"

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(report_content)
    temp_file.close()
    return temp_file.name

def generate_pdf_report(analysis_result):
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Code Review Report for {analysis_result.get('filename', 'Unknown')}", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Quality Score: {analysis_result['score']}/100", styles['Heading2']))
    story.append(Spacer(1, 12))

    if analysis_result['issues']:
        story.append(Paragraph("Issues:", styles['Heading3']))
        for issue in analysis_result['issues']:
            story.append(Paragraph(f"{issue['type'].upper()}: {issue['message']} (Line {issue['line']})", styles['Normal']))
        story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("No issues found.", styles['Normal']))
        story.append(Spacer(1, 12))

    if analysis_result['suggestions']:
        story.append(Paragraph("Suggestions:", styles['Heading3']))
        for suggestion in analysis_result['suggestions']:
            story.append(Paragraph(suggestion, styles['Normal']))
    else:
        story.append(Paragraph("No suggestions.", styles['Normal']))

    doc.build(story)
    return temp_file.name

def generate_command_txt_report(analysis_result):
    report_content = f"Command Line Analysis Report\n\n"
    report_content += f"Analyzed Command: {analysis_result.get('command', 'Unknown')}\n\n"
    report_content += f"Risk Level: {analysis_result.get('risk_level', 'Unknown')}\n"
    report_content += f"Total Issues: {analysis_result.get('total_issues', 0)}\n"
    report_content += f"Total Suggestions: {analysis_result.get('total_suggestions', 0)}\n\n"

    if analysis_result.get('issues'):
        report_content += "Security Issues & Warnings:\n"
        for issue in analysis_result['issues']:
            report_content += f"- {issue['type'].upper()} - {issue.get('risk', 'Unknown')} RISK: {issue['message']}\n"
            if issue.get('command_part'):
                report_content += f"  Problematic part: {issue['command_part']}\n"
        report_content += "\n"

    if analysis_result.get('suggestions'):
        report_content += "Suggestions & Best Practices:\n"
        for suggestion in analysis_result['suggestions']:
            report_content += f"- {suggestion}\n"
        report_content += "\n"

    if analysis_result.get('is_code') and analysis_result.get('corrected_code'):
        report_content += "Code Corrections:\n"
        report_content += "Original Code:\n"
        report_content += f"{analysis_result['command']}\n\n"
        report_content += "Corrected Code:\n"
        report_content += f"{analysis_result['corrected_code']}\n\n"

    report_content += "Conclusion:\n"
    if analysis_result.get('risk_level') in ['CRITICAL', 'HIGH']:
        report_content += "⚠️ HIGH RISK: This command contains serious security issues that should be addressed immediately.\n"
    elif analysis_result.get('risk_level') == 'MEDIUM':
        report_content += "⚡ MEDIUM RISK: This command has some issues that should be reviewed and potentially corrected.\n"
    elif analysis_result.get('risk_level') == 'LOW':
        report_content += "✅ LOW RISK: This command appears relatively safe but always double-check before execution.\n"
    else:
        report_content += "✅ ANALYSIS COMPLETE: No significant issues found.\n"

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(report_content)
    temp_file.close()
    return temp_file.name

def generate_command_pdf_report(analysis_result):
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Command Line Analysis Report", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Analyzed Command: {analysis_result.get('command', 'Unknown')}", styles['Heading2']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Risk Level: {analysis_result.get('risk_level', 'Unknown')}", styles['Heading3']))
    story.append(Paragraph(f"Total Issues: {analysis_result.get('total_issues', 0)} | Total Suggestions: {analysis_result.get('total_suggestions', 0)}", styles['Normal']))
    story.append(Spacer(1, 12))

    if analysis_result.get('issues'):
        story.append(Paragraph("Security Issues & Warnings:", styles['Heading3']))
        for issue in analysis_result['issues']:
            story.append(Paragraph(f"{issue['type'].upper()} - {issue.get('risk', 'Unknown')} RISK: {issue['message']}", styles['Normal']))
            if issue.get('command_part'):
                story.append(Paragraph(f"Problematic part: {issue['command_part']}", styles['Italic']))
        story.append(Spacer(1, 12))

    if analysis_result.get('suggestions'):
        story.append(Paragraph("Suggestions & Best Practices:", styles['Heading3']))
        for suggestion in analysis_result['suggestions']:
            story.append(Paragraph(suggestion, styles['Normal']))
        story.append(Spacer(1, 12))

    if analysis_result.get('is_code') and analysis_result.get('corrected_code'):
        story.append(Paragraph("Code Corrections:", styles['Heading3']))
        story.append(Paragraph("Original Code:", styles['Heading4']))
        story.append(Paragraph(analysis_result['command'], styles['Code']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Corrected Code:", styles['Heading4']))
        story.append(Paragraph(analysis_result['corrected_code'], styles['Code']))
        story.append(Spacer(1, 12))

    story.append(Paragraph("Conclusion:", styles['Heading3']))
    if analysis_result.get('risk_level') in ['CRITICAL', 'HIGH']:
        story.append(Paragraph("⚠️ HIGH RISK: This command contains serious security issues that should be addressed immediately.", styles['Normal']))
    elif analysis_result.get('risk_level') == 'MEDIUM':
        story.append(Paragraph("⚡ MEDIUM RISK: This command has some issues that should be reviewed and potentially corrected.", styles['Normal']))
    elif analysis_result.get('risk_level') == 'LOW':
        story.append(Paragraph("✅ LOW RISK: This command appears relatively safe but always double-check before execution.", styles['Normal']))
    else:
        story.append(Paragraph("✅ ANALYSIS COMPLETE: No significant issues found.", styles['Normal']))

    doc.build(story)
    return temp_file.name
