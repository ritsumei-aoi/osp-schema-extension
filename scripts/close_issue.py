"""Mark an issue closed: tick criteria, set date/status, replace the Response placeholder.

usage: python scripts/close_issue.py docs/issues/I01.md response.md
"""
import sys

PLACEHOLDER = "*(AI Agent: Please append your proposals, analysis, and execution logs here.)*"

path, resp = sys.argv[1], sys.argv[2]
s = open(path).read()
s = s.replace("**Date**: \n**Status**: open", "**Date**: 2026-10-06\n**Status**: closed")
s = s.replace("- [ ]", "- [x]")
s = s.replace(PLACEHOLDER, open(resp).read().strip())
open(path, "w").write(s)
