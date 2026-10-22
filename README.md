# jira-md-upload (deprecated)

> **Deprecated:** This tool has been replaced by
> [cubrid-jira](https://github.com/vimkim/cubrid-jira).
> Use `cubrid-jira` for new work; this repository is retained for historical reference.

The ideas and functionality developed here have been integrated into the stabilized
`cubrid-jira` CLI and the
[my-cubrid-jira](https://github.com/vimkim/my-cubrid-jira) document base.
`cubrid-jira` handles Markdown description uploads, comment posting, Korean
spacing, and Jira formatting fixes. `my-cubrid-jira` maintains issue documents
and delegates publishing to `cubrid-jira`.

## Migrate to cubrid-jira

```sh
uv tool install git+https://github.com/vimkim/cubrid-jira.git
```

Use the replacement commands to preview description updates and comments:

```sh
# Replaces: jira-md-upload ISSUE_KEY ISSUE_KEY.md
cubrid-jira update ISSUE_KEY --description-file ISSUE_KEY.md --from markdown

# Replaces: jira-md-comment ISSUE_KEY comment.md
cubrid-jira comment ISSUE_KEY --body-file comment.md --from markdown
```

Writes are dry-run by default. Add `--yes` to send the reviewed request.
Configure credentials with `CUBRID_JIRA_USER` and `CUBRID_JIRA_PASSWORD`, or a
`jira.cubrid.org` entry in `~/.netrc`. See the
[cubrid-jira README](https://github.com/vimkim/cubrid-jira#readme) for current
requirements and usage.

<details>
<summary>Historical documentation for the deprecated tool</summary>

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

To post the converted Markdown as a comment instead:

```sh
jira-md-comment CBRD-26597 CBRD-26597.md
```

Or via justfile:

```sh
just upload-26597
```

## Notes

- Overwrites the current issue description.
- Requires edit permission on the Jira issue.
- Uses Jira Server/Data Center REST API v2: `/rest/api/2/issue/{issueKey}`

---

## Korean Spacing Fix (`korean-spacing.py`)

Jira cannot render `*italic*` or `**bold**` when the markers are directly adjacent to Korean characters. This script inserts a single space before an opening marker and after a closing marker when the neighboring character is Korean.

`jira-md-upload` and `jira-md-comment` apply this fix automatically before Markdown conversion. They also add spacing around generated Jira inline code spans such as `{{name}}` when those spans touch Korean text.

### Usage

```sh
python korean-spacing.py -i input.md -o output.md
```

| Flag | Description |
|------|-------------|
| `-i` / `--input` | Source Markdown file |
| `-o` / `--output` | Destination file (can be the same as input) |

### Example

Before:
```
이것은**중요한**내용입니다.
```

After:
```
이것은 **중요한** 내용입니다.
```

Handles `**bold**`, `*italic*`, and `` `code` `` spans.

</details>
