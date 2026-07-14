import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.scripts = []
        self.styles = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"])
        if tag == "link" and values.get("rel") == "stylesheet":
            self.styles.append(values.get("href"))


class StaticWebAppTests(unittest.TestCase):
    def test_page_references_local_assets(self):
        parser = DocumentParser()
        parser.feed((ROOT / "web" / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(parser.scripts, ["app.js"])
        self.assertEqual(parser.styles, ["app.css"])
        for asset in parser.scripts + parser.styles:
            self.assertTrue((ROOT / "web" / asset).is_file())

    def test_web_app_has_no_login_or_token_storage(self):
        source = (ROOT / "web" / "app.js").read_text(encoding="utf-8").lower()
        for forbidden in ("client_secret", "authorization: bearer", "localstorage", "sessionstorage", "oauth"):
            self.assertNotIn(forbidden, source)

    def test_devcontainer_is_valid_json(self):
        config = json.loads((ROOT / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8"))
        self.assertIn("github-cli:1", next(iter(config["features"])))


if __name__ == "__main__":
    unittest.main()
