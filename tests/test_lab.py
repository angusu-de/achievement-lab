import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import achievement_lab


class ConfigTests(unittest.TestCase):
    def test_repository_boundary_accepts_lab_name(self):
        config = achievement_lab.Config("target", "helper")
        config.validate()

    def test_repository_boundary_rejects_arbitrary_repo(self):
        config = achievement_lab.Config("target", "helper", evidence_repo="production")
        with self.assertRaises(achievement_lab.LabError):
            config.validate()

    def test_load_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({"target_login": "target", "helper_login": "helper"}))
            self.assertEqual(achievement_lab.load_config(path).full_repo, "target/achievement-lab-private")


class CatalogTests(unittest.TestCase):
    def test_catalog_has_x4_ceiling_and_no_write_only_signal_automation(self):
        output = io.StringIO()
        with redirect_stdout(output):
            achievement_lab.catalog(as_json=True)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["visible_tier_max"], 4)
        starstruck = next(item for item in payload["achievements"] if item["name"] == "Starstruck")
        self.assertEqual(starstruck["automation"], "never")

    def test_catalog_cli_does_not_require_config(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = achievement_lab.main(["catalog"])
        self.assertEqual(result, 0)
        self.assertIn("no visible x8 tier", output.getvalue())


class GuidedSetupTests(unittest.TestCase):
    def test_no_command_prints_help_in_non_interactive_use(self):
        output = io.StringIO()
        with mock.patch.object(achievement_lab.sys.stdin, "isatty", return_value=False), redirect_stdout(output):
            result = achievement_lab.main([])
        self.assertEqual(result, 0)
        self.assertIn("wizard", output.getvalue())

    def test_ui_respects_no_color(self):
        with mock.patch.dict("os.environ", {"NO_COLOR": "1"}):
            ui = achievement_lab.Ui()
            self.assertEqual(ui.paint("1", "safe"), "safe")

    def test_connected_accounts_filters_failed_credentials(self):
        payload = json.dumps({"hosts": {"github.com": [
            {"login": "target", "state": "success"},
            {"login": "expired", "state": "failed"},
        ]}})
        completed = mock.Mock(returncode=0, stdout=payload)
        with mock.patch.object(achievement_lab.shutil, "which", return_value="/usr/bin/gh"), \
             mock.patch.object(achievement_lab.subprocess, "run", return_value=completed):
            self.assertEqual(achievement_lab.connected_accounts(), ["target"])


if __name__ == "__main__":
    unittest.main()
