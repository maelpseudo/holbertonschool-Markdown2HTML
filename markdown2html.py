#!/usr/bin/env python3
import sys
import os

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

# If everything is correct, exit with status 0
sys.exit(0)
