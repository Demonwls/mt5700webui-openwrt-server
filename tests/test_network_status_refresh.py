import re
import unittest
from pathlib import Path


NETWORK_STATUS_BUNDLE = (
    Path(__file__).resolve().parents[1]
    / "at-webserver"
    / "files"
    / "www"
    / "5700"
    / "p__CPE__Network__Info__index.69f202f9.async.js"
)

WEB_ROOT = NETWORK_STATUS_BUNDLE.parent
RUNTIME_BUNDLE = WEB_ROOT / "umi.03797ca7.js"
PRELOAD_HELPER = WEB_ROOT / "preload_helper.39ec1fb6.js"


class NetworkStatusRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = NETWORK_STATUS_BUNDLE.read_text(encoding="utf-8")
        cls.runtime = RUNTIME_BUNDLE.read_text(encoding="utf-8")
        cls.preload = PRELOAD_HELPER.read_text(encoding="utf-8")

    def test_global_refresh_is_enabled_at_two_seconds_by_default(self):
        self.assertRegex(
            self.bundle,
            r"networkInfo:\s*\{\s*enabled:\s*!0,\s*interval:\s*2",
        )
        self.assertRegex(
            self.bundle,
            r"setInterval\(\s*globalRefresh,\s*d\s*\*\s*1e3",
        )
        self.assertIn('Ce("networkInfo", !0, 2)', self.bundle)

    def test_only_one_refresh_control_is_rendered(self):
        self.assertEqual(
            1,
            len(
                re.findall(
                    r'children:\s*"\\u81EA\\u52A8\\u5237\\u65B0"',
                    self.bundle,
                )
            ),
        )
        self.assertNotIn("\\u603B\\u81EA\\u52A8\\u5237\\u65B0", self.bundle)

    def test_single_refresh_control_keeps_custom_interval_input(self):
        self.assertIn("value: B.networkInfo.interval", self.bundle)
        self.assertIn('return Ce("networkInfo", !0, n || 2)', self.bundle)
        self.assertRegex(self.bundle, r"min:\s*1,\s*max:\s*60")
        marker = 'children: "\\u81EA\\u52A8\\u5237\\u65B0"'
        position = self.bundle.index(marker)
        control = self.bundle[max(0, position - 1600) : position + 1000]
        self.assertIn('type: "link"', control)
        self.assertIn('? "#e6f7ff"', control)

    def test_refresh_pauses_off_page_and_cleans_up_on_unmount(self):
        self.assertIn('document.visibilityState !== "visible"', self.bundle)
        self.assertIn("clearInterval(autoRefreshTimer.current)", self.bundle)
        self.assertIn("autoRefreshTimer.current = null", self.bundle)

    def test_refresh_skips_when_at_queue_is_busy(self):
        self.assertRegex(
            self.bundle,
            r"nn\.current\s*\|\|\s*en\.current\.length\s*>\s*0",
        )

    def test_changed_bundle_has_a_new_cache_key_everywhere(self):
        self.assertIn('92:"69f202f9"', self.runtime)
        self.assertIn(NETWORK_STATUS_BUNDLE.name, self.preload)
        for index in WEB_ROOT.rglob("index.html"):
            html = index.read_text(encoding="utf-8")
            self.assertIn(RUNTIME_BUNDLE.name, html, str(index))
            self.assertIn(PRELOAD_HELPER.name, html, str(index))

        for asset in (self.runtime, self.preload):
            self.assertNotIn("bcf1fe35", asset)


if __name__ == "__main__":
    unittest.main()
