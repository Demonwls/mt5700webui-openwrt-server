import json
import unittest
from pathlib import Path


MENU_FILE = (
    Path(__file__).resolve().parents[1]
    / "luci-app-at-webserver"
    / "root"
    / "usr"
    / "share"
    / "luci"
    / "menu.d"
    / "luci-app-at-webserver.json"
)


class LuciMenuTests(unittest.TestCase):
    def test_service_menu_is_prioritized(self):
        menu = json.loads(MENU_FILE.read_text(encoding="utf-8"))
        entry = menu["admin/services/at-webserver"]
        self.assertEqual(5, entry["order"])


if __name__ == "__main__":
    unittest.main()
