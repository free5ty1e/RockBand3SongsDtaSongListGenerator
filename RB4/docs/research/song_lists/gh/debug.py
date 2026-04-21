#!/usr/bin/env python3
import re

# Debug - just show first data row
with open('/home/vscode/.local/share/opencode/tool-output/tool_dacc54ec6001Uvv0H826VF3CNW', 'r') as f:
    lines = f.readlines()

# Find where header row is
for i, line in enumerate(lines):
    if 'Song 1 title' in line and 'Artist 1' in line:
        print(f"Header at line {i}")
        # Print surrounding
        print("---")
        for j in range(i, min(i+15, len(lines))):
            print(f"{j}: {repr(lines[j])}")
        break