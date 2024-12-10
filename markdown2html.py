#!/usr/bin/env python3
import sys
import os
import re
import hashlib

# Check if the number of arguments is exactly 3 (script name + 2 arguments)
if len(sys.argv) != 3:
    print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
    sys.exit(1)

# Get the input and output filenames from command-line arguments
markdown_file = sys.argv[1]
html_file = sys.argv[2]

# Check if the input Markdown file exists
if not os.path.isfile(markdown_file):
    print(f"Missing {markdown_file}", file=sys.stderr)
    sys.exit(1)

try:
    # Read all lines from the Markdown file
    with open(markdown_file, 'r') as md:
        lines = md.readlines()
except Exception as e:
    print(f"Error reading {markdown_file}: {e}", file=sys.stderr)
    sys.exit(1)

# Initialize variables to keep track of the current state
html_output = []
in_ul = False      # Flag to indicate if we're inside an unordered list
in_ol = False      # Flag to indicate if we're inside an ordered list
in_p = False       # Flag to indicate if we're inside a paragraph
paragraph_lines = []  # To collect lines belonging to the current paragraph

# Iterate through each line in the Markdown file
for line in lines:
    stripped = line.rstrip()

    # Functionality: Replace **text** with <b>text</b> and __text__ with <em>text</em>
    # Replace **text**
    bold_matches = re.findall(r'\*\*(.+?)\*\*', stripped)
    for match in bold_matches:
        stripped = stripped.replace(f"**{match}**", f"<b>{match}</b>")

    # Replace __text__
    italic_matches = re.findall(r'__(.+?)__', stripped)
    for match in italic_matches:
        stripped = stripped.replace(f"__{match}__", f"<em>{match}</em>")

    # Functionality: Replace [[text]] with MD5 hash and ((text)) by removing 'c'/'C'
    # Replace [[text]] with MD5 hash
    hash_matches = re.findall(r'\[\[(.+?)\]\]', stripped)
    for match in hash_matches:
        md5_hash = hashlib.md5(match.encode()).hexdigest()
        stripped = stripped.replace(f"[[{match}]]", md5_hash)

    # Replace ((text)) by removing 'c' and 'C'
    remove_c_matches = re.findall(r'\(\((.+?)\)\)', stripped)
    for match in remove_c_matches:
        modified_text = re.sub(r'[cC]', '', match)
        stripped = stripped.replace(f"(({match}))", modified_text)

    # Handle empty lines (signify end of paragraph or list)
    if not stripped:
        if in_p:
            # Close paragraph
            html_output.append("<p>")
            for idx, pline in enumerate(paragraph_lines):
                if idx < len(paragraph_lines) - 1:
                    html_output.append(f"    {pline}<br/>")
                else:
                    html_output.append(f"    {pline}")
            html_output.append("</p>")
            paragraph_lines = []
            in_p = False
        if in_ul:
            # Close unordered list
            html_output.append("</ul>")
            in_ul = False
        if in_ol:
            # Close ordered list
            html_output.append("</ol>")
            in_ol = False
        continue

    # Check for headings
    heading_match = re.match(r'^(#{1,6})\s+(.*)', stripped)
    if heading_match:
        # Close any open paragraphs or lists
        if in_p:
            html_output.append("<p>")
            for idx, pline in enumerate(paragraph_lines):
                if idx < len(paragraph_lines) - 1:
                    html_output.append(f"    {pline}<br/>")
                else:
                    html_output.append(f"    {pline}")
            html_output.append("</p>")
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

    # Check for unordered list items starting with '- '
    ul_match = re.match(r'^-\s+(.*)', stripped)
    if ul_match:
        # Close any open paragraphs or ordered lists
        if in_p:
            html_output.append("<p>")
            for idx, pline in enumerate(paragraph_lines):
                if idx < len(paragraph_lines) - 1:
                    html_output.append(f"    {pline}<br/>")
                else:
                    html_output.append(f"    {pline}")
            html_output.append("</p>")
            paragraph_lines = []
            in_p = False
        if in_ol:
            html_output.append("</ol>")
            in_ol = False
        if not in_ul:
            # Open unordered list
            html_output.append("<ul>")
            in_ul = True
        # Add list item
        item = ul_match.group(1)
        html_output.append(f"    <li>{item}</li>")
        continue

    # Check for ordered list items starting with '* '
    ol_match = re.match(r'^\*\s+(.*)', stripped)
    if ol_match:
        # Close any open paragraphs or unordered lists
        if in_p:
            html_output.append("<p>")
            for idx, pline in enumerate(paragraph_lines):
                if idx < len(paragraph_lines) - 1:
                    html_output.append(f"    {pline}<br/>")
                else:
                    html_output.append(f"    {pline}")
            html_output.append("</p>")
            paragraph_lines = []
            in_p = False
        if in_ul:
            html_output.append("</ul>")
            in_ul = False
        if not in_ol:
            # Open ordered list
            html_output.append("<ol>")
            in_ol = True
        # Add list item
        item = ol_match.group(1)
        html_output.append(f"    <li>{item}</li>")
        continue

    # If none of the above, it's part of a paragraph
    if not in_p:
        # Close any open lists
        if in_ul:
            html_output.append("</ul>")
            in_ul = False
        if in_ol:
            html_output.append("</ol>")
            in_ol = False
        # Start a new paragraph
        in_p = True
        paragraph_lines = []
    # Add the line to the current paragraph
    paragraph_lines.append(stripped)

# After processing all lines, close any open tags
if in_p:
    html_output.append("<p>")
    for idx, pline in enumerate(paragraph_lines):
        if idx < len(paragraph_lines) - 1:
            html_output.append(f"    {pline}<br/>")
        else:
            html_output.append(f"    {pline}")
    html_output.append("</p>")
if in_ul:
    html_output.append("</ul>")
if in_ol:
    html_output.append("</ol>")

# Join all HTML lines with newline characters
final_html = '\n'.join(html_output) + '\n'

# Write the HTML content to the output file
try:
    with open(html_file, 'w') as html:
        html.write(final_html)
except Exception as e:
    print(f"Error writing to {html_file}: {e}", file=sys.stderr)
    sys.exit(1)

# Exit successfully
sys.exit(0)
