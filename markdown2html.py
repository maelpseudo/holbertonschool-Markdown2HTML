#!/usr/bin/env python3
import sys
import os
import re
import hashlib

def print_usage():
    print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)

def print_missing(filename):
    print(f"Missing {filename}", file=sys.stderr)

def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

def remove_c(text):
    return re.sub(r'[cC]', '', text)

def process_bold_emphasis(text):
    # Replace **text** with <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Replace __text__ with <em>text</em>
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)
    return text

def process_special_syntax(text):
    # Replace [[text]] with MD5 hash
    text = re.sub(r'\[\[(.*?)\]\]', lambda m: md5_hash(m.group(1)), text)
    # Replace ((text)) with text without 'c' or 'C'
    text = re.sub(r'\(\((.*?)\)\)', lambda m: remove_c(m.group(1)), text)
    return text

def convert_markdown_to_html(lines):
    html_output = []
    in_ul = False
    in_ol = False
    in_p = False

    paragraph_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            # Empty line signifies the end of a paragraph or list
            if in_p:
                if paragraph_lines:
                    paragraph_html = '<p>\n'
                    for idx, pline in enumerate(paragraph_lines):
                        pline = process_special_syntax(pline)
                        pline = process_bold_emphasis(pline)
                        if idx < len(paragraph_lines) - 1:
                            paragraph_html += f'    {pline}\n    <br/>\n'
                        else:
                            paragraph_html += f'    {pline}\n'
                    paragraph_html += '</p>'
                    html_output.append(paragraph_html)
                paragraph_lines = []
                in_p = False
            if in_ul:
                html_output.append('</ul>')
                in_ul = False
            if in_ol:
                html_output.append('</ol>')
                in_ol = False
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if heading_match:
            if in_p:
                if paragraph_lines:
                    paragraph_html = '<p>\n'
                    for idx, pline in enumerate(paragraph_lines):
                        pline = process_special_syntax(pline)
                        pline = process_bold_emphasis(pline)
                        if idx < len(paragraph_lines) - 1:
                            paragraph_html += f'    {pline}\n    <br/>\n'
                        else:
                            paragraph_html += f'    {pline}\n'
                    paragraph_html += '</p>'
                    html_output.append(paragraph_html)
                paragraph_lines = []
                in_p = False
            if in_ul:
                html_output.append('</ul>')
                in_ul = False
            if in_ol:
                html_output.append('</ol>')
                in_ol = False

            level = len(heading_match.group(1))
            content = heading_match.group(2)
            content = process_special_syntax(content)
            content = process_bold_emphasis(content)
            html_output.append(f'<h{level}>{content}</h{level}>')
            continue

        # Unordered List
        ul_match = re.match(r'^-\s+(.*)', stripped)
        if ul_match:
            if in_p:
                if paragraph_lines:
                    paragraph_html = '<p>\n'
                    for idx, pline in enumerate(paragraph_lines):
                        pline = process_special_syntax(pline)
                        pline = process_bold_emphasis(pline)
                        if idx < len(paragraph_lines) - 1:
                            paragraph_html += f'    {pline}\n    <br/>\n'
                        else:
                            paragraph_html += f'    {pline}\n'
                    paragraph_html += '</p>'
                    html_output.append(paragraph_html)
                paragraph_lines = []
                in_p = False
            if in_ol:
                html_output.append('</ol>')
                in_ol = False
            if not in_ul:
                html_output.append('<ul>')
                in_ul = True
            item = ul_match.group(1)
            item = process_special_syntax(item)
            item = process_bold_emphasis(item)
            html_output.append(f'    <li>{item}</li>')
            continue

        # Ordered List
        ol_match = re.match(r'^\*\s+(.*)', stripped)
        if ol_match:
            if in_p:
                if paragraph_lines:
                    paragraph_html = '<p>\n'
                    for idx, pline in enumerate(paragraph_lines):
                        pline = process_special_syntax(pline)
                        pline = process_bold_emphasis(pline)
                        if idx < len(paragraph_lines) - 1:
                            paragraph_html += f'    {pline}\n    <br/>\n'
                        else:
                            paragraph_html += f'    {pline}\n'
                    paragraph_html += '</p>'
                    html_output.append(paragraph_html)
                paragraph_lines = []
                in_p = False
            if in_ul:
                html_output.append('</ul>')
                in_ul = False
            if not in_ol:
                html_output.append('<ol>')
                in_ol = True
            item = ol_match.group(1)
            item = process_special_syntax(item)
            item = process_bold_emphasis(item)
            html_output.append(f'    <li>{item}</li>')
            continue

        # Paragraph
        if not in_p:
            in_p = True
            paragraph_lines = []
        line_content = process_special_syntax(stripped)
        line_content = process_bold_emphasis(line_content)
        paragraph_lines.append(line_content)

    # After processing all lines, close any open tags
    if in_p and paragraph_lines:
        paragraph_html = '<p>\n'
        for idx, pline in enumerate(paragraph_lines):
            pline = pline
            if idx < len(paragraph_lines) - 1:
                paragraph_html += f'    {pline}\n    <br/>\n'
            else:
                paragraph_html += f'    {pline}\n'
        paragraph_html += '</p>'
        html_output.append(paragraph_html)
    if in_ul:
        html_output.append('</ul>')
    if in_ol:
        html_output.append('</ol>')

    return '\n'.join(html_output) + '\n'

def main():
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):
        print_missing(input_file)
        sys.exit(1)

    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    html_content = convert_markdown_to_html(lines)

    try:
        with open(output_file, 'w') as f:
            f.write(html_content)
    except Exception as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
