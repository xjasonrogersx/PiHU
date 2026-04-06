#!/usr/bin/env python3
"""
updatemd.py - Process ```uml code blocks in markdown files using PlantUML.

For each ```uml block found in the markdown file:
  - Computes an MD5 hash of the block content
  - Generates a PNG image via plantuml, saved to .img/<hash>.png
  - Wraps the block in a <details> element with the image linked above it

Already-processed blocks are checked: if the content hash has changed the old
image is removed and a new one is generated; if unchanged the block is left as-is.

A .umltheme file (if present in the same directory as the markdown file or in
the nearest repo root) is prepended inside @startuml / @enduml.

Usage:
    updatemd.py <markdown_file>
"""

import sys
import os
import re
import hashlib
import subprocess


def find_theme_content(md_file_path):
    """Return content of .umltheme if found alongside the md file or at repo root."""
    md_dir = os.path.dirname(os.path.abspath(md_file_path))

    theme_path = os.path.join(md_dir, '.umltheme')
    if os.path.exists(theme_path):
        with open(theme_path, 'r') as f:
            return f.read().strip()

    # Walk up the directory tree looking for a .git marker (repo root)
    current = md_dir
    while True:
        parent = os.path.dirname(current)
        if parent == current:
            break
        if os.path.exists(os.path.join(current, '.git')):
            theme_path = os.path.join(current, '.umltheme')
            if os.path.exists(theme_path):
                with open(theme_path, 'r') as f:
                    return f.read().strip()
            break
        current = parent

    return None


def md5(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def find_plantuml_cmd():
    """Return the command list to invoke plantuml.

    Prefers a .jar file in the same directory as this script; falls back to
    the 'plantuml' executable on PATH.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    jars = sorted(f for f in os.listdir(script_dir) if re.match(r'plantuml.*\.jar$', f, re.IGNORECASE))
    if jars:
        return ['java', '-jar', os.path.join(script_dir, jars[-1])]
    return ['plantuml']


def generate_image(uml_content, hash_val, img_dir, theme_content):
    """Write plantuml source to /tmp/<hash> and invoke plantuml to produce a PNG."""
    lines = ['@startuml']
    if theme_content:
        lines.append(theme_content)
    lines.append(uml_content.strip())
    lines.append('@enduml')

    tmp_file = os.path.join('/tmp', hash_val)
    with open(tmp_file, 'w') as f:
        f.write('\n'.join(lines) + '\n')

    os.makedirs(img_dir, exist_ok=True)

    result = subprocess.run(
        find_plantuml_cmd() + ['-tpng', '-o', img_dir, tmp_file],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"Warning: plantuml failed for {hash_val}:\n{result.stderr}", file=sys.stderr)
        return False

    return True


def make_block(hash_val, uml_content):
    return (
        f'![](.img/{hash_val}.png)\n'
        f'<details>\n'
        f'<summary>View UML</summary>\n'
        f'\n'
        f'```uml\n'
        f'{uml_content}'
        f'```\n'
        f'</details>'
    )


# Matches both already-processed blocks (group 1 = old hash, group 2 = content)
# and raw ```uml blocks (group 3 = content).  The more specific processed form
# is listed first in the alternation so it takes priority.
_PATTERN = re.compile(
    r'!\[\]\(\.img/([a-f0-9]{32})\.png\)\n'
    r'<details>\n<summary>View UML</summary>\n'
    r'```uml\n(.*?)```\n'
    r'</details>'
    r'|'
    r'```uml\n(.*?)```',
    re.DOTALL
)


def process_markdown(md_file_path):
    with open(md_file_path, 'r') as f:
        original = f.read()

    md_dir = os.path.dirname(os.path.abspath(md_file_path))
    img_dir = os.path.join(md_dir, '.img')
    theme_content = find_theme_content(md_file_path)

    def replace(m):
        if m.group(1) is not None:
            # Already-processed block — check whether content has changed
            old_hash = m.group(1)
            uml_content = m.group(2)
            new_hash = md5(uml_content)
            if new_hash == old_hash:
                return m.group(0)
            old_img = os.path.join(img_dir, old_hash + '.png')
            if os.path.exists(old_img):
                os.remove(old_img)
            generate_image(uml_content, new_hash, img_dir, theme_content)
            return make_block(new_hash, uml_content)
        else:
            # Raw ```uml block — wrap it
            uml_content = m.group(3)
            hash_val = md5(uml_content)
            generate_image(uml_content, hash_val, img_dir, theme_content)
            return make_block(hash_val, uml_content)

    updated = _PATTERN.sub(replace, original)

    if updated != original:
        with open(md_file_path, 'w') as f:
            f.write(updated)
        print(f"Updated: {md_file_path}")
    else:
        print(f"No changes: {md_file_path}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <markdown_file>")
        sys.exit(1)

    md_file = sys.argv[1]
    if not os.path.exists(md_file):
        print(f"Error: file not found: {md_file}", file=sys.stderr)
        sys.exit(1)

    process_markdown(md_file)


if __name__ == '__main__':
    main()
