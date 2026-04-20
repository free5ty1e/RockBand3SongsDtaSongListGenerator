#!/usr/bin/env python3
import re
from pathlib import Path

# Look at lines around the track listing
files = {
    'rb3': '/home/vscode/.local/share/opencode/tool-output/tool_da9056dc1001cM5MYr3DPu4UoX',
}

with open(files['rb3'], 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

for i, line in enumerate(lines[160:180]):
    # Show the actual characters
    print(f"{i+160}: [{line[:100]}]{repr(line[:5])}")