#!/usr/bin/env python3
import re

files = {
    'rb3': '/home/vscode/.local/share/opencode/tool-output/tool_da9056dc1001cM5MYr3DPu4UoX',
}

with open(files['rb3'], 'r') as f:
    lines = f.read().split('\n')

# Print lines around where we should start
for i, line in enumerate(lines[160:170]):
    print(f"{i+160}: {repr(line[:60])}")