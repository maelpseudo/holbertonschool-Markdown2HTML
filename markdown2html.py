#!/usr/bin/python3
"""
A script that converts a Markdown file to HTML.
"""

import sys
import os

if __name__ == "__main__":
    # Check if the number of arguments is correct
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        exit(1)

    markdown_file = sys.argv[1]
    html_file = sys.argv[2]

    # Check if the Markdown file exists
    if not os.path.isfile(markdown_file):
        print(f"Missing {markdown_file}", file=sys.stderr)
        exit(1)

    try:
        # Read the Markdown file
        with open(markdown_file, "r", encoding="utf-8") as md_file:
            markdown_content = md_file.readlines()

        # Simple conversion (example: this only converts # headers to <h1>)
        html_content = ""
        for line in markdown_content:
            if line.startswith("# "):
                html_content += f"<h1>{line[2:].strip()}</h1>\n"
            elif line.startswith("## "):
                html_content += f"<h2>{line[3:].strip()}</h2>\n"
            elif line.startswith("### "):
                html_content += f"<h3>{line[4:].strip()}</h3>\n"
            else:
                html_content += f"<p>{line.strip()}</p>\n"

        # Write the HTML content to the output file
        with open(html_file, "w", encoding="utf-8") as html_out:
            html_out.write(html_content)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        exit(1)

    exit(0)
