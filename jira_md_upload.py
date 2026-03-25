#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from typing import Optional

import re

import requests


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

    return "\n".join(_fix_line(line) for line in text.split("\n"))


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

    body = md if args.plain else fix_jira_bold_code_nesting(md_to_jira(md))

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
