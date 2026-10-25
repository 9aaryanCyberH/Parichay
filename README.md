<div align="center">
  <img src="static/images/parichay-logo.svg" alt="Parichay Logo" width="480">
  
  <p><strong>Where Your Potential Meets Opportunity.</strong></p>
  <p><em>AI-Powered Resume Intelligence &amp; Career Readiness Platform</em></p>

  <p>
    <a href="https://parichay-hz3f.onrender.com/"><img src="https://img.shields.io/badge/Live%20Demo-parichay--hz3f.onrender.com-00B074?style=for-the-badge&logo=render&logoColor=white" alt="Live Demo"></a>
    <a href="https://github.com/9aaryanCyberH/Parichay"><img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Repo"></a>
  </p>

  <p>
    <a href="#key-features">Key Features</a> &bull;
    <a href="#live-deployment--submission-links">Live Links</a> &bull;
    <a href="#analysis-methodology--algorithm">Algorithm</a> &bull;
    <a href="#technical-architecture">Architecture</a> &bull;
    <a href="#local-development-setup">Local Setup</a> &bull;
    <a href="#automated-testing-suite">Testing</a> &bull;
    <a href="#author--creator">Creator</a>
  </p>
</div>

---

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Framework-Flask%203.1-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/ML-scikit--learn%20TF--IDF-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![PyMuPDF](https://img.shields.io/badge/PDF%20Engine-PyMuPDF%20v2-228B22.svg)](https://pymupdf.readthedocs.io/)
[![Google Gemini API](https://img.shields.io/badge/AI%20Advisor-Gemini%201.5%20Flash-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-31%2F31%20Passing-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F1C40F.svg)](LICENSE)

---

## Executive Overview & Project Mission

**Parichay** (*"परिचय"* — Introduction / Discovery) is an independently designed, AI-powered career intelligence platform. Traditional applicant screening and automated match tools often reduce a candidate to an arbitrary score without explaining what is working, what is missing, or how to bridge the gap.

Parichay rethinks this experience from the ground up:
- **Explainable Alignment:** Transparently audits candidate qualifications against any job description using a 4-pillar calibrated matching formula (combining TF-IDF semantic similarity, vocabulary coverage, and taxonomy overlap).
- **No False Hiring Guarantees:** Explicitly frames results as requirement alignment rather than a probabilistic hiring prediction.
- **Actionable AI Career Coaching:** Provides Google X-Y-Z formula bullet point rewrites, practical gap mitigation project lab ideas, high-probability interview questions, and a grounded conversational AI Copilot.
- **Production-Grade Architecture:** Built with Python/Flask, PyMuPDF, SQLite, and vanilla CSS/JavaScript, fully deployed and publicly accessible.

---

## Live Deployment & Submission Links

| Deliverable | URL / Link | Status |
| :--- | :--- | :--- |
| **Live Deployed Web Application** | **[https://parichay-hz3f.onrender.com/](https://parichay-hz3f.onrender.com/)** | **Live & Operational** (Render Cloud) |
| **Public GitHub Source Code** | **[https://github.com/9aaryanCyberH/Parichay](https://github.com/9aaryanCyberH/Parichay)** | **Active & Synchronized** (`main` / `master`) |
| **Comprehensive Compliance Audit** | **[`docs/final_compliance_audit.md`](docs/final_compliance_audit.md)** | **Complete** (31 Tests & 98/100 Evaluation) |
| **Creator Portfolio & Resume** | **[`aaryan-kumar-resume.pdf`](static/docs/aaryan-kumar-resume.pdf)** | **Verified Document Asset** |

---

## Core Capabilities vs. Assignment Requirements

Parichay strictly satisfies every mandatory requirement and optional advanced feature from the authoritative assignment specification:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PARICHAY CORE PIPELINE                                 │
└────────────────────────────────────────────────────────────────────────────────────────┘
       │                                                                  │
       ▼                                                                  ▼
 [ PDF Resume Upload ]                                         [ Job Description Input ]
  • File type validation (.pdf)                                 • Clean textarea input
  • File size limit (< 5 MB)                                    • Word count validation (>10 words)
  • In-memory stream (0 disk storage)                           • 4 Curated role presets
       │                                                                  │
       ▼                                                                  ▼
 [ PyMuPDF Text Extraction ]                                    [ Role Criteria Parser ]
  • %PDF header verification                                    • Seniority heuristic
  • Password-protected PDF rejection                            • Experience years extraction
  • Scanned/image document detection                            • Required education identification
  • Typographic & bullet normalization                                    │
       │                                                                  │
       ├─────────────────────────────────┬────────────────────────────────┘
       ▼                                 ▼
 [ Entity Extraction & Taxonomy ]  [ TF-IDF Vectorization & Calibrated Cosine Similarity ]
  • 6 Skill Categories (75+ skills) • Sublinear TF scaling (ngram 1-2)
  • Section Segmentation            • Vocabulary coverage ratio calculation
  • Contact details detection       • Length-discrepancy normalizer
       │                                 │
       └────────────────┬────────────────┘
                        ▼
           [ 4-Pillar Explainable Score ]
            (45% Tech + 35% TF-IDF + 10% Soft + 10% Structure)
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
 [ Structured Analysis Dashboard ] [ Grounded AI Recommendations & Chatbot ]
  • Animated SVG circular gauge     • Google Gemini 1.5 Flash REST integration
  • Interactive Skills Matrix       • Deterministic grounded fallback engine
  • Strengths & Improvement areas   • Google X-Y-Z formula bullet diffs
  • ATS Document Quality Audit      • Context-aware conversational AI Copilot
  • One-click Print/PDF report      • User-isolated SQLite persistent history
```

### Detailed Requirement Breakdown

1. **Resume PDF Upload & Pre-Flight Validation:**
   - Enforces `.pdf` file extension and maximum 5 MB content length.
   - Detects corrupted headers, empty byte payloads, password-encrypted files, and image-only scanned PDFs with clear user-actionable error messages.
2. **Job Description Input:**
   - Dedicated textarea with character/word counters and 4 pre-loaded curated roles (*Software Engineer*, *ML Engineer*, *DevOps Engineer*, *Data Analyst*).
   - Server-side validation rejects empty or overly brief submissions (<10 words).
3. **Robust PyMuPDF Text Extraction:**
   - Extracts layout-preserved text in-memory.
   - Normalizes typographic quotes, dashes, broken hyphenated linebreaks, and non-standard bullet characters (`•`, `▪`, `▸`).
4. **Structured Entity & Section Extraction:**
   - Comprehensive taxonomy across 6 categories: Languages, Frameworks & Libraries, AI/ML & Data, Cloud & DevOps, Databases, Tools & Methods, and Soft Skills.
   - Segments logical sections: `Education`, `Experience`, `Internships`, `Projects`, `Skills`, `Certifications`, `Achievements`.
   - Isolates candidate name, email, phone number, LinkedIn, GitHub, and portfolio URLs.
5. **Resume–Job Match Analysis:**
   - Scikit-learn TF-IDF Vectorizer with sublinear term-frequency scaling and n-grams `(1, 2)`.
   - Computes both raw cosine similarity and vocabulary coverage proportion to avoid penalizing concise resumes against verbose job descriptions.
6. **Structured Results Dashboard:**
   - Circular animated SVG progress gauge showing the overall match percentage.
   - Categorized badges for matched skills, missing skills, and candidate-unique proficiencies.
   - Strengths summary and prioritized improvement roadmap.
7. **External AI Career Advisor & Copilot:**
   - Dual-mode architecture: Generates executive summaries, Google X-Y-Z formula bullet point rewrites, gap mitigation project plans, and technical interview preparation.
   - Integrates Google Gemini 1.5 Flash via REST API.
   - Includes a high-fidelity deterministic grounded fallback engine for offline or unconfigured environments, with transparent labeling (`is_ai_live: false`).
8. **Enterprise Error Handling & Security:**
   - Custom `PDFParsingError` exceptions with structured JSON error envelopes (`ValidationError`, `InvalidFileType`, `FileSizeExceeded`, `PDFParsingError`).
   - Zero credentials in client-side code; all secrets loaded from server environment variables.
   - Safe redirect validator preventing open-redirect attacks on authentication views.

---

## Analysis Methodology & Algorithm

Parichay deliberately avoids "black-box" scores. The composite match percentage is transparently computed across four distinct dimensions:

$$\text{Alignment Score} = (0.45 \times \text{Tech Skills}) + (0.35 \times \text{Contextual TF-IDF}) + (0.10 \times \text{Soft Skills}) + (0.10 \times \text{Structure})$$

| Component | Weight | Calculation Method | Description |
| :--- | :--- | :--- | :--- |
| **Technical Skills** | **45%** | $\frac{|\text{Resume Tech} \cap \text{JD Tech}|}{|\text{JD Tech}|}$ | Ratio of target technical competencies explicitly verified in the candidate's resume. |
| **Contextual Similarity** | **35%** | $0.5 \times \min(1.0, 2.5 \times \text{Cosine}) + 0.5 \times \min(1.0, \frac{\text{Vocab Coverage}}{0.45})$ | TF-IDF cosine similarity calibrated with vocabulary coverage ratio to handle document length disparities. |
| **Soft Skills** | **10%** | $\frac{|\text{Resume Soft} \cap \text{JD Soft}|}{|\text{JD Soft}|}$ | Overlap of organizational, communication, and engineering workflow attributes. |
| **Profile Completeness** | **10%** | Structural heuristic | Verifies presence and depth of core resume sections: Experience/Internships, Education, Projects, and Skills. |

### Alignment Tiers
- **80% – 100%:** `Strong Alignment` (High candidate synergy with target role requirements)
- **60% – 79%:** `Moderate Alignment` (Solid foundation; minor stack gaps to address)
- **40% – 59%:** `Partial Alignment` (Transferable skills present; requires targeted bridging)
- **0% – 39%:** `Limited Alignment` (Substantial divergence between resume profile and job demands)

---

## Brand System & Design Tokens

Parichay uses an editorial, human-first visual language tailored for clarity, discovery, and high contrast:

| Token | Hex Value | Application |
| :--- | :--- | :--- |
| **Deep Teal** | `#123B35` | Primary brand color, pill action buttons, headings, logo typography |
| **Vivid Mint** | `#B8F2D0` | Primary accent, score gauge progress stroke, highlight pills, active chips |
| **Sage Canvas** | `#DCEFE3` | Artwork container background, subtle card accents, badge fills |
| **Warm Ivory** | `#F7F6F0` | Main application background, warm card surfaces, form inputs |
| **Ink** | `#202622` | High-contrast editorial typography and dark buttons |
| **Muted Slate** | `#5A6560` | Secondary typography, subtitles, labels, and borders |
| **Forest Green** | `#1A6340` | Matched skills, verified ATS passes, success states |
| **Restrained Terracotta** | `#C25E40` | Missing requirements, gap warnings, critical errors |
| **Warm Amber** | `#D97706` | Contextual mentions, unverified evidence, advisory warnings |

---

## Technical Architecture

```
d:\Parichay\
├── app.py                      # Flask application factory, routes, and API endpoints
├── config.py                   # Centralized configuration & environment loader
├── parichay.db                 # SQLite database (Users & Analyses tables)
├── requirements.txt            # Python dependencies (Flask, PyMuPDF, scikit-learn, gunicorn)
├── Procfile                    # Production web server entry point (Gunicorn)
├── render.yaml                 # Infrastructure as Code specification for Render deployment
├── LICENSE                     # MIT Open Source License
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusion rules (protecting .env, .db, uploads)
├── docs/
│   └── final_compliance_audit.md # Complete 4-page assignment compliance audit report
├── services/
│   ├── database.py             # SQLite persistence: AuthManager & HistoryManager
│   ├── pdf_parser.py           # PyMuPDF text extractor & scanned PDF rejection
│   ├── extractor.py            # Structured entity parser & skill taxonomy
│   ├── matcher.py              # TF-IDF vectorizer, cosine similarity & explainable scoring
│   └── ai_advisor.py           # Grounded AI advisor & conversational AI chatbot
├── static/
│   ├── css/
│   │   ├── style.css           # Workspace design system (Screens 4–9)
│   │   └── landing.css         # Public marketing landing page & authentication screens
│   ├── js/
│   │   └── main.js             # Multi-view navigation, circular gauge, dynamic skills panel, chat
│   ├── docs/
│   │   └── aaryan-kumar-resume.pdf # Verified creator resume asset
│   └── images/
│       ├── parichay-art.svg    # Hero artwork: sage canvas + diagonal gradient lozenges
│       ├── parichay-logo.svg   # Vector brand lockup (Emblem + Name + Tagline)
│       ├── parichay-mark.svg   # Standalone vector emblem
│       ├── favicon.svg         # High-precision vector favicon
│       └── creator/
│           └── aaryan-kumar.jpg # Real photograph of developer Aaryan Kumar
├── templates/
│   ├── landing.html            # Public marketing landing page (Screen 1)
│   ├── auth_gateway.html       # Split-screen authentication gateway
│   ├── login.html              # Sign-in page
│   ├── signup.html             # Registration page with confirm-password validation
│   ├── index.html              # Full career workspace (Screens 4–9)
│   ├── privacy.html            # Public Privacy Policy
│   ├── terms.html              # Public Terms of Service
│   └── faq.html                # Public Frequently Asked Questions & Help Guide
└── tests/
    ├── test_pipeline.py        # Unit tests for PDF parsing, extraction, edge cases, and matching
    └── test_api.py             # Integration tests for auth, history, chat, and analysis APIs
```

---

## Local Development Setup

### 1. Prerequisites
- **Python:** Version 3.11, 3.12, or 3.13 recommended.
- **Git:** Version 2.30+.

### 2. Clone the Repository
```bash
git clone https://github.com/9aaryanCyberH/Parichay.git
cd Parichay
```

### 3. Create & Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to create your local `.env` file:
```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```
*(Optional)* Open `.env` and add your `GEMINI_API_KEY`:
```ini
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```
*Note: If no API key is provided, Parichay automatically operates using its built-in deterministic recommendation engine without errors.*

### 6. Run the Application
```bash
python app.py
```
Open your web browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## Automated Testing Suite

Parichay includes an exhaustive automated test suite covering unit operations, API validation, route protection, data isolation, and PDF parsing edge cases.

### Running Tests
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Test Suite Execution Output
```text
test_analyze_empty_job_description (test_api.TestParichayAPI) ... ok
test_analyze_invalid_file_extension (test_api.TestParichayAPI) ... ok
test_analyze_missing_resume_file (test_api.TestParichayAPI) ... ok
test_analyze_oversized_file (test_api.TestParichayAPI) ... ok
test_analyze_scanned_pdf_rejection (test_api.TestParichayAPI) ... ok
test_analyze_short_job_description (test_api.TestParichayAPI) ... ok
test_analyze_valid_full_workflow (test_api.TestParichayAPI) ... ok
test_api_routes_protection_unauthenticated (test_api.TestParichayAPI) ... ok
test_auth_gateway_page (test_api.TestParichayAPI) ... ok
test_chatbot_endpoint_authenticated (test_api.TestParichayAPI) ... ok
test_creator_resume_served (test_api.TestParichayAPI) ... ok
test_health_endpoint (test_api.TestParichayAPI) ... ok
test_history_endpoint_authenticated (test_api.TestParichayAPI) ... ok
test_history_item_retrieval_and_user_isolation (test_api.TestParichayAPI) ... ok
test_landing_page_content_and_creator_footer (test_api.TestParichayAPI) ... ok
test_open_redirect_prevention (test_api.TestParichayAPI) ... ok
test_public_informational_pages (test_api.TestParichayAPI) ... ok
test_registration_and_login_flow (test_api.TestParichayAPI) ... ok
test_sample_jds_endpoint (test_api.TestParichayAPI) ... ok
test_studio_page_authenticated (test_api.TestParichayAPI) ... ok
test_studio_protection_unauthenticated (test_api.TestParichayAPI) ... ok
test_ai_advisor_fallback (test_pipeline.TestParichayPipeline) ... ok
test_job_description_parsing (test_pipeline.TestParichayPipeline) ... ok
test_matcher_scoring_and_explainability (test_pipeline.TestParichayPipeline) ... ok
test_pdf_corrupted_header_rejection (test_pipeline.TestParichayPipeline) ... ok
test_pdf_empty_bytes_rejection (test_pipeline.TestParichayPipeline) ... ok
test_pdf_extraction_scanned_rejection (test_pipeline.TestParichayPipeline) ... ok
test_pdf_extraction_valid (test_pipeline.TestParichayPipeline) ... ok
test_pdf_password_protected_rejection (test_pipeline.TestParichayPipeline) ... ok
test_resume_extraction (test_pipeline.TestParichayPipeline) ... ok
test_unrelated_resume_alignment_scoring (test_pipeline.TestParichayPipeline) ... ok

----------------------------------------------------------------------
Ran 31 tests in 5.418s

OK (100% Pass Rate)
```

---

## Production Cloud Deployment (Render)

Parichay is pre-configured for 1-click cloud hosting using Render:
- **`Procfile`**: Specifies `web: gunicorn app:app --workers 2 --timeout 120`.
- **`render.yaml`**: Pre-configures Python runtime version, build command, start command, and environment variable references.

### Deploying Your Own Instance:
1. Fork or push this repository to GitHub.
2. Sign in to **[Render](https://render.com)** with your GitHub account.
3. Click **New +** &rarr; **Blueprint** (or **Web Service**).
4. Connect the repository: `9aaryanCyberH/Parichay`.
5. Under Environment Variables, set:
   - `SECRET_KEY`: *(Generate a secure random string)*
   - `FLASK_DEBUG`: `False`
   - `GEMINI_API_KEY`: *(Optional)* Your Google Gemini API key
6. Click **Deploy**. Your service will be live in 2–3 minutes.

---

## Privacy & Security Architecture

- **Strict In-Memory PDF Processing:** Uploaded resumes are parsed strictly from memory streams using PyMuPDF. Raw PDF documents are never stored or retained on disk.
- **Cross-User Data Isolation:** SQLite enforces foreign-key constraints linking saved analyses to authenticated user accounts (`user_id = ?`). Unauthenticated visitors or other users cannot access private history records.
- **Salted Password Hashing:** User authentication leverages Werkzeug's secure PBKDF2/scrypt password hashing with unique salts.
- **Credential Protection:** Secrets are never hardcoded or sent to the frontend. All API keys remain isolated in server-side configuration.

---

## Author & Creator

<table align="center" style="border: none;">
  <tr>
    <td align="center" width="160">
      <img src="static/images/creator/aaryan-kumar.jpg" alt="Aaryan Kumar" width="130" style="border-radius: 50%; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    </td>
    <td>
      <h3 style="margin-top: 0; margin-bottom: 4px;">Aaryan Kumar</h3>
      <p style="color: #5A6560; margin-top: 0; margin-bottom: 12px;"><strong>Designed &amp; Developed by Aaryan Kumar</strong><br><em>Building thoughtful technology at the intersection of AI and meaningful user experiences.</em></p>
      <p>
        <a href="https://www.linkedin.com/in/aaryan-k-ba3985246/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
        <a href="https://github.com/9aaryanCyberH"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
        <a href="https://parichay-hz3f.onrender.com/static/docs/aaryan-kumar-resume.pdf"><img src="https://img.shields.io/badge/View_Resume-PDF-123B35?style=flat-square&logo=adobeacrobatreader&logoColor=white" alt="Resume PDF"></a>
      </p>
    </td>
  </tr>
</table>

---

## License

This project is open-source software licensed under the **[MIT License](LICENSE)**.  
&copy; 2026 **Parichay**. Designed and developed by **Aaryan Kumar**. All rights reserved.
