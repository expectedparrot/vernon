#!/usr/bin/env python3
"""Write the Expected Parrot report stylesheet into a writeup directory."""

from pathlib import Path

_CSS_FILE = Path(__file__).resolve().parent / "report.css"


def create_css(writeup_dir: str = "writeup") -> Path:
    """Copy report.css into writeup_dir/report.css. Returns the output path."""
    dest = Path(writeup_dir) / "report.css"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_CSS_FILE.read_text())
    return dest


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "writeup"
    out = create_css(target)
    print(f"Wrote {out}")
