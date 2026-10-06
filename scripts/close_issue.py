"""Close an issue file: set date/status, tick all criteria, fill the Response section.

Usage: python scripts/close_issue.py N response.md   (N = 1..8)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = "*(AI Agent: Please append your proposals, analysis, and execution logs here.)*"


def main():
    n, resp_path = sys.argv[1], Path(sys.argv[2])
    p = ROOT / "docs" / "issues" / f"I0{n}.md"
    s = p.read_text()
    s = s.replace("**Date**: \n**Status**: open", "**Date**: 2026-10-06\n**Status**: closed")
    s = s.replace("- [ ]", "- [x]")
    s = s.replace(PLACEHOLDER, resp_path.read_text())
    p.write_text(s)


if __name__ == "__main__":
    main()
