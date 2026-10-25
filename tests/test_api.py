"""
tests/test_api.py - Integration tests for Flask endpoints and HTTP error handling.
"""
import io
import os
import unittest
from app import app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALID_PDF_PATH = os.path.join(BASE_DIR, "sample_data", "sample_resume_swe.pdf")
SCANNED_PDF_PATH = os.path.join(BASE_DIR, "sample_data", "scanned_resume.pdf")


class TestParichayAPI(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

        with open(VALID_PDF_PATH, "rb") as f:
            self.valid_pdf_bytes = f.read()

        with open(SCANNED_PDF_PATH, "rb") as f:
            self.scanned_pdf_bytes = f.read()

    def test_health_endpoint(self):
        """Test GET /api/health returns 200 OK."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "Parichay Resume Intelligence")

    def test_sample_jds_endpoint(self):
        """Test GET /api/sample-jds returns curated list of JDs."""
        response = self.client.get("/api/sample-jds")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(len(data["sample_jds"]), 0)

    def test_analyze_missing_inputs(self):
        """Test POST /api/analyze without resume or JD returns 400."""
        # Missing both
        response = self.client.post("/api/analyze", data={})
        self.assertEqual(response.status_code, 400)

        # Missing resume
        response = self.client.post("/api/analyze", data={"job_description": "We need Python developers."})
        self.assertEqual(response.status_code, 400)

    def test_analyze_scanned_pdf_rejection(self):
        """Test POST /api/analyze with image-only/scanned PDF returns 400 with explanation."""
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
        self.assertIn("executive_summary", res_data["recommendations"])


if __name__ == "__main__":
    unittest.main()
