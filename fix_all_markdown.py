#!/usr/bin/env python3
"""Fix all markdown linting errors automatically."""

import re
from pathlib import Path

def fix_markdown(content):
    """Fix markdown formatting issues."""
    lines = content.split('\n')
    fixed = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        prev = lines[i-1] if i > 0 else ''
        next_line = lines[i+1] if i < len(lines)-1 else ''
        
        # Fix headings - add blank lines before/after
        if line.startswith('#'):
            if prev and prev.strip() and not prev.startswith('#'):
                if fixed and fixed[-1].strip():
                    fixed.append('')
            fixed.append(line)
            if next_line and next_line.strip() and not next_line.startswith('#'):
                fixed.append('')
        # Fix lists
        elif line.strip().startswith(('-', '*', '1.')):
            if prev and prev.strip() and not prev.strip().startswith(('-', '*', '1.')) and not prev.startswith('#'):
                if fixed and fixed[-1].strip():
                    fixed.append('')
            fixed.append(line)
        # Fix code blocks
        elif line.strip() == '```':
            fixed.append('```bash')
        else:
            fixed.append(line.rstrip())
        i += 1
    
    return '\n'.join(fixed)

files = [
    'COMPLETE_CLEANUP_SUMMARY.md',
    'ABSOLUTE_FINAL_STATUS.md',
    'CLEANUP_REPORT.md'
]

for f in files:
    path = Path(f)
    if path.exists():
        print(f"Fixing {f}...")
        content = path.read_text()
        fixed = fix_markdown(content)
        path.write_text(fixed)
        print(f"✅ Fixed {f}")
