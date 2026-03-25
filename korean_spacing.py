#!/usr/bin/env python3
import re
import argparse
from pathlib import Path

KOREAN = r"[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]"


INLINE_RE = re.compile(
    r"""
    (?<!\*)\*\*([^\n]*?[^\s*])\*\*(?!\*)   |   # **bold**
    (?<!\*)\*([^\s*\n][^\n]*?[^\s*])\*(?!\*) | # *italic* (not list bullet)
    `([^\s`\n][^\n]*?[^\s`])`                  # `code`
    """,
    re.VERBOSE,
)


def is_korean_char(ch: str) -> bool:
    return re.match(KOREAN, ch) is not None


def normalize_span(span: str) -> str:
    if span.startswith("**") and span.endswith("**"):
        return f"**{span[2:-2].strip()}**"
    if span.startswith("*") and span.endswith("*"):
        return f"*{span[1:-1].strip()}*"
    if span.startswith("`") and span.endswith("`"):
        return f"`{span[1:-1].strip()}`"
    return span


def fix_spacing(text: str) -> str:
    result = []
    last = 0

    for m in INLINE_RE.finditer(text):
        start, end = m.span()
        span = normalize_span(m.group(0))

        result.append(text[last:start])

        prev_char = text[start - 1] if start > 0 else ""
        next_char = text[end] if end < len(text) else ""

        if prev_char and is_korean_char(prev_char):
            if not result[-1].endswith(" "):
                result.append(" ")

        result.append(span)

        if next_char and is_korean_char(next_char):
            result.append(" ")

        last = end

    result.append(text[last:])
    return "".join(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ensure spacing around inline markdown spans next to Korean text"
    )
    parser.add_argument("-i", "--input", required=True, help="Input markdown file")
    parser.add_argument("-o", "--output", required=True, help="Output markdown file")
    args = parser.parse_args()

    src = Path(args.input).read_text(encoding="utf-8")
    dst = fix_spacing(src)
    Path(args.output).write_text(dst, encoding="utf-8")


if __name__ == "__main__":
    main()
