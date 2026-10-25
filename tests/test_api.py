"""
tests/test_api.py - Complete Integration tests for Parichay
Validates:
- Route protection and authentication gateway (/auth)
- Public landing page, copywriting, and creator footer
- Public legal and info pages (/privacy, /terms, /faq, /docs/...)
- Safe redirects (preventing open redirects)
- User registration, password matching, session persistence, and logout
- Full resume analysis pipeline (valid and scanned PDF error handling)
- Conversational Career AI Assistant
- User history persistence
"""
import io
import os
import uuid
import unittest
from unittest.mock import patch, MagicMock
from app import app
from services.database import AuthManager, HistoryManager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALID_PDF_PATH = os.path.join(BASE_DIR, "sample_data", "sample_resume_swe.pdf")
SCANNED_PDF_PATH = os.path.join(BASE_DIR, "sample_data", "scanned_resume.pdf")


class TestParichayAPI(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key"
        self.client = app.test_client()

        with open(VALID_PDF_PATH, "rb") as f:
            self.valid_pdf_bytes = f.read()

        with open(SCANNED_PDF_PATH, "rb") as f:
            self.scanned_pdf_bytes = f.read()

    def login_test_user(self):
        """Helper to create and authenticate a test user session."""
        test_email = f"auth_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "SecurePassword123!"
        AuthManager.register_user("Test User", test_email, test_password)
        auth_res = AuthManager.authenticate_user(test_email, test_password)
        user = auth_res["user"]

        with self.client.session_transaction() as sess:
            sess["user_id"] = user["id"]
            sess["user_name"] = user["name"]
            sess["user_email"] = user["email"]
        return user

    def test_health_endpoint(self):
        """Test GET /api/health returns 200 OK."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "Parichay Resume Intelligence")

    def test_sample_jds_endpoint(self):
        """Test GET /api/sample-jds returns curated list of JDs with 4 roles."""
        response = self.client.get("/api/sample-jds")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["sample_jds"]), 4)

    # =========================================================================
    # PROTECTED ROUTES & AUTHENTICATION GATEWAY TESTS
    # =========================================================================
    def test_studio_protection_unauthenticated(self):
        """Test GET /studio redirects unauthenticated visitor to /auth with next target."""
        response = self.client.get("/studio")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth", response.headers["Location"])
        self.assertIn("next", response.headers["Location"])

    def test_api_routes_protection_unauthenticated(self):
        """Test unauthenticated API requests receive 401 with redirect to /auth."""
        # /api/analyze
        resp_analyze = self.client.post("/api/analyze", data={})
        self.assertEqual(resp_analyze.status_code, 401)
        data = resp_analyze.get_json()
        self.assertFalse(data["authenticated"])
        self.assertEqual(data["error_type"], "AuthenticationRequired")

        # /api/chat
        resp_chat = self.client.post("/api/chat", json={"message": "Hello"})
        self.assertEqual(resp_chat.status_code, 401)

        # /api/history
        resp_hist = self.client.get("/api/history")
        self.assertEqual(resp_hist.status_code, 401)

    def test_auth_gateway_page(self):
        """Test GET /auth renders the split-screen gateway offering Sign In and Create Account."""
        response = self.client.get("/auth?next=/studio")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Your next step", html)
        self.assertIn("starts here.", html)
        self.assertIn("Sign in to your account", html)
        self.assertIn("Create an account", html)
        self.assertIn("Return to homepage", html)

    def test_open_redirect_prevention(self):
        """Test malicious external next parameter is blocked and defaulted to /studio."""
        # Direct attempt with external domain
        resp = self.client.get("/auth?next=https://malicious-external-phishing.com")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertNotIn("https://malicious-external-phishing.com", html)

    # =========================================================================
    # PUBLIC PAGES, CONTENT, COPYWRITING & CREATOR FOOTER TESTS
    # =========================================================================
    def test_landing_page_content_and_creator_footer(self):
        """Test public landing page has exact copywriting, 6 features, 4 steps, and creator profile."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        # Header & Hero
        self.assertIn("Parichay", html)
        self.assertIn("YOUR NEXT CAREER MOVE STARTS WITH CLARITY", html)
        self.assertIn("Where Your Potential Meets Opportunity.", html)
        self.assertIn("Analyze my resume", html)
        self.assertIn("Explore how it works", html)

        # 6 Features
        self.assertIn("Resume intelligence", html)
        self.assertIn("Explainable role alignment", html)
        self.assertIn("Skills gap analysis", html)
        self.assertIn("Actionable AI recommendations", html)
        self.assertIn("Document quality review", html)
        self.assertIn("Analysis history", html)

        # 4 Steps
        self.assertIn("Step 01 — Add your resume", html)
        self.assertIn("Step 02 — Define your target", html)
        self.assertIn("Step 03 — Understand your alignment", html)
        self.assertIn("Step 04 — Plan your next move", html)

        # Privacy Section
        self.assertIn("Your career information deserves care.", html)
        self.assertIn("Read our Privacy Policy", html)

        # Creator Footer Section
        self.assertIn("Designed & developed by", html)
        self.assertIn("Aaryan Kumar", html)
        self.assertIn("Building thoughtful technology at the intersection of AI and meaningful user experiences.", html)
        self.assertIn("https://www.linkedin.com/in/aaryan-k-ba3985246/", html)
        self.assertIn("https://github.com/9aaryanCyberH", html)
        self.assertIn("aaryan-kumar-resume.pdf", html)
        self.assertIn("&copy; 2026 Parichay. All rights reserved.", html)

    def test_public_informational_pages(self):
        """Test GET /privacy, /terms, /faq remain accessible without authentication."""
        for path, keyword in [
            ("/privacy", "Privacy Policy"),
            ("/terms", "Terms of Service"),
            ("/faq", "Frequently Asked Questions")
        ]:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, f"Failed accessing {path}")
            self.assertIn(keyword, resp.get_data(as_text=True))

    def test_creator_resume_served(self):
        """Test the real creator resume PDF is successfully served via /docs route."""
        resp = self.client.get("/docs/aaryan-kumar-resume.pdf")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/pdf", resp.headers.get("Content-Type", ""))
        self.assertGreater(len(resp.data), 100000)  # ~198 KB file
        resp.close()

    # =========================================================================
    # AUTHENTICATION WORKFLOW (LOGIN, REGISTRATION, SESSION, LOGOUT)
    # =========================================================================
    def test_registration_and_login_flow(self):
        """Test user signup, confirm password check, login, and safe redirection."""
        unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePassword123!"

        # 1. Signup with mismatched confirm password fails
        bad_signup = self.client.post("/signup", data={
            "name": "Candidate One",
            "email": unique_email,
            "password": password,
            "confirm_password": "MismatchedPassword!"
        })
        self.assertIn("Passwords do not match", bad_signup.get_data(as_text=True))

        # 2. Signup with matching passwords succeeds and redirects to /studio
        good_signup = self.client.post("/signup", data={
            "name": "Candidate One",
            "email": unique_email,
            "password": password,
            "confirm_password": password
        }, follow_redirects=False)
        self.assertEqual(good_signup.status_code, 302)
        self.assertIn("/studio", good_signup.headers["Location"])

        # 3. Logout invalidates session
        logout_resp = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(logout_resp.status_code, 302)
        self.assertEqual(logout_resp.headers["Location"], "/")

        # 4. Login with wrong password fails
        bad_login = self.client.post("/login", data={
            "email": unique_email,
            "password": "WrongPassword!"
        })
        self.assertIn("Incorrect password", bad_login.get_data(as_text=True))

        # 5. Login with correct password succeeds and redirects to destination
        good_login = self.client.post("/login?next=/studio", data={
            "email": unique_email,
            "password": password
        }, follow_redirects=False)
        self.assertEqual(good_login.status_code, 302)
        self.assertIn("/studio", good_login.headers["Location"])

    def test_ghost_session_handling_and_no_loop(self):
        """Test stale/nonexistent user_id session is cleared and does not trap user in redirect loops."""
        # 1. Simulate a ghost session cookie (user_id not in database)
        with self.client.session_transaction() as sess:
            sess["user_id"] = 99999999
            sess["user_name"] = "Ghost User"
            sess["user_email"] = "ghost@example.com"

        # 2. Visiting protected /studio clears ghost session and redirects to /auth
        resp_studio = self.client.get("/studio", follow_redirects=False)
        self.assertEqual(resp_studio.status_code, 302)
        self.assertIn("/auth", resp_studio.headers["Location"])

        # 3. Visiting /login directly does not bounce back to /studio; renders login form (200 OK)
        resp_login = self.client.get("/login")
        self.assertEqual(resp_login.status_code, 200)
        self.assertIn("Sign in to continue your resume journey", resp_login.get_data(as_text=True))

        # 4. Visiting /signup directly does not bounce back to /studio; renders signup form (200 OK)
        resp_signup = self.client.get("/signup")
        self.assertEqual(resp_signup.status_code, 200)
        self.assertIn("Create your Parichay account to access your workspace", resp_signup.get_data(as_text=True))

    def test_login_and_signup_pages_always_ask_credentials(self):
        """Verifies GET /login and GET /signup always render forms to prompt credentials rather than skipping directly to studio."""
        self.login_test_user()

        login_resp = self.client.get("/login")
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn("Sign in to continue your resume journey", login_resp.get_data(as_text=True))

        signup_resp = self.client.get("/signup")
        self.assertEqual(signup_resp.status_code, 200)
        self.assertIn("Create your Parichay account to access your workspace", signup_resp.get_data(as_text=True))

    def test_topbar_button_classes_harmonized(self):
        """Test topbar auth buttons in index.html use matching btn-topbar-pill without color clash."""
        user = self.login_test_user()
        resp = self.client.get("/studio")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Authenticated state shows current user name and signout pill
        self.assertIn(user["name"], html)
        self.assertIn("Sign out", html)
        self.assertIn("btn-topbar-signout", html)

        # Confirm unauthenticated fallback in template source uses matching btn-topbar-pill
        template_path = os.path.join(BASE_DIR, "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            tmpl_content = f.read()
        self.assertIn('class="btn-topbar-pill">Sign in</a>', tmpl_content)
        self.assertIn('class="btn-topbar-pill">Sign up</a>', tmpl_content)
        self.assertNotIn('class="btn-topbar-solid">Sign up</a>', tmpl_content)

    # =========================================================================
    # AUTHENTICATED WORKSPACE & ANALYSIS PIPELINE TESTS
    # =========================================================================
    def test_studio_page_authenticated(self):
        """Test GET /studio returns the full workspace application when authenticated."""
        self.login_test_user()
        response = self.client.get("/studio")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Resume Studio", html)
        self.assertIn("Let's understand your fit for the role.", html)
        self.assertIn("Target job description", html)
        self.assertIn("Your resume", html)

    def test_analyze_scanned_pdf_rejection(self):
        """Test POST /api/analyze with image-only/scanned PDF returns 400 with explanation."""
        self.login_test_user()
        data = {
            "resume": (io.BytesIO(self.scanned_pdf_bytes), "scanned_resume.pdf"),
            "job_description": "We are seeking a Python engineer with Docker, PyTorch, and SQL experience to build scalable backend microservices."
        }
        response = self.client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.get_json()
        self.assertFalse(res_data["success"])
        self.assertEqual(res_data["error_type"], "PDFParsingError")

    def test_analyze_valid_full_workflow(self):
        """Test POST /api/analyze with valid PDF and JD returns complete real analysis."""
        self.login_test_user()
        jd = """
        We are seeking a Machine Learning Engineer with 2+ years of experience.
        Must be proficient in Python, PyTorch, Docker, PostgreSQL, and Scikit-Learn.
        Nice to have: Kubernetes, AWS, and FastAPI.
        Strong problem solving, teamwork, and communication skills required.
        """
        data = {
            "resume": (io.BytesIO(self.valid_pdf_bytes), "sample_resume_swe.pdf"),
            "job_description": jd
        }
        response = self.client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.get_json()
        
        self.assertTrue(res_data["success"])
        self.assertEqual(res_data["candidate"]["name"], "Aarav Sharma")
        self.assertGreater(res_data["alignment"]["score"], 50)
        self.assertIn("score_breakdown", res_data["alignment"])
        self.assertIn("Python", res_data["skills"]["matched_technical"])
        self.assertIn("Kubernetes", res_data["skills"]["missing_technical"])
        self.assertIn("recommendations", res_data)

    def test_chatbot_endpoint_authenticated(self):
        """Test POST /api/chat handles career inquiries with grounded responses."""
        self.login_test_user()
        payload = {
            "message": "How do I rewrite my resume bullet points using Google's X-Y-Z formula?",
            "history": [],
            "candidate": {
                "name": "Aarav Sharma",
                "matched_skills": ["Python", "PyTorch"],
                "missing_skills": ["Kubernetes", "AWS"]
            },
            "alignment": {
                "score": 78,
                "fit_tier": "High Fit"
            }
        }
        response = self.client.post("/api/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("reply", data)
        self.assertGreater(len(data["reply"]), 20)

    def test_chatbot_multiturn_alternating_turns(self):
        """Test POST /api/chat with existing conversation history including consecutive user turns."""
        self.login_test_user()
        payload = {
            "message": "Can you give me a STAR format answer for that?",
            "history": [
                {"role": "user", "content": "What technical interview questions should I practice?"},
                {"role": "assistant", "content": "Interviewers will focus on Python memory management and Docker."},
                {"role": "user", "content": "Can you give me a STAR format answer for that?"}
            ],
            "candidate": {
                "name": "Priya Nair",
                "matched_skills": ["Java", "Spring Boot"],
                "missing_skills": ["Docker", "Kubernetes"]
            },
            "alignment": {
                "score": 65,
                "fit_tier": "Moderate Match"
            }
        }
        response = self.client.post("/api/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("reply", data)
        self.assertGreater(len(data["reply"]), 20)

    def test_chatbot_chip_prompts(self):
        """Test POST /api/chat handles default suggestion chip prompts gracefully."""
        self.login_test_user()
        for chip_prompt in [
            "What are the three most important gaps in my resume?",
            "Explain how my alignment score was calculated.",
            "Help me improve this project description."
        ]:
            response = self.client.post("/api/chat", json={
                "message": chip_prompt,
                "candidate": {"name": "Test User", "matched_skills": ["Python"], "missing_skills": ["AWS"]},
                "alignment": {"score": 70, "fit_tier": "High Fit"}
            })
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data["success"])
            self.assertIn("reply", data)

    @patch("services.ai_advisor.requests.post")
    def test_gemini_live_chat_integration_success(self, mock_post):
        """Test that /api/chat invokes Gemini with valid alternating roles and returns live AI response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Here is an advanced X-Y-Z bullet tailored to your distributed systems background."}
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        self.login_test_user()
        from config import Config
        with patch.object(Config, "GEMINI_API_KEY", "test-api-key"), \
             patch("services.ai_advisor.os.environ.get", return_value="test-api-key"):
            response = self.client.post("/api/chat", json={
                "message": "Give me an advanced bullet point.",
                "history": [
                    {"role": "user", "content": "Hello advisor"},
                    {"role": "assistant", "content": "Hello! How can I help?"}
                ],
                "candidate": {"name": "Aarav", "matched_skills": ["Python"]},
                "alignment": {"score": 85, "fit_tier": "Strong Match"}
            })
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data["success"])
            self.assertTrue(data["is_ai_live"])
            self.assertIn("Google Gemini", data["engine"])
            self.assertIn("advanced X-Y-Z", data["reply"])

            # Verify alternating turns in the outbound request payload
            call_kwargs = mock_post.call_args[1]
            contents = call_kwargs["json"]["contents"]
            for i in range(len(contents) - 1):
                self.assertNotEqual(contents[i]["role"], contents[i+1]["role"],
                                    "Adjacent turns in contents MUST NOT share the same role")

    def test_gemini_status_endpoint(self):
        """Test GET /api/config/gemini-status returns status object with model."""
        response = self.client.get("/api/config/gemini-status")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("is_live", data)
        self.assertIn("model", data)

    @patch("requests.post")
    def test_gemini_key_validation_endpoint(self, mock_post):
        """Test POST /api/config/gemini-key validates key and responds with success."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}
        mock_post.return_value = mock_resp

        response = self.client.post("/api/config/gemini-key", json={"api_key": "AIzaSyTestValidKey123456789"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["is_live"])

    def test_chatbot_prioritize_learning_grounded_response(self):
        """Test POST /api/chat handles 'Which skills should I prioritize learning?' with concrete plan."""
        self.login_test_user()
        response = self.client.post("/api/chat", json={
            "message": "Which skills should I prioritize learning?",
            "candidate": {"name": "Aarav Sharma", "matched_skills": ["Python", "Flask"], "missing_skills": ["Docker", "Kubernetes"]},
            "alignment": {"score": 66, "fit_tier": "Moderate Alignment"}
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("High-Priority Skills Roadmap", data["reply"])
        self.assertIn("Docker", data["reply"])

    def test_history_endpoint_authenticated(self):
        """Test GET /api/history endpoint returns valid response for authenticated user."""
        self.login_test_user()
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["analyses"], list)

    # =========================================================================
    # API VALIDATION & EDGE CASE TESTS
    # =========================================================================
    def test_analyze_empty_job_description(self):
        """Test POST /api/analyze with empty job description returns 400 ValidationError."""
        self.login_test_user()
        data = {
            "resume": (io.BytesIO(self.valid_pdf_bytes), "sample_resume_swe.pdf"),
            "job_description": "   "
        }
        response = self.client.post("/api/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res = response.get_json()
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "ValidationError")

    def test_analyze_short_job_description(self):
        """Test POST /api/analyze with job description < 10 words returns 400 ValidationError."""
        self.login_test_user()
        data = {
            "resume": (io.BytesIO(self.valid_pdf_bytes), "sample_resume_swe.pdf"),
            "job_description": "Hiring a senior developer."
        }
        response = self.client.post("/api/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res = response.get_json()
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "ValidationError")
        self.assertIn("too brief", res["message"].lower())

    def test_analyze_missing_resume_file(self):
        """Test POST /api/analyze with no resume file attached returns 400 ValidationError."""
        self.login_test_user()
        data = {
            "job_description": "We are seeking a senior full stack Python and React engineer with 5 years experience."
        }
        response = self.client.post("/api/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res = response.get_json()
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "ValidationError")

    def test_analyze_invalid_file_extension(self):
        """Test POST /api/analyze with non-PDF extension (.txt) returns 400 InvalidFileType."""
        self.login_test_user()
        data = {
            "resume": (io.BytesIO(b"Hello plain text resume content"), "resume.txt"),
            "job_description": "We are seeking a senior full stack Python and React engineer with 5 years experience."
        }
        response = self.client.post("/api/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res = response.get_json()
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "InvalidFileType")

    def test_analyze_oversized_file(self):
        """Test POST /api/analyze with file exceeding MAX_CONTENT_LENGTH returns 413 FileSizeExceeded."""
        self.login_test_user()
        # Create bytes larger than 5 MB
        large_bytes = b"%PDF-1.4\n" + (b"0" * (5 * 1024 * 1024 + 1024))
        data = {
            "resume": (io.BytesIO(large_bytes), "oversized.pdf"),
            "job_description": "We are seeking a senior full stack Python and React engineer with 5 years experience."
        }
        response = self.client.post("/api/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 413)
        res = response.get_json()
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "FileSizeExceeded")

    def test_history_item_retrieval_and_user_isolation(self):
        """Test user history record retrieval and cross-user data isolation."""
        # 1. Login user A and perform an analysis to populate history
        user_a = self.login_test_user()
        jd = "We are seeking a Machine Learning Engineer with Python, PyTorch, Docker, and SQL experience."
        res_a = self.client.post("/api/analyze", data={
            "resume": (io.BytesIO(self.valid_pdf_bytes), "sample_resume_swe.pdf"),
            "job_description": jd
        }, content_type="multipart/form-data")
        self.assertEqual(res_a.status_code, 200)
        analysis_id = res_a.get_json().get("saved_history_id")
        self.assertIsNotNone(analysis_id)

        # 2. User A can retrieve the specific analysis item
        item_resp = self.client.get(f"/api/history/{analysis_id}")
        self.assertEqual(item_resp.status_code, 200)
        self.assertEqual(item_resp.get_json()["item"]["id"], analysis_id)

        # 3. Login user B
        user_b = self.login_test_user()
        self.assertNotEqual(user_a["id"], user_b["id"])

        # 4. User B cannot access User A's history record (404 isolation)
        forbidden_resp = self.client.get(f"/api/history/{analysis_id}")
        self.assertEqual(forbidden_resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()

