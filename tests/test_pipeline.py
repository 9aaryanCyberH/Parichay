"""
tests/test_pipeline.py - Comprehensive tests for PDF parsing, entity extraction, and matching.
"""
import os
import unittest
from services.pdf_parser import PDFParser, PDFParsingError
from services.extractor import ResumeExtractor, JobDescriptionParser
from services.matcher import ResumeJobMatcher
from services.ai_advisor import AIAdvisor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALID_PDF_PATH = os.path.join(BASE_DIR, "sample_data", "sample_resume_swe.pdf")
SCANNED_PDF_PATH = os.path.join(BASE_DIR, "sample_data", "scanned_resume.pdf")


class TestParichayPipeline(unittest.TestCase):

    def setUp(self):
        with open(VALID_PDF_PATH, "rb") as f:
            self.valid_pdf_bytes = f.read()

        with open(SCANNED_PDF_PATH, "rb") as f:
            self.scanned_pdf_bytes = f.read()

        self.sample_jd_text = """
        We are seeking a Machine Learning Engineer with 2+ years of experience.
        Must be proficient in Python, PyTorch, Docker, PostgreSQL, and Scikit-Learn.
        Nice to have: Kubernetes, AWS, and FastAPI.
        Strong problem solving, teamwork, and communication skills required.
        Bachelor's degree in Computer Science or related field.
        """

    def test_pdf_extraction_valid(self):
        """Verify normal resume PDF extracts text, page count, and metrics."""
        result = PDFParser.extract_text_from_bytes(self.valid_pdf_bytes, "resume.pdf")
        self.assertIn("AARAV SHARMA", result["text"])
        self.assertGreater(result["word_count"], 100)
        self.assertEqual(result["page_count"], 1)
        self.assertFalse(result["is_scanned"])

    def test_pdf_extraction_scanned_rejection(self):
        """Verify scanned/unreadable PDF triggers a clear PDFParsingError."""
        with self.assertRaises(PDFParsingError) as ctx:
            PDFParser.extract_text_from_bytes(self.scanned_pdf_bytes, "scanned.pdf")
        self.assertTrue(
            "very little or no readable text" in str(ctx.exception).lower() or
            "scanned" in str(ctx.exception).lower()
        )

    def test_resume_extraction(self):
        """Verify contact, section segmentation, and skill taxonomy extraction."""
        pdf_res = PDFParser.extract_text_from_bytes(self.valid_pdf_bytes)
        text = pdf_res["text"]

        contact = ResumeExtractor.extract_contact_info(text)
        self.assertEqual(contact["name"], "Aarav Sharma")
        self.assertIn("aarav.sharma.dev@gmail.com", contact["email"])
        self.assertIsNotNone(contact["phone"])

        sections = ResumeExtractor.segment_sections(text)
        self.assertIn("education", sections)
        self.assertIn("skills", sections)
        self.assertIn("projects", sections)
        self.assertIn("experience", sections)

        skills = ResumeExtractor.extract_skills(text)
        tech_skills = skills["technical_skills"]
        self.assertIn("Python", tech_skills)
        self.assertIn("PyTorch", tech_skills)
        self.assertIn("Docker", tech_skills)
        self.assertIn("PostgreSQL", tech_skills)
        self.assertIn("FastAPI", tech_skills)

    def test_job_description_parsing(self):
        """Verify JD parsing detects target skills, experience level, and role seniority."""
        jd_info = JobDescriptionParser.parse_job_description(self.sample_jd_text)
        jd_tech = jd_info["skills"]["technical_skills"]
        self.assertIn("Python", jd_tech)
        self.assertIn("PyTorch", jd_tech)
        self.assertIn("Docker", jd_tech)
        self.assertEqual(jd_info["experience_years"], "2+ years")

    def test_matcher_scoring_and_explainability(self):
        """Verify TF-IDF cosine similarity, skill overlap, and transparent score calculation."""
        pdf_res = PDFParser.extract_text_from_bytes(self.valid_pdf_bytes)
        resume_text = pdf_res["text"]
        resume_skills = ResumeExtractor.extract_skills(resume_text)
        resume_sections = ResumeExtractor.segment_sections(resume_text)

        jd_info = JobDescriptionParser.parse_job_description(self.sample_jd_text)
        jd_skills = jd_info["skills"]

        match_res = ResumeJobMatcher.match(
            resume_text=resume_text,
            jd_text=self.sample_jd_text,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            resume_sections=resume_sections
        )

        # Check alignment score bounds
        self.assertGreaterEqual(match_res["score"], 60)
        self.assertLessEqual(match_res["score"], 100)
        
        # Verify matched skills
        matched = match_res["skills_analysis"]["matched_technical"]
        self.assertIn("Python", matched)
        self.assertIn("PyTorch", matched)
        self.assertIn("Docker", matched)
        self.assertIn("PostgreSQL", matched)

        # Verify missing skills in JD (Kubernetes is not in resume)
        missing = match_res["skills_analysis"]["missing_technical"]
        self.assertIn("Kubernetes", missing)

        # Check score breakdown transparency
        breakdown = match_res["score_breakdown"]
        self.assertIn("overall_score", breakdown)
        self.assertEqual(len(breakdown["components"]), 4)
        self.assertIn("formula_explanation", breakdown)

    def test_ai_advisor_fallback(self):
        """Verify advisor returns grounded recommendations even without external API key."""
        pdf_res = PDFParser.extract_text_from_bytes(self.valid_pdf_bytes)
        resume_text = pdf_res["text"]
        resume_skills = ResumeExtractor.extract_skills(resume_text)
        resume_sections = ResumeExtractor.segment_sections(resume_text)
        contact = ResumeExtractor.extract_contact_info(resume_text)

        resume_data = {
            "contact": contact,
            "skills": resume_skills,
            "sections": resume_sections
        }
        jd_info = JobDescriptionParser.parse_job_description(self.sample_jd_text)
        match_res = ResumeJobMatcher.match(
            resume_text=resume_text,
            jd_text=self.sample_jd_text,
            resume_skills=resume_skills,
            jd_skills=jd_info["skills"],
            resume_sections=resume_sections
        )

        advice = AIAdvisor.generate_recommendations(
            resume_data=resume_data,
            jd_data=jd_info,
            match_data=match_res,
            api_key=""  # Test deterministic fallback
        )

        self.assertIn("executive_summary", advice)
        self.assertIn("Aarav Sharma", advice["executive_summary"])
        self.assertGreater(len(advice["bullet_enhancements"]), 0)
        self.assertGreater(len(advice["gap_mitigation_plan"]), 0)


if __name__ == "__main__":
    unittest.main()
