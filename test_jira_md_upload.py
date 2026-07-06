import shutil
import unittest

from jira_md_upload import fix_korean_jira_inline_spacing, markdown_to_jira_body
from korean_spacing import fix_spacing


class KoreanJiraInlineSpacingTest(unittest.TestCase):
    def test_jira_code_span_gets_space_before_korean_suffix(self):
        text = "주 회귀: {{xlocator_fetch_all}}의 값"

        self.assertEqual(
            fix_korean_jira_inline_spacing(text),
            "주 회귀: {{xlocator_fetch_all}} 의 값",
        )

    def test_jira_inline_markup_gets_space_after_korean_prefix(self):
        text = "한국{{code}}값과 한국*강조*값"

        self.assertEqual(
            fix_korean_jira_inline_spacing(text),
            "한국 {{code}} 값과 한국 *강조* 값",
        )

    def test_jira_inline_spacing_skips_code_blocks(self):
        text = (
            "{code:sql}\n"
            "SELECT '{{xlocator_fetch_all}}의 값', '한국*강조*값';\n"
            "{code}\n"
            "본문{{xlocator_fetch_all}}의 값"
        )

        self.assertEqual(
            fix_korean_jira_inline_spacing(text),
            "{code:sql}\n"
            "SELECT '{{xlocator_fetch_all}}의 값', '한국*강조*값';\n"
            "{code}\n"
            "본문 {{xlocator_fetch_all}} 의 값",
        )

    def test_markdown_spacing_skips_fenced_code_blocks(self):
        text = "본문`코드`값\n```sql\nSELECT '본문`코드`값';\n```\n"

        self.assertEqual(
            fix_spacing(text),
            "본문 `코드` 값\n```sql\nSELECT '본문`코드`값';\n```\n",
        )

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_markdown_conversion_preserves_korean_adjacent_bold(self):
        body = markdown_to_jira_body("이것은**중요한**내용입니다.")

        self.assertIn("이것은 *중요한* 내용입니다.", body)
        self.assertNotIn("{*}중요한{*}", body)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_markdown_conversion_spaces_jira_code_before_korean_suffix(self):
        body = markdown_to_jira_body(
            "주 회귀: `xlocator_fetch_all`의 `heap_next` 경로"
        )

        self.assertIn("{{xlocator_fetch_all}} 의", body)
        self.assertIn("{{heap_next}} 경로", body)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_markdown_conversion_preserves_fenced_code_block_text(self):
        body = markdown_to_jira_body(
            "```sql\nSELECT '{{xlocator_fetch_all}}의 값', '한국*강조*값';\n```\n"
        )

        self.assertIn(
            "SELECT '{{xlocator_fetch_all}}의 값', '한국*강조*값';",
            body,
        )

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_markdown_conversion_preserves_bold_code_text_in_fenced_code_block(self):
        body = markdown_to_jira_body("```text\nSELECT '*foo {{bar}} baz*';\n```\n")

        self.assertIn("SELECT '*foo {{bar}} baz*';", body)


if __name__ == "__main__":
    unittest.main()
