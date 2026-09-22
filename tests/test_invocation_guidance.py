"""Package checks; model behavior is evaluated with realistic requests separately."""
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("projectos_validator", ROOT / "scripts/validate_skill.py")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


class InvocationGuidanceTest(unittest.TestCase):
    def package(self, temp):
        target = Path(temp) / "project-os"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return target

    def errors(self, root):
        return [f.message for f in validator.validate(root) if f.severity == "ERROR"]

    def test_package_and_explicit_invocation_are_valid(self):
        self.assertEqual(self.errors(ROOT), [])

    def test_missing_resource_is_a_finding_not_a_crash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.package(temp)
            (root / "scripts/audit_project_docs.py").unlink()
            self.assertTrue(any("audit_project_docs.py" in e for e in self.errors(root)))

    def test_broken_markdown_reference_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.package(temp)
            source = root / "references/onboarding-and-invocation.md"
            source.write_text(source.read_text(encoding="utf-8") +
                              "\nSee [resource](references/missing.md).\n", encoding="utf-8")
            self.assertTrue(any("missing.md" in e for e in self.errors(root)))

    def test_external_reference_cannot_escape_package(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.package(temp)
            source = root / "SKILL.md"
            source.write_text(source.read_text(encoding="utf-8") +
                              "\n`references/../../outside.md`\n", encoding="utf-8")
            self.assertTrue(any("escapes skill" in e for e in self.errors(root)))

    def test_prose_paraphrase_and_concise_description_are_not_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.package(temp)
            (root / "SKILL.md").write_text(
                "---\nname: project-os\ndescription: Plan projects and reconcile state.\n---\n"
                "# ProjectOS\nUse the relevant project lifecycle guidance.\n", encoding="utf-8")
            self.assertEqual(validator.validate(root), [])


if __name__ == "__main__":
    unittest.main()
