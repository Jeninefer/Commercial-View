#!/usr/bin/env python3
"""
Comprehensive Markdown Fixer for Commercial-View project
Fixes MD022, MD031, MD032, MD040, MD047 errors
"""
import os
import re
import glob

def fix_md022_heading_spacing(content):
    """Fix MD022: Headings should be surrounded by blank lines"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if this is a heading
        if line.strip().startswith('#'):
            # Check if previous line exists and is not empty
            if i > 0 and lines[i-1].strip() != '':
                fixed_lines.append('')
            
            fixed_lines.append(line)
            
            # Check if next line exists and is not empty
            if i < len(lines) - 1 and lines[i+1].strip() != '':
                fixed_lines.append('')
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_md031_fenced_code_blocks(content):
    """Fix MD031: Fenced code blocks should be surrounded by blank lines"""
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        # Check for code block markers
        if line.strip().startswith('```'):
            if not in_code_block:  # Starting code block
                # Add blank line before if previous line is not empty
                if i > 0 and lines[i-1].strip() != '':
                    fixed_lines.append('')
                in_code_block = True
            else:  # Ending code block
                in_code_block = False
                fixed_lines.append(line)
                # Add blank line after if next line is not empty
                if i < len(lines) - 1 and lines[i+1].strip() != '':
                    fixed_lines.append('')
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_md032_list_spacing(content):
    """Fix MD032: Lists should be surrounded by blank lines"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if this is a list item
        if re.match(r'^[\s]*[-*+]\s', line) or re.match(r'^[\s]*\d+\.\s', line):
            # Check if this is the first item in a list
            if i > 0 and not (re.match(r'^[\s]*[-*+]\s', lines[i-1]) or re.match(r'^[\s]*\d+\.\s', lines[i-1])) and lines[i-1].strip() != '':
                fixed_lines.append('')
            
            fixed_lines.append(line)
            
            # Check if this is the last item in a list
            if i < len(lines) - 1:
                next_line = lines[i+1]
                if not (re.match(r'^[\s]*[-*+]\s', next_line) or re.match(r'^[\s]*\d+\.\s', next_line)) and next_line.strip() != '':
                    fixed_lines.append('')
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_md040_code_language(content):
    """Fix MD040: Fenced code blocks should have a language specified"""
    # Replace ``` with ```bash, ```python, etc. based on context
    content = re.sub(r'^```\s*$', '```bash', content, flags=re.MULTILINE)
    return content

def fix_md047_trailing_newline(content):
    """Fix MD047: Files should end with a single newline character"""
    if not content.endswith('\n'):
        content += '\n'
    elif content.endswith('\n\n'):
        content = content.rstrip('\n') + '\n'
    return content

def process_markdown_file(filepath):
    """Process a single markdown file"""
    print(f"Processing {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Warning: Could not read {filepath} as UTF-8, skipping")
        return
    
    original_content = content
    
    # Apply fixes
    content = fix_md022_heading_spacing(content)
    content = fix_md031_fenced_code_blocks(content)
    content = fix_md032_list_spacing(content)
    content = fix_md040_code_language(content)
    content = fix_md047_trailing_newline(content)
    
    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"No changes needed for {filepath}")

def main():
    """Main function to process all markdown files"""
    # Find all markdown files in current directory and subdirectories
    md_files = glob.glob('*.md') + glob.glob('**/*.md', recursive=True)
    
    if not md_files:
        print("No markdown files found")
        return
    
    print(f"Found {len(md_files)} markdown files")
    
    for md_file in md_files:
        process_markdown_file(md_file)
    
    print("Markdown fixing completed!")

if __name__ == "__main__":
    main()