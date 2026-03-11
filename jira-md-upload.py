#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys

import requests


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


def update_description(base_url: str, issue_key: str, username: str, password: str, description: str):
    url = f"{base_url.rstrip('/')}/rest/api/2/issue/{issue_key}"
    payload = {
        "fields": {
            "description": description
        }
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
    args = parser.parse_args()

    if not args.jira_url or not args.user or not args.password:
        print("Set JIRA_URL, JIRA_USER, JIRA_PASSWORD", file=sys.stderr)
        sys.exit(1)

    with open(args.markdown_file, "r", encoding="utf-8") as f:
        md = f.read()

    body = md if args.plain else md_to_jira(md)

    update_description(
        base_url=args.jira_url,
        issue_key=args.issue_key,
        username=args.user,
        password=args.password,
        description=body,
    )

    print(f"Updated {args.issue_key}")


if __name__ == "__main__":
    main()
