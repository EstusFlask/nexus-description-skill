#!/usr/bin/env python3
"""Check common Nexus BBCode nesting; this is not a renderer or URL checker."""

import argparse
import json
from pathlib import Path
import re

PAIRED = {
    "b", "i", "u", "s", "url", "img", "quote", "code", "list", "color",
    "size", "font", "center", "left", "right", "spoiler", "youtube",
}
TOKEN = re.compile(r"\[(/?)([A-Za-z*]+)(?:=([^\]\r\n]*))?\]")


def check(text):
    """Return line-numbered errors for recognized tags; ignore unknown syntax."""
    stack = []
    errors = []
    tags = 0
    links = 0
    for token in TOKEN.finditer(text):
        closing, name, argument = token.groups()
        name = name.lower()
        if stack and stack[-1][0] == "code":
            if closing and name == "code":
                stack.pop()
                tags += 1
            continue
        if name not in PAIRED | {"*", "line"}:
            continue
        line = text.count("\n", 0, token.start()) + 1
        tags += 1
        if name == "*":
            if not any(tag == "list" for tag, _ in stack):
                errors.append({"line": line, "message": "List item outside [list]."})
            continue
        if name == "line":
            if closing:
                errors.append({"line": line, "message": "[line] has no closing tag."})
            continue
        if closing:
            if not stack:
                errors.append({"line": line, "message": f"Unexpected [/{name}]."})
            elif stack[-1][0] != name:
                errors.append({
                    "line": line,
                    "message": f"[/{name}] crosses unclosed [{stack[-1][0]}].",
                })
            else:
                stack.pop()
        else:
            stack.append((name, line))
            if name == "url":
                links += 1
                if argument is not None and not argument.strip():
                    errors.append({"line": line, "message": "Empty [url=] target."})
    for name, line in stack:
        errors.append({"line": line, "message": f"Unclosed [{name}]."})
    return {"tagsChecked": tags, "links": links, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="UTF-8 BBCode source file")
    parser.add_argument("--json", action="store_true", help="Print a JSON report")
    args = parser.parse_args()
    try:
        report = check(args.file.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError) as exc:
        parser.exit(2, f"Cannot read BBCode: {exc}\n")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["errors"]:
        for error in report["errors"]:
            print(f"{args.file}:{error['line']}: {error['message']}")
    else:
        print(f"PASS: {report['tagsChecked']} tags checked, {report['links']} links.")
    return int(bool(report["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
