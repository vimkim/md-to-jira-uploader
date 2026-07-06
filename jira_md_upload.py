#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from typing import Optional

import re

import requests

from korean_spacing import fix_spacing as fix_markdown_korean_inline_spacing


KOREAN = r"[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]"
JIRA_VERBATIM_RE = re.compile(r"^\s*\{(?:code|noformat)(?::[^}]*)?\}\s*$")


def is_korean_char(ch: str) -> bool:
    return re.match(KOREAN, ch) is not None


def fix_jira_lines_outside_code_blocks(text: str, fix_line) -> str:
    result = []
    in_code = False

    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        newline = line[len(content):]

        if JIRA_VERBATIM_RE.match(content):
            in_code = not in_code
            result.append(line)
            continue

        if in_code:
            result.append(line)
        else:
            result.append(fix_line(content) + newline)

    return "".join(result)


def fix_jira_bold_code_nesting(text: str) -> str:
    """Fix {{monospace}} inside *bold* in JIRA wiki markup.

    JIRA wiki cannot render {{monospace}} nested inside *bold*.
    Splits: *foo {{bar}} baz* → *foo* {{bar}} *baz*
    """

    def _fix_line(line: str) -> str:
        # Skip list items (lines starting with * or ** as bullets)
        if re.match(r"\s*\*+\s", line):
            return line

        def _split_bold(m):
            inner = m.group(1)
            if "{{" not in inner:
                return m.group(0)

            segments = re.split(r"(\{\{.*?\}\})", inner)
            parts = []
            for seg in segments:
                if seg.startswith("{{") and seg.endswith("}}"):
                    parts.append(seg)
                else:
                    stripped = seg.strip()
                    if stripped:
                        parts.append(f"*{stripped}*")
            return " ".join(parts)

        # Match JIRA bold *...* (non-space after opening, non-space before closing)
        return re.sub(r"\*(?!\s)([^*\n]+?)(?<!\s)\*", _split_bold, line)

    return fix_jira_lines_outside_code_blocks(text, _fix_line)


JIRA_INLINE_RE = re.compile(
    r"""
    \{\{[^\n{}]*?[^\s{}]\}\}      |   # {{monospace}}
    \*(?!\s)([^*\n]*?[^\s*])\*        # *bold*
    """,
    re.VERBOSE,
)

def fix_korean_jira_inline_spacing_line(text: str) -> str:
    result = []
    last = 0

    for m in JIRA_INLINE_RE.finditer(text):
        start, end = m.span()
        span = m.group(0)

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


def fix_korean_jira_inline_spacing(text: str) -> str:
    """Add spaces around Jira inline markup that touches Korean text.

    Jira Server can fail to parse inline wiki markup when the closing marker is
    immediately followed by Korean suffixes, for example {{code}}의. Jira
    code/noformat macro bodies must stay byte-for-byte unchanged.
    """
    return fix_jira_lines_outside_code_blocks(text, fix_korean_jira_inline_spacing_line)


def sanitize_markdown(text: str) -> str:
    """Ensure blank lines before headings, lists, and fenced code blocks.

    Without these blank lines, pandoc may collapse adjacent elements
    (e.g. heading + list) into a single paragraph, breaking JIRA rendering.
    """
    lines = text.split("\n")
    out = []
    for i, line in enumerate(lines):
        if i > 0 and out and out[-1].strip() != "":
            needs_blank = False
            if re.match(r"^#{1,6}\s", line):  # heading
                needs_blank = True
            elif re.match(r"^[-*+]\s", line):  # unordered list start
                needs_blank = not re.match(r"^[-*+]\s", out[-1])
            elif re.match(r"^\d+\.\s", line):  # ordered list start
                needs_blank = not re.match(r"^\d+\.\s", out[-1])
            elif re.match(r"^[~`]{3}", line):  # fenced code block
                needs_blank = True
            if needs_blank:
                out.append("")
        out.append(line)
    return "\n".join(out)


def md_to_jira(md_text: str) -> str:
    # Requires pandoc installed:
    #   pandoc --from markdown --to jira
    try:
        result = subprocess.run(
            ["pandoc", "--from", "markdown", "--to", "jira"],
            input=md_text,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout
    except FileNotFoundError:
        raise RuntimeError("pandoc is not installed")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pandoc failed: {e.stderr}") from e


def markdown_to_jira_body(md_text: str) -> str:
    spaced_markdown = fix_markdown_korean_inline_spacing(md_text)
    jira_text = md_to_jira(sanitize_markdown(spaced_markdown))
    jira_text = fix_jira_bold_code_nesting(jira_text)
    return fix_korean_jira_inline_spacing(jira_text)


def update_issue(base_url: str, issue_key: str, username: str, password: str, description: str, summary: Optional[str] = None):
    url = f"{base_url.rstrip('/')}/rest/api/2/issue/{issue_key}"

    fields = {
        "description": description
    }

    if summary is not None:
        fields["summary"] = summary

    payload = {
        "fields": fields
    }

    resp = requests.put(
        url,
        auth=(username, password),
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )

    if resp.status_code not in (200, 204):
        raise RuntimeError(f"Jira update failed: {resp.status_code} {resp.text}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("issue_key", help="e.g. CBRD-26565")
    parser.add_argument("markdown_file", help="path to .md file")
    parser.add_argument("--jira-url", default=os.environ.get("JIRA_URL"))
    parser.add_argument("--user", default=os.environ.get("JIRA_USER"))
    parser.add_argument("--password", default=os.environ.get("JIRA_PASSWORD"))
    parser.add_argument("--plain", action="store_true", help="upload raw markdown without conversion")
    parser.add_argument("--summary", help="also update Jira issue summary")
    args = parser.parse_args()

    if not args.jira_url or not args.user or not args.password:
        print("Set JIRA_URL, JIRA_USER, JIRA_PASSWORD", file=sys.stderr)
        sys.exit(1)

    if args.summary is not None and not args.summary.strip():
        print("--summary must not be empty", file=sys.stderr)
        sys.exit(1)

    with open(args.markdown_file, "r", encoding="utf-8") as f:
        md = f.read()

    body = md if args.plain else markdown_to_jira_body(md)

    update_issue(
        base_url=args.jira_url,
        issue_key=args.issue_key,
        username=args.user,
        password=args.password,
        description=body,
        summary=args.summary,
    )

    print(f"Updated {args.issue_key}")


if __name__ == "__main__":
    main()
