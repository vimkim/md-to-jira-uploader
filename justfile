install:
    uv tool install --editable .

uninstall:
    uv tool uninstall jira-md-upload

upload-26597:
    jira-md-upload CBRD-26597 CBRD-26597.md
