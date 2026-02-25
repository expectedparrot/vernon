#!/usr/bin/env python3
"""Validate that writeup/ contains only allowed .md files.

The only permitted markdown files in writeup/ are:
  - report.md    (the single report)
  - survey.md    (auto-generated survey docs)
  - planning.md  (working notes)
  - appendix.md  (supplementary material)

Any other .md file is a violation — all report content belongs in report.md.

Usage:
    python check_writeup.py [study_dir]

Exit codes:
    0  — OK
    1  — violations found (extra .md files)
"""

import sys
from pathlib import Path

ALLOWED = {"report.md", "survey.md", "planning.md", "appendix.md"}


def check(study_dir: str = ".") -> list[str]:
    """Return list of disallowed .md files in writeup/."""
    writeup = Path(study_dir) / "writeup"
    if not writeup.is_dir():
        return []
    return [
        f.name for f in writeup.glob("*.md") if f.name not in ALLOWED
    ]


if __name__ == "__main__":
    study = sys.argv[1] if len(sys.argv) > 1 else "."
    violations = check(study)
    if violations:
        msg = (
            f"ERROR: writeup/ contains disallowed markdown files: {violations}\n"
            "All report content must go in report.md. "
            "Merge these files into report.md and delete them."
        )
        print(msg, file=sys.stderr)
        sys.exit(1)
    else:
        print("OK: writeup/ contains only allowed .md files.")
