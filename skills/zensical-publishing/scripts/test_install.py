import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("install.py")


def run(repo, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), *args],
                          capture_output=True, text=True)


def table(repo, name="zensical.toml"):
    d = tomllib.loads((repo / name).read_text())
    return d.get("project", d)


class InstallTest(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.repo = Path(self._t.name)

    def tearDown(self):
        self._t.cleanup()

    def write(self, name, text):
        p = self.repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def test_no_lists(self):
        self.write("zensical.toml", '[project]\nsite_name = "x"\n\n[project.theme]\nvariant = "modern"\n')
        r = run(self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        p = table(self.repo)
        self.assertEqual(p["extra_css"], ["assets/reading-tools/reading-tools.css"])
        self.assertEqual(p["theme"]["variant"], "modern")
        self.assertTrue((self.repo / "docs/assets/reading-tools/reading-tools.js").is_file())

    def test_existing_lists_single_and_multi_line(self):
        self.write("zensical.toml",
                   '[project]\n# keep me\nextra_css = ["a.css"]\n'
                   'extra_javascript = [\n  "a.js",  # note\n  "b.js",\n]\n')
        self.assertEqual(run(self.repo).returncode, 0)
        p = table(self.repo)
        self.assertEqual(p["extra_css"], ["a.css", "assets/reading-tools/reading-tools.css"])
        self.assertEqual(p["extra_javascript"],
                         ["a.js", "b.js", "assets/reading-tools/reading-tools.js"])
        self.assertIn("# keep me", (self.repo / "zensical.toml").read_text())

    def test_top_level_config(self):
        self.write("zensical.toml", 'site_name = "x"\n\n[theme]\nfoo = 1\n')
        self.assertEqual(run(self.repo).returncode, 0)
        self.assertEqual(table(self.repo)["extra_css"], ["assets/reading-tools/reading-tools.css"])

    def test_idempotent_and_check(self):
        self.write("zensical.toml", '[project]\nsite_name = "x"\n')
        self.assertEqual(run(self.repo, "--check").returncode, 1)
        run(self.repo)
        before = (self.repo / "zensical.toml").read_text()
        self.assertEqual(run(self.repo).returncode, 0)
        self.assertEqual((self.repo / "zensical.toml").read_text(), before)
        self.assertEqual(run(self.repo, "--check").returncode, 0)
        (self.repo / "docs/assets/reading-tools/reading-tools.js").write_text("old")
        self.assertEqual(run(self.repo, "--check").returncode, 1)
        run(self.repo)
        self.assertEqual(run(self.repo, "--check").returncode, 0)

    def test_dry_run_changes_nothing(self):
        self.write("zensical.toml", '[project]\nsite_name = "x"\n')
        run(self.repo, "--dry-run")
        self.assertFalse((self.repo / "docs").exists())
        self.assertNotIn("extra_css", (self.repo / "zensical.toml").read_text())

    def test_multiple_books_shared_symlinks(self):
        self.write("zensical.a.toml", '[project]\ndocs_dir = "a"\n')
        self.write("zensical.b.toml", '[project]\ndocs_dir = "b"\n')
        r = run(self.repo, "--shared", "shared")
        self.assertEqual(r.returncode, 0, r.stderr)
        for book in "ab":
            link = self.repo / book / "assets/reading-tools/reading-tools.css"
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.read_text(), (self.repo / "shared/reading-tools.css").read_text())
        self.assertEqual(run(self.repo, "--shared", "shared", "--check").returncode, 0)

    def test_workflow_paths_warning(self):
        self.write("zensical.toml", '[project]\nsite_name = "x"\n')
        self.write(".github/workflows/docs.yml",
                   "on:\n  push:\n    paths:\n      - \"zensical.toml\"\n      - \"other/**\"\njobs: {}\n# zensical\n")
        r = run(self.repo)
        self.assertIn("WARN", r.stdout)
        self.write(".github/workflows/docs.yml",
                   "on:\n  push:\n    paths:\n      - \"docs/**\"\njobs: {}\n# zensical\n")
        self.assertNotIn("WARN", run(self.repo).stdout)


if __name__ == "__main__":
    unittest.main()
