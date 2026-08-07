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
    def test_menu_is_available_under_services(self):
        menu = json.loads(MENU_FILE.read_text(encoding="utf-8"))
        entry = menu["admin/services/at-webserver"]
        self.assertEqual("AT WebServer", entry["title"])
        self.assertEqual(-10, entry["order"])
        self.assertEqual(
            "首页", menu["admin/services/at-webserver/home"]["title"]
        )
        self.assertEqual(
            "配置", menu["admin/services/at-webserver/config"]["title"]
        )
        self.assertEqual(
            "日志查看", menu["admin/services/at-webserver/logs"]["title"]
        )
        self.assertNotIn("admin/modem/tdtech", menu)


if __name__ == "__main__":
    unittest.main()
