#!/usr/bin/env python3
import re

files = {
    'rb3': '/home/vscode/.local/share/opencode/tool-output/tool_da9056dc1001cM5MYr3DPu4UoX',
}

with open(files['rb3'], 'r') as f:
    lines = f.readlines()

# Find first song data around line 192
for i in range(190, 230):
    line = lines[i].rstrip()
    if line:
        print(f"{i}: {line[:70]}")