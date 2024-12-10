#!/usr/bin/env python3

import sys
import os
import hashlib
import re

def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

def remove_c(text):
    return re.sub(r'c', '', text, flags=re.IGNORECASE)

def convert_markdown_to_html(content):
    lines = content.split('\n')
    html_lines = []
    in_unordered_list = False
    in_ordered_list = False
    in_paragraph = False

    def close_open_lists():
        nonlocal in_unordered_list, in_ordered_list
        if in_unordered_list:
            html_lines.append("</ul>")
            in_unordered_list = False
        if in_ordered_list:
            html_lines.append("</ol>")
            in_ordered_list = False

    for line in lines:
        stripped_line = line.strip()

        # Handle headings
        if stripped_line.startswith('#'):
            close_open_lists()
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            heading_level = len(stripped_line.split(' ')[0])
            if 1 <= heading_level <= 6:
                heading_text = stripped_line[heading_level:].strip()
                html_lines.append(f"<h{heading_level}>{heading_text}</h{heading_level}>")
            continue

        # Handle unordered list items
        if stripped_line.startswith('- '):
            if in_ordered_list:
                html_lines.append("</ol>")
                in_ordered_list = False
            if not in_unordered_list:
                if in_paragraph:
                    html_lines.append("</p>")
                    in_paragraph = False
                html_lines.append("<ul>")
                in_unordered_list = True
            list_item = stripped_line[2:].strip()
            html_lines.append(f"    <li>{list_item}</li>")
            continue

        # Handle ordered list items
        if stripped_line.startswith('* '):
            if in_unordered_list:
                html_lines.append("</ul>")
                in_unordered_list = False
            if not in_ordered_list:
                if in_paragraph:
                    html_lines.append("</p>")
                    in_paragraph = False
                html_lines.append("<ol>")
                in_ordered_list = True
            list_item = stripped_line[2:].strip()
            html_lines.append(f"    <li>{list_item}</li>")
            continue

        # Handle custom bold, MD5, and content modification syntax
        def custom_replacements(text):
            text = re.sub(r'\[\[(.*?)\]\]', lambda m: md5_hash(m.group(1)), text)
            text = re.sub(r'\(\((.*?)\)\)', lambda m: remove_c(m.group(1)), text)
            return text

        # Handle paragraphs
        if stripped_line:
            close_open_lists()
            if not in_paragraph:
                html_lines.append("<p>")
                in_paragraph = True
            elif in_paragraph:
                html_lines.append("        <br />")
            html_lines.append(f"    {custom_replacements(stripped_line)}")
        else:
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False

    # Close any open lists or paragraphs at the end of the document
    close_open_lists()
    if in_paragraph:
        html_lines.append("</p>")

    return '\n'.join(html_lines)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./markdown2html.py <input_markdown_file> <output_html_file>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        html_content = convert_markdown_to_html(markdown_content)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    except Exception as e:
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()