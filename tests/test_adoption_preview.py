import importlib.util
from pathlib import Path
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "scripts/check_projectos_adoption.py"
spec = importlib.util.spec_from_file_location("adoption", TOOL)
adoption = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adoption)


class AdoptionTest(unittest.TestCase):
    def test_nested_override_and_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            child = root / "child"
            child.mkdir()
            (root / "AGENTS.md").write_text("root")
            (child / "AGENTS.override.md").write_text("override")
            (child / "AGENTS.md").write_text("shadowed")
            report = adoption.inspect(root, child)
            self.assertEqual([Path(x["path"]).name for x in report["selected"]], ["AGENTS.md", "AGENTS.override.md"])
            self.assertEqual(report["shadowed"], [str(child / "AGENTS.md")])
            self.assertEqual(report["status"], "static_preview")

    def test_limit_reports_omitted_later_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            child = root / "child"
            child.mkdir()
            (root / "AGENTS.md").write_text("abcdef")
            (child / "AGENTS.md").write_text("child")
            report = adoption.inspect(root, child, limit=4)
            self.assertEqual([x["within_limit_bytes"] for x in report["selected"]], [4, 0])
            self.assertTrue(all(x["truncated_or_omitted"] for x in report["selected"]))

    def test_empty_override_and_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.override.md").write_text("\n")
            (root / "CUSTOM.md").write_text("instructions")
            self.assertEqual(Path(adoption.inspect(root, root, fallback=["CUSTOM.md"])["selected"][0]["path"]).name, "CUSTOM.md")

    def test_wrong_worktree_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            child = root / "child"
            child.mkdir()
            with self.assertRaises(ValueError):
                adoption.inspect(child, root)
