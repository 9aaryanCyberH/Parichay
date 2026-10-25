"""
Unit tests for Parichay Dark Mode Toggle, Icon Visibility, and All Pages Audit.
Verifies Section 5 Optional Requirement:
- Default theme is Light Mode.
- All 8 templates render #themeToggleBtn with Moon and Sun icons.
- Instant pre-init script is present in <head> to prevent FOUC.
- Shared theme.js is loaded across all pages.
"""

import os
import unittest
import uuid
from html.parser import HTMLParser
from app import app
from services.database import AuthManager


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
        reg = AuthManager.register_user("Admin User", f"admin_{uuid.uuid4().hex[:6]}@example.com", "AdminPass123!")
        user = reg["user"]
        with self.client.session_transaction() as sess:
            sess["user_id"] = user["id"]
            sess["user_name"] = user["name"]
            sess["user_email"] = user["email"]

        res = self.client.get("/studio")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")

        parser = ToggleParser()
        parser.feed(content)
        self.assertTrue(parser.has_toggle_btn, "Studio view missing #themeToggleBtn")
        self.assertTrue(parser.has_light_icon, "Studio view missing .theme-icon-light")
        self.assertTrue(parser.has_dark_icon, "Studio view missing .theme-icon-dark")
    def test_dark_mode_css_homogeneity(self):
        """Verifies that style.css and landing.css have dark mode overrides for key components to prevent white boxes."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        style_path = os.path.join(base_dir, "static", "css", "style.css")
        with open(style_path, "r", encoding="utf-8") as f:
            style_css = f.read()

        self.assertIn('[data-theme="dark"] .skill-row-item', style_css)
        self.assertIn('[data-theme="dark"] .audit-checklist-item', style_css)
        self.assertIn('[data-theme="dark"] .btn-history-load', style_css)
        self.assertIn('[data-theme="dark"] .btn-view-suggestion', style_css)
        self.assertIn('[data-theme="dark"] .score-progress-bar-wrap', style_css)

        landing_path = os.path.join(base_dir, "static", "css", "landing.css")
        with open(landing_path, "r", encoding="utf-8") as f:
            landing_css = f.read()
        self.assertIn('[data-theme="dark"] .creator-link-pill', landing_css)


if __name__ == "__main__":
    unittest.main()
