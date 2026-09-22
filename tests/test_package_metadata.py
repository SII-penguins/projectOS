"""Package validation must not accept ambiguous or unparseable discovery data."""

import tempfile
import unittest

import test_invocation_guidance as helpers


class PackageMetadataTest(unittest.TestCase):
    package = helpers.InvocationGuidanceTest.package
    errors = helpers.InvocationGuidanceTest.errors

    def replace_frontmatter(self, root, front):
        (root / "SKILL.md").write_text("---\n" + front + "\n---\n# ProjectOS\n", encoding="utf-8")

    def test_duplicate_discovery_fields_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.package(tmp)
            self.replace_frontmatter(
                root, "name: first\nname: project-os\ndescription: Plan projects."
            )
            self.assertTrue(self.errors(root))

    def test_invalid_required_scalars_are_rejected(self):
        for value in ("[]", "true", "null", '"unterminated', '"   "', "123"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                root = self.package(tmp)
                self.replace_frontmatter(root, "name: project-os\ndescription: " + value)
                self.assertTrue(self.errors(root))

    def test_folded_description_is_parsed_not_mistaken_for_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.package(tmp)
            self.replace_frontmatter(
                root, "name: project-os\ndescription: >-\n  Plan projects\n  and reconcile state."
            )
            metadata, _ = helpers.validator.parse_frontmatter(
                (root / "SKILL.md").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["description"], "Plan projects and reconcile state.")
            self.assertEqual(self.errors(root), [])

    def test_name_length_limit_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.package(tmp)
            self.replace_frontmatter(root, "name: " + "a" * 65 + "\ndescription: Plan projects.")
            self.assertTrue(any("64" in error for error in self.errors(root)))

    def test_corrupt_utf8_is_a_finding_not_a_traceback(self):
        for relative in (
            "SKILL.md",
            "references/lifecycle-protocol.md",
            "scripts/audit_project_docs.py",
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = self.package(tmp)
                (root / relative).write_bytes(b"\xff\xfeinvalid")
                self.assertTrue(self.errors(root))

    def test_default_prompt_must_name_the_exact_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.package(tmp)
            path = root / "agents/openai.yaml"
            path.write_text(
                path.read_text(encoding="utf-8").replace("$project-os", "$project-os-extra"),
                encoding="utf-8",
            )
            self.assertTrue(self.errors(root))

    def test_duplicate_invocation_policy_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.package(tmp)
            path = root / "agents/openai.yaml"
            path.write_text(
                path.read_text(encoding="utf-8") + "  allow_implicit_invocation: false\n",
                encoding="utf-8",
            )
            self.assertTrue(self.errors(root))


if __name__ == "__main__":
    unittest.main()
