import json
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
