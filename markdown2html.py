#!/usr/bin/python3
"""
markdown2html.py
================

A script to convert Markdown files to HTML.

Usage:
    ./markdown2html.py README.md README.html

Requirements:
    - Converts headings, unordered lists, ordered lists, paragraphs, bold, emphasis,
      and custom syntaxes to HTML.
    - Handles custom syntaxes:
        [[text]] -> MD5 hash of text
        ((text)) -> Remove all 'c' or 'C' from text
    - Validates command-line arguments and file existence.
    - Adheres to PEP 8 style guidelines.

Author:
    Your Name
"""

import sys
import os
import re
import hashlib


def print_usage():
    """Prints the usage message to STDERR."""
    print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)


def print_missing(filename):
    """Prints a missing file error message to STDERR."""
    print(f"Missing {filename}", file=sys.stderr)


def md5_hash(text):
    """
    Returns the MD5 hash of the given text in lowercase.

    Args:
        text (str): The text to hash.

    Returns:
        str: The MD5 hash of the text.
    """
    return hashlib.md5(text.encode()).hexdigest()


def remove_c(text):
    """
    Removes all occurrences of 'c' and 'C' from the text.

    Args:
        text (str): The text to process.

    Returns:
        str: The text without 'c' or 'C'.
    """
    return re.sub(r'[cC]', '', text)


def replace_bold_and_emphasis(text):
    """
    Replaces Markdown bold and emphasis syntax with HTML tags.

    Args:
        text (str): The text to process.

    Returns:
        str: The text with bold and emphasis converted to HTML.
    """
    # Replace **text** with <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Replace __text__ with <em>text</em>
    text = re.sub(r'__(.+?)__', r'<em>\1</em>', text)
    return text


def replace_custom_syntax(text):
    """
    Replaces custom Markdown syntaxes with corresponding HTML or processed text.

    Args:
        text (str): The text to process.

    Returns:
        str: The text with custom syntaxes processed.
    """
    # Replace [[text]] with MD5 hash
    text = re.sub(r'\[\[(.+?)\]\]', lambda m: md5_hash(m.group(1)), text)
    # Replace ((text)) with text without 'c' or 'C'
    text = re.sub(r'\(\((.+?)\)\)', lambda m: remove_c(m.group(1)), text)
    return text


def convert_markdown_to_html(lines):
    """
    Converts a list of Markdown lines to HTML.

    Args:
        lines (list): List of strings representing lines in a Markdown file.

    Returns:
        str: The converted HTML content.
    """
    html_output = []
    in_ul = False
    in_ol = False
    in_p = False
    paragraph_lines = []

    for line in lines:
        stripped = line.rstrip()

        # Replace bold, emphasis, and custom syntax
        stripped = replace_bold_and_emphasis(stripped)
        stripped = replace_custom_syntax(stripped)

        # Handle empty lines
        if not stripped:
            if in_p:
                paragraph_html = "<p>\n"
                for idx, pline in enumerate(paragraph_lines):
                    if idx < len(paragraph_lines) - 1:
                        paragraph_html += f"    {pline}<br/>\n"
                    else:
                        paragraph_html += f"    {pline}\n"
                paragraph_html += "</p>"
                html_output.append(paragraph_html)
                paragraph_lines = []
                in_p = False
            if in_ul:
                html_output.append("</ul>")
                in_ul = False
            if in_ol:
                html_output.append("</ol>")
                in_ol = False
            continue

        # Handle headings
        heading_match = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if heading_match:
            # Close paragraphs and lists
            if in_p:
                paragraph_html = "<p>\n"
                for idx, pline in enumerate(paragraph_lines):
                    if idx < len(paragraph_lines) - 1:
                        paragraph_html += f"    {pline}<br/>\n"
                    else:
                        paragraph_html += f"    {pline}\n"
                paragraph_html += "</p>"
                html_output.append(paragraph_html)
                paragraph_lines = []
                in_p = False
            if in_ul:
                html_output.append("</ul>")
                in_ul = False
            if in_ol:
                html_output.append("</ol>")
                in_ol = False

            # Determine heading level
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            html_output.append(f"<h{level}>{content}</h{level}>")
            continue

        # Handle unordered lists
        ul_match = re.match(r'^-\s+(.*)', stripped)
        if ul_match:
            # Close paragraphs and ordered lists
            if in_p:
                paragraph_html = "<p>\n"
                for idx, pline in enumerate(paragraph_lines):
                    if idx < len(paragraph_lines) - 1:
                        paragraph_html += f"    {pline}<br/>\n"
                    else:
                        paragraph_html += f"    {pline}\n"
                paragraph_html += "</p>"
                html_output.append(paragraph_html)
                paragraph_lines = []
                in_p = False
            if in_ol:
                html_output.append("</ol>")
                in_ol = False
            if not in_ul:
                html_output.append("<ul>")
                in_ul = True
            item = ul_match.group(1)
            html_output.append(f"    <li>{item}</li>")
            continue

        # Handle ordered lists
        ol_match = re.match(r'^\*\s+(.*)', stripped)
        if ol_match:
            # Close paragraphs and unordered lists
            if in_p:
                paragraph_html = "<p>\n"
                for idx, pline in enumerate(paragraph_lines):
                    if idx < len(paragraph_lines) - 1:
                        paragraph_html += f"    {pline}<br/>\n"
                    else:
                        paragraph_html += f"    {pline}\n"
                paragraph_html += "</p>"
                html_output.append(paragraph_html)
                paragraph_lines = []
                in_p = False
            if in_ul:
                html_output.append("</ul>")
                in_ul = False
            if not in_ol:
                html_output.append("<ol>")
                in_ol = True
            item = ol_match.group(1)
            html_output.append(f"    <li>{item}</li>")
            continue

        # Handle paragraphs
        if not in_p:
            if in_ul:
                html_output.append("</ul>")
                in_ul = False
            if in_ol:
                html_output.append("</ol>")
                in_ol = False
            in_p = True
            paragraph_lines = []
        paragraph_lines.append(stripped)

    # Close any remaining open tags after processing all lines
    if in_p:
        paragraph_html = "<p>\n"
        for idx, pline in enumerate(paragraph_lines):
            if idx < len(paragraph_lines) - 1:
                paragraph_html += f"    {pline}<br/>\n"
            else:
                paragraph_html += f"    {pline}\n"
        paragraph_html += "</p>"
        html_output.append(paragraph_html)
    if in_ul:
        html_output.append("</ul>")
    if in_ol:
        html_output.append("</ol>")

    return '\n'.join(html_output) + '\n'


def main():
    """
    The main function that orchestrates the Markdown to HTML conversion.
    """
    # Validate the number of command-line arguments
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)

    # Extract input and output file names
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check if the input Markdown file exists
    if not os.path.isfile(input_file):
        print_missing(input_file)
        sys.exit(1)

    try:
        # Read the Markdown file
        with open(input_file, 'r') as md_file:
            markdown_lines = md_file.readlines()
    except Exception as e:
        print(f"Error reading {input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert Markdown to HTML
    html_content = convert_markdown_to_html(markdown_lines)

    try:
        # Write the HTML content to the output file
        with open(output_file, 'w') as html_file:
            html_file.write(html_content)
    except Exception as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
