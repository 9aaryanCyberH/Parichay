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

    def test_pdf_empty_bytes_rejection(self):
        """Verify empty (0 bytes) upload raises PDFParsingError."""
        with self.assertRaises(PDFParsingError) as ctx:
            PDFParser.extract_text_from_bytes(b"", "empty.pdf")
        self.assertIn("empty (0 bytes)", str(ctx.exception))

    def test_pdf_corrupted_header_rejection(self):
        """Verify file lacking %PDF header raises PDFParsingError."""
        with self.assertRaises(PDFParsingError) as ctx:
            PDFParser.extract_text_from_bytes(b"NOT_A_PDF_FILE_HEADER_DATA_12345", "corrupt.pdf")
        self.assertIn("valid PDF header format", str(ctx.exception))

    def test_pdf_password_protected_rejection(self):
        """Verify password-protected/encrypted PDF is cleanly rejected."""
        import pymupdf as fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 72), "Confidential Resume Data")
        perm = int(fitz.PDF_PERM_ACCESSIBILITY | fitz.PDF_PERM_PRINT)
        encrypt_meth = fitz.PDF_ENCRYPT_AES_256
        encrypted_bytes = doc.tobytes(encryption=encrypt_meth, user_pw="secret123", owner_pw="owner123", permissions=perm)
        doc.close()

        with self.assertRaises(PDFParsingError) as ctx:
            PDFParser.extract_text_from_bytes(encrypted_bytes, "encrypted.pdf")
        self.assertIn("password-protected", str(ctx.exception))

    def test_unrelated_resume_alignment_scoring(self):
        """Verify completely unrelated resume receives a low alignment score and Limited Alignment tier."""
        chef_resume = """
        MARCUS BEAN
        Executive Pastry Chef & Culinary Director
        marcus.bean.pastry@culinary.org | +1 (555) 432-8765 | Chicago, IL

        PROFESSIONAL SUMMARY
        Award-winning pastry chef with 8 years of fine dining kitchen management, artisan bread baking,
        chocolate tempering, menu pricing, inventory sourcing, and staff supervision.

        EXPERIENCE
        Executive Pastry Chef — The Grand Bistro (2020 - Present)
        - Managed daily pastry kitchen operations, food prep safety standards, and inventory.
        - Designed seasonal dessert menus and trained 6 line cooks in French baking techniques.

        EDUCATION
        Associate Degree in Culinary Arts — Culinary Institute of America (2016)

        SKILLS
        Baking, French Pastries, Kitchen Safety, Food Cost Management, Plating, Menu Design
        """
        resume_skills = ResumeExtractor.extract_skills(chef_resume)
        resume_sections = ResumeExtractor.segment_sections(chef_resume)
        jd_info = JobDescriptionParser.parse_job_description(self.sample_jd_text)

        match_res = ResumeJobMatcher.match(
            resume_text=chef_resume,
            jd_text=self.sample_jd_text,
            resume_skills=resume_skills,
            jd_skills=jd_info["skills"],
            resume_sections=resume_sections
        )

        self.assertLessEqual(match_res["score"], 25)
        self.assertEqual(match_res["fit_tier"], "Limited Alignment")
        self.assertEqual(len(match_res["skills_analysis"]["matched_technical"]), 0)

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


