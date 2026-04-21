#!/usr/bin/env python3
import re
import json

lines = open('/home/vscode/.local/share/opencode/tool-output/tool_dacc54ec6001Uvv0H826VF3CNW').readlines()

debug = []
in_table = False
field_idx = 0

for i, line in enumerate(lines):
    line_stripped = line.strip()
    
    if 'Song 1 title' in line_stripped and 'Artist 1' in line_stripped:
        in_table = True
        debug.append("TABLE START")
        continue
    
    if in_table and line_stripped.startswith('## '):
        debug.append("TABLE END")
        break
    
    if not in_table:
        continue
    
    if not line_stripped:
        continue
    
    if line_stripped.startswith('|') and '---' in line_stripped:
        continue
    
    debug.append(f"Field {field_idx}: {line_stripped[:50]}")
    field_idx += 1
    
    if len(debug) > 30:
        break

for d in debug:
    print(d)