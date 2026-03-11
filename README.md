# jira-md-upload

A CLI tool to upload Markdown content to a Jira issue description.

Reads a Markdown file, optionally converts it to Jira wiki markup using `pandoc`, and updates the **description field** of a Jira issue via the Jira REST API.

## Demo

<table>
<tr>
<td align="center">

### markdown file
<img width="938" src="https://github.com/user-attachments/assets/bdb14aa5-b98e-4a2a-912d-bc85388fe774" />

</td>
<td align="center">

### auto-created jira issue
<img width="938" src="https://github.com/user-attachments/assets/6ace481a-5942-4e99-a1c6-67aa4145072a" />

</td>
</tr>
</table>

## Requirements

- [uv](https://docs.astral.sh/uv/)
- `pandoc` (optional, for Markdown → Jira markup conversion)

## Install

```sh
just install
```

This installs `jira-md-upload` globally via `uv tool install`.

## Environment Variables

```sh
export JIRA_URL="http://jira.cubrid.org"
export JIRA_USER="your_username"
export JIRA_PASSWORD="your_password"
```

Or use a `.envrc` with [direnv](https://direnv.net/).

## Usage

```sh
jira-md-upload ISSUE_KEY MARKDOWN_FILE [--plain]
```

- `--plain` — skip pandoc conversion and upload raw Markdown

Example:

```sh
jira-md-upload CBRD-26597 CBRD-26597.md
```

Or via justfile:

```sh
just upload-26597
```

## Notes

- Overwrites the current issue description.
- Requires edit permission on the Jira issue.
- Uses Jira Server/Data Center REST API v2: `/rest/api/2/issue/{issueKey}`
