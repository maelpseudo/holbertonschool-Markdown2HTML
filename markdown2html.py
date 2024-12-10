#!/usr/bin/env python3
import sys
import os
import re
import hashlib

def replace_bold_and_italic(text):
    """
    Replace Markdown bold and italic syntax with corresponding HTML tags.
    """
    # Replace **text** with <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Replace __text__ with <em>text</em>
    text = re.sub(r'__(.+?)__', r'<em>\1</em>', text)
    return text

def replace_custom_syntax(text):
    """
    Replace custom syntax:
    [[content]] -> MD5 hash of content
    ((content)) -> Remove all 'c' (case insensitive) from content
    """
    # Replace [[content]] with MD5 hash of content
    text = re.sub(r'\[\[(.+?)\]\]', lambda match: hashlib.md5(match.group(1).encode()).hexdigest(), text)
    # Replace ((content)) by removing all 'c' (case insensitive) from content
    text = re.sub(r'\(\((.+?)\)\)', lambda match: re.sub(r'[cC]', '', match.group(1)), text)
    return text

def parse_markdown(markdown_file, html_file):
    """
    Parse the Markdown file for headings, unordered lists, ordered lists,
    paragraphs, bold, italic, and custom syntax, then write to the HTML file.
    """
    try:
        with open(markdown_file, 'r') as md, open(html_file, 'w') as html:
            in_ul = False  # Flag for unordered list
            in_ol = False  # Flag for ordered list
            in_paragraph = False  # Flag for paragraphs
            
            for line in md:
                line = line.rstrip()
                # Process bold, italic, and custom syntax
                line = replace_bold_and_italic(line)
                line = replace_custom_syntax(line)
                
                # Check for headings
                if line.startswith('#'):
                    # Close any open lists or paragraphs
                    if in_ul:
                        html.write("</ul>\n")
                        in_ul = False
                    if in_ol:
                        html.write("</ol>\n")
                        in_ol = False
                    if in_paragraph:
                        html.write("</p>\n")
                        in_paragraph = False
                    
                    # Process heading
                    heading_level = len(line.split(' ')[0])
                    heading_text = line[heading_level:].strip()
                    html.write(f"<h{heading_level}>{heading_text}</h{heading_level}>\n")
                
                # Check for unordered list items
                elif line.startswith('- '):
                    if in_ol:
                        html.write("</ol>\n")
                        in_ol = False
                    if not in_ul:
                        html.write("<ul>\n")
                        in_ul = True
                    list_item = line[2:].strip()
                    html.write(f"    <li>{list_item}</li>\n")
                
                # Check for ordered list items
                elif line.startswith('* '):
                    if in_ul:
                        html.write("</ul>\n")
                        in_ul = False
                    if not in_ol:
                        html.write("<ol>\n")
                        in_ol = True
                    list_item = line[2:].strip()
                    html.write(f"    <li>{list_item}</li>\n")
                
                # Check for paragraph
                elif line:
                    if not in_paragraph:
                        if in_ul:
                            html.write("</ul>\n")
                            in_ul = False
                        if in_ol:
                            html.write("</ol>\n")
                            in_ol = False
                        html.write("<p>\n")
                        in_paragraph = True
                    else:
                        html.write("    <br/>\n")
                    html.write(f"    {line}\n")
                
                # If the line is empty, close any open paragraph
                else:
                    if in_paragraph:
                        html.write("</p>\n")
                        in_paragraph = False
            
            # Close any open lists or paragraphs at the end of the file
            if in_ul:
                html.write("</ul>\n")
            if in_ol:
                html.write("</ol>\n")
            if in_paragraph:
                html.write("</p>\n")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

# Main logic
if __name__ == "__main__":
    # Check if the number of arguments is correct
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)

    # Get the input and output filenames
    markdown_file = sys.argv[1]
    html_file = sys.argv[2]

    # Check if the input Markdown file exists
    if not os.path.exists(markdown_file):
        print(f"Missing {markdown_file}", file=sys.stderr)
        sys.exit(1)

    # Process the Markdown file and generate the HTML
    parse_markdown(markdown_file, html_file)

    # Exit successfully
    sys.exit(0)
