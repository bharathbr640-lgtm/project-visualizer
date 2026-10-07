#!/usr/bin/env python3
"""check_page.py - quick automatic checks for a generated project-map.html

Usage:
    python3 check_page.py <path/to/project-map.html>

Catches the most common problems: JavaScript syntax errors (needs node), ids that the code looks
up but do not exist, resources that need the internet, and pages that are not interactive or
not animated. Exit code 1 means: fix the PROBLEM lines first.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1]).expanduser()
    if not path.is_file():
        sys.exit(f"ERROR: {path} not found")
    html = path.read_text(encoding="utf-8", errors="ignore")
    problems, notes = [], []

    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S | re.I)
    if not scripts:
        problems.append("No inline <script>. The page will not be interactive.")
    node = shutil.which("node")
    if scripts and not node:
        notes.append("node was not found, so JavaScript syntax was NOT checked. Re-read the script carefully.")
    for n, code in enumerate(scripts, 1):
        if not node:
            break
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp = f.name
        try:
            r = subprocess.run([node, "--check", tmp], capture_output=True, text=True, timeout=30)
            if r.returncode:
                msg = r.stderr.strip().replace("\n", "\n  ")[:700]
                problems.append(f"JavaScript syntax error in script {n}:\n  {msg}")
        finally:
            os.unlink(tmp)

    ids = set(re.findall(r"""\bid\s*=\s*["']([^"']+)["']""", html))
    for name in sorted(set(re.findall(r"""getElementById\(\s*["']([^"']+)["']\s*\)""", html))):
        if name not in ids:
            problems.append(f"The code looks up id '{name}' but no element has that id.")

    need = set(re.findall(r"""<(?:script|img|iframe|source)\b[^>]*\bsrc\s*=\s*["'](https?://[^"']+)""", html, re.I))
    need |= set(re.findall(r"""<link\b[^>]*\bhref\s*=\s*["'](https?://[^"']+)""", html, re.I))
    need |= set(re.findall(r"""(?:url\(\s*|@import\s+)["']?(https?://[^)"';\s]+)""", html))
    for u in sorted(need):
        problems.append(f"Needs the internet: {u[:100]} (the page must work offline; inline it or remove it)")

    if not re.search(r"addEventListener|onclick\s*=|onmouseover\s*=|onmouseenter\s*=|\.onclick|\.onmouseover", html):
        problems.append("No click or hover handlers found. The page must be interactive.")
    if not re.search(r"@keyframes|animateMotion|<animate\b|requestAnimationFrame|setInterval", html):
        problems.append("No animation found. Something should move to show order or direction.")

    if "viewport" not in html:
        notes.append("No viewport meta tag. The page may look small on phones.")
    if re.search(r"lorem ipsum|TODO|FIXME|placeholder text", html, re.I):
        notes.append("Found 'lorem ipsum', 'TODO', 'FIXME' or 'placeholder text'. Remove leftovers unless they are real project notes.")
    if len(html) > 2_000_000:
        notes.append("The file is bigger than 2 MB. Consider trimming data.")
    if len(html) < 8_000:
        notes.append("The page is very small. Does it really explain the whole project?")

    print(f"Checked {path} ({len(html) // 1024} KB)")
    for n in notes:
        print("NOTE:", n)
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        sys.exit(1)
    print("OK: no problems found. Now open the page and look at it.")


if __name__ == "__main__":
    main()
