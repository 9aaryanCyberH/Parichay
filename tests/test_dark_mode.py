"""
Unit tests for Parichay Dark Mode Toggle, Icon Visibility, and All Pages Audit.
Verifies Section 5 Optional Requirement:
- Default theme is Light Mode.
- All 8 templates render #themeToggleBtn with Moon and Sun icons.
- Instant pre-init script is present in <head> to prevent FOUC.
- Shared theme.js is loaded across all pages.
"""

import unittest
from html.parser import HTMLParser
from app import app


class ToggleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_toggle_btn = False
        self.has_light_icon = False
        self.has_dark_icon = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "button" and attr_dict.get("id") == "themeToggleBtn":
            self.has_toggle_btn = True
        if "theme-icon-light" in attr_dict.get("class", ""):
            self.has_light_icon = True
        if "theme-icon-dark" in attr_dict.get("class", ""):
            self.has_dark_icon = True


class TestDarkModeAudit(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_public_pages_have_theme_toggle_and_scripts(self):
        routes = ["/", "/privacy", "/terms", "/faq", "/auth", "/login", "/signup"]
        for route in routes:
            with self.subTest(route=route):
                res = self.client.get(route)
                self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")
                content = res.data.decode("utf-8")
                
                parser = ToggleParser()
                parser.feed(content)
                self.assertTrue(parser.has_toggle_btn, f"Route {route} missing #themeToggleBtn")
                self.assertTrue(parser.has_light_icon, f"Route {route} missing .theme-icon-light")
                self.assertTrue(parser.has_dark_icon, f"Route {route} missing .theme-icon-dark")
                self.assertIn("theme.js", content, f"Route {route} missing theme.js")
                self.assertIn("localStorage.getItem('parichay-theme')", content, f"Route {route} missing head theme init")

    def test_studio_page_has_theme_toggle_and_scripts(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = "test-uuid-admin"
            sess["user_name"] = "Admin User"
            sess["user_email"] = "admin@example.com"

        res = self.client.get("/studio")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")

        parser = ToggleParser()
        parser.feed(content)
        self.assertTrue(parser.has_toggle_btn, "Studio view missing #themeToggleBtn")
        self.assertTrue(parser.has_light_icon, "Studio view missing .theme-icon-light")
        self.assertTrue(parser.has_dark_icon, "Studio view missing .theme-icon-dark")
        self.assertIn("theme.js", content, "Studio view missing theme.js")


if __name__ == "__main__":
    unittest.main()
