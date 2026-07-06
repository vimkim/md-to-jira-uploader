#!/usr/bin/env python3
"""Post a markdown file as a Jira comment (mirrors jira_md_upload.py).

Uses the same pandoc-based markdown -> Jira wiki conversion path and
the same JIRA_URL / JIRA_USER / JIRA_PASSWORD env vars.
"""
import argparse
import json
import os
import sys

import requests

from jira_md_upload import (
    markdown_to_jira_body,
)


def add_comment(base_url: str, issue_key: str, username: str, password: str, body: str):
    url = f"{base_url.rstrip('/')}/rest/api/2/issue/{issue_key}/comment"
    payload = {"body": body}
    resp = requests.post(
        url,
        auth=(username, password),
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Jira comment failed: {resp.status_code} {resp.text}")
    return resp.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("issue_key", help="e.g. CBRD-26756")
    parser.add_argument("markdown_file", help="path to .md file")
    parser.add_argument("--jira-url", default=os.environ.get("JIRA_URL"))
    parser.add_argument("--user", default=os.environ.get("JIRA_USER"))
    parser.add_argument("--password", default=os.environ.get("JIRA_PASSWORD"))
    parser.add_argument("--plain", action="store_true", help="upload raw markdown without conversion")
    args = parser.parse_args()

    if not args.jira_url or not args.user or not args.password:
        print("Set JIRA_URL, JIRA_USER, JIRA_PASSWORD", file=sys.stderr)
        sys.exit(1)

    with open(args.markdown_file, "r", encoding="utf-8") as f:
        md = f.read()

    body = md if args.plain else markdown_to_jira_body(md)

    result = add_comment(
        base_url=args.jira_url,
        issue_key=args.issue_key,
        username=args.user,
        password=args.password,
        body=body,
    )

    print(f"Added comment {result.get('id')} to {args.issue_key}")


if __name__ == "__main__":
    main()
