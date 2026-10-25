"""
sample_data/generate_sample_pdf.py - Creates realistic sample PDFs for test suite and demo testing.
Generates:
1. sample_resume_swe.pdf (valid technical resume)
2. scanned_resume.pdf (image/empty PDF to test scanner detection)
"""
import os
import fitz  # PyMuPDF

SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_valid_resume():
    output_path = os.path.join(SAMPLE_DIR, "sample_resume_swe.pdf")
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    content = """AARAV SHARMA
Kolkata, WB | aarav.sharma.dev@gmail.com | +91 98765 43210
linkedin.com/in/aarav-sharma-dev | github.com/aaravsharma-dev | aaravsharma.dev

SUMMARY
Results-driven Software Engineer with practical expertise in Python, PyTorch, React, and cloud architectures. Passionate about machine learning pipelines, scalable backend engineering, and robust software design.

EDUCATION
B.Tech in Computer Science & Engineering | 2021 - 2025
Institute of Engineering & Technology, Kolkata
CGPA: 8.85 / 10.0

TECHNICAL SKILLS
- Languages: Python, JavaScript, TypeScript, C++, SQL, Bash/Shell, HTML/CSS
- Frameworks & Libraries: React, Node.js, Flask, FastAPI, PyTorch, Scikit-Learn, Pandas, NumPy
- Cloud & DevOps: Docker, Git, CI/CD, GitHub Actions, AWS, Linux
- Databases: PostgreSQL, MongoDB, Redis, SQLite
- Concepts: Machine Learning, REST APIs, System Design, Data Analysis, Unit Testing, Agile/Scrum

EXPERIENCE
Software Engineering Intern | TechFlow Solutions | Jan 2024 - Jun 2024
- Engineered high-throughput REST APIs using Python (FastAPI) and PostgreSQL, serving 50,000+ weekly requests.
- Integrated Redis caching layer, decreasing average response latency from 240ms to 48ms.
- Containerized microservices with Docker and configured GitHub Actions CI/CD deployment pipelines.
- Collaborated in an agile scrum team of 6 engineers with daily standups and bi-weekly sprint reviews.

PROJECTS
MedVision - AI-Powered Medical Imaging Diagnosis | PyTorch, Python, Flask, Docker
- Built an image classification system using PyTorch and OpenCV achieving 94.2% diagnostic accuracy.
- Containerized the inference pipeline with Docker and deployed a REST API endpoint for real-time scans.
- Designed an interactive web dashboard in React to visualize model confidence scores and heatmaps.

CareerCompass - Intelligent Job Matcher & Resume Intelligence | Python, Scikit-Learn, React, PostgreSQL
- Implemented TF-IDF vectorization and cosine similarity scoring to match candidate skills with vacancies.
- Architected PostgreSQL database schemas with indexing, reducing search execution times by 40%.
- Integrated unit tests with Pytest achieving 92% code coverage across core matching algorithms.

CERTIFICATIONS
- DeepLearning.AI: Machine Learning Specialization (Coursera)
- AWS Certified Cloud Practitioner
- Problem Solving (Intermediate) Certificate - HackerRank

ACHIEVEMENTS
- Finalist, Smart India Hackathon (SIH) 2023
- Solved 450+ data structures & algorithms problems on LeetCode
"""
    # Insert text into PDF
    rect = fitz.Rect(40, 40, 555, 800)
    page.insert_textbox(rect, content, fontsize=10.5, fontname="helv", color=(0.1, 0.1, 0.1))
    doc.save(output_path)
    doc.close()
    print(f"Generated: {output_path}")

def create_scanned_dummy():
    output_path = os.path.join(SAMPLE_DIR, "scanned_resume.pdf")
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    # Insert minimal text (less than threshold) to simulate scanned or empty PDF
    rect = fitz.Rect(50, 50, 500, 100)
    page.insert_textbox(rect, "SCANNED DOCUMENT", fontsize=14, fontname="helv")
    doc.save(output_path)
    doc.close()
    print(f"Generated: {output_path}")

if __name__ == "__main__":
    create_valid_resume()
    create_scanned_dummy()
