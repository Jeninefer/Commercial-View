#!/usr/bin/env python3
"""
Script to fix heading levels and remove emphasis in all Markdown files

This script:
1. Finds all .md files in the repository
2. Ensures only one H1 (# heading) at the top
3. Changes additional H1 headings to H2 (## heading)
4. Removes emphasis markers (**, _, __, *) from all headings
"""

import os
import re
import sys
from pathlib import Path


def fix_markdown_file(file_path):
    """Fix heading levels and emphasis in a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        found_first_h1 = False
        modified = False
        
        for i in range(len(lines)):
            # Check for H1 headings
            if re.match(r'^\s*# ', lines[i]):
                if found_first_h1:
                    # Convert additional H1 to H2
                    lines[i] = re.sub(r'^\s*# ', '## ', lines[i])
                    modified = True
                    print(f"  Fixed additional H1 heading on line {i+1} in {file_path}")
                else:
                    found_first_h1 = True
                    
            # Check for headings with emphasis
            if re.match(r'^\s*#{1,6} .*(\*\*|\*|__|_)', lines[i]):
                # Remove emphasis markers from headings
                original = lines[i]
                lines[i] = re.sub(r'(\*\*|\*|__|_)', '', lines[i])
                modified = True
                print(f"  Removed emphasis from heading on line {i+1} in {file_path}")
        
        if modified:
            # Write back the modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False


def main():
    """Find and fix markdown files in the repository."""
    # Get repository root (parent of the scripts directory)
    repo_root = Path(__file__).parent.parent
    
    # Find all markdown files
    md_files = []
    for root, _, files in os.walk(repo_root):
        path = Path(root)
        if any(part in str(path) for part in ['node_modules', '.venv', '.archive']):
            continue
            
        for file in files:
            if file.endswith('.md'):
                md_files.append(path / file)
    
    print(f"Found {len(md_files)} markdown files to process")
    
    fixed_files = 0
    unchanged_files = 0
    
    for file_path in md_files:
        print(f"Processing: {file_path}")
        if fix_markdown_file(file_path):
            fixed_files += 1
            print(f"  Fixed issues in file: {file_path.name}")
        else:
            unchanged_files += 1
            print(f"  No issues found in: {file_path.name}")
    
    print("\n✅ Process completed!")
    print(f"  Fixed files: {fixed_files}")
    print(f"  Files without issues: {unchanged_files}")
    print(f"  Total files processed: {len(md_files)}")


if __name__ == "__main__":
    main()
# Make the script executable
chmod +x scripts/fix_markdown_headings.py

# Run the script
python3 scripts/fix_markdown_headings.py
