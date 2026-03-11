# jira_md_upload

A simple CLI tool to upload Markdown content to a Jira issue description.

The script reads a Markdown file, optionally converts it to Jira wiki markup using `pandoc`, and updates the **description field** of a Jira issue via the Jira REST API.

---

## Requirements

* Python 3.7+
* Python package:

  * `requests`
* Optional (recommended for formatting):

  * `pandoc`

Install Python dependency:

```
pip install requests
```

Install pandoc (optional but recommended):

```
sudo apt install pandoc
```

---

## Environment Variables

Set the following environment variables before running the script:

```
export JIRA_URL="http://jira.cubrid.org"
export JIRA_USER="your_username"
export JIRA_PASSWORD="your_password"
```

---

## Usage

Basic usage:

```
python jira_md_upload.py ISSUE_KEY MARKDOWN_FILE
```

Example:

```
python jira_md_upload.py CBRD-26597 CBRD-26597.md
```

This will:

1. Read the Markdown file
2. Convert it to Jira markup using `pandoc`
3. Upload the result to the **description** field of the issue

---

## Upload Raw Markdown

If your Jira instance supports Markdown directly, skip conversion:

```
python jira_md_upload.py CBRD-26597 CBRD-26597.md --plain
```

---

## Example Workflow

Write your issue description in Markdown:

```
# Bug description

Steps to reproduce:

1. Start server
2. Run query
3. Crash occurs

Expected behavior:
- Server should not crash
```

Upload it:

```
python jira_md_upload.py CBRD-26597 CBRD-26597.md
```

The script will update the Jira issue description automatically.

---

## Notes

* The script **overwrites the current issue description**.
* You must have permission to edit the Jira issue.
* If formatting looks incorrect, ensure `pandoc` is installed so Markdown can be converted to Jira markup.
* Jira Server/Data Center typically uses the REST endpoint:

```
/rest/api/2/issue/{issueKey}
```

---

## License

Internal tool for convenience. Modify as needed.

