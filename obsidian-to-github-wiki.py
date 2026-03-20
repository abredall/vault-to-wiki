#!/usr/bin/env python3
import argparse
import sys
import re
import subprocess
from pathlib import Path
from transformations import run_all_transformations

# Argument parsing
parser = argparse.ArgumentParser(
    prog='Obsidian to Github Wiki',
    description='Converts Obsidian markdown files to be compatible with Github Wiki formatting.'
)

parser.add_argument(
    '--input',
    help='The input Obsidian vault to convert.',
    required=True
)

parser.add_argument(
    '--output',
    help='The output directory for the converted Github Wiki files.',
    required=True
)

parser.add_argument(
    '--convert-full-vault',
    help='Whether to convert the entire vault or only the files changed in the last commit. (true/false)',
    required=False,
    default='false'
)

args = parser.parse_args()

# Sanitize input for convert-full-vault
convert_full_vault = args.convert_full_vault.lower() in ['true', '1', 'yes', 'y', 't']

if convert_full_vault:
    try: 
        print("Converting entire vault...")
        filenames = [str(p) for p in Path(args.input).rglob('*') if p.is_file() and not p.name.startswith('.') and not str(p).startswith('.') and str(p.parents[-3]) != f'{args.input}/Templates']
        old_files = [Path(f) for f in filenames]
        old_md_files = [p for p in old_files if p.suffix == '.md']
    except Exception as e:
        print(f"Failed to get files from vault: {e}", level="ERROR")
        sys.exit(1)
else:
    # Retrieve list of files changed in last commit
    try:
        header, *filenames = subprocess.check_output("git log -1 --stat --oneline --name-only | grep -v '.*' | grep -v 'Templates/'", shell=True, cwd=args.input).splitlines()
        filenames = [f.decode() for f in filenames]
        old_files = [Path(f"{args.input}/{f}") for f in filenames]
        old_md_files = [p for p in old_files if p.suffix == ".md" and p.is_file()]
        print(f"Files in last commit: {[str(f) for f in old_files]}")
    except Exception as e:
        print(f"Failed to get files from last commit: {e}", level="ERROR")
        sys.exit(1)

# Assign file names from old_files WITHOUT .md extension, to otherfiles
old_other_files = [p for p in old_files if p.suffix != ".md" and p.is_file()]

# Create corresponding output file paths
new_files = [Path(re.sub(f'^{args.input}', args.output, f)) for f in filenames]
new_md_files = [p for p in new_files if p.suffix == ".md"]
new_other_files = [p for p in new_files if p.suffix != ".md" and p.is_file()]

# Run all transformations
print("Starting content transformations...")
for old_file, new_file in zip(old_md_files, new_md_files):
    original_text = old_file.read_text(encoding='utf-8')
    new_text = run_all_transformations(original_text)
    if new_text != original_text:
        print(f"Transformed {old_file.name}")
    new_file.parent.mkdir(parents=True, exist_ok=True)
    new_file.write_text(new_text, encoding='utf-8')

# Copy non-markdown files
for old_file, new_file in zip(old_other_files, new_other_files):
    new_file.parent.mkdir(parents=True, exist_ok=True)
    old_file.copy(new_file)
