<div align="center">
  <img src="static/images/parichay-logo.svg" alt="Parichay Logo" width="460">
  
  <p><strong>Where Your Potential Meets Opportunity.</strong></p>
  <p><em>AI-Powered Resume Intelligence &amp; Career Readiness Platform</em></p>
</div>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/ML-scikit--learn%20TF--IDF-orange.svg)](https://scikit-learn.org/)
[![PyMuPDF](https://img.shields.io/badge/PDF-PyMuPDF-green.svg)](https://pymupdf.readthedocs.io/)
[![SQLite](https://img.shields.io/badge/Storage-SQLite3-lightgrey.svg)](https://sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Brand System & Design Tokens

Parichay uses an editorial, human-first visual language tailored for clarity and discovery:

| Token | Value | Role |
| :--- | :--- | :--- |
| **Deep Teal** | `#123B35` | Primary brand color, dark pill action buttons, headings, logo typography |
| **Vivid Mint** | `#B8F2D0` | Primary accent, score gauge progress stroke, highlight pills, active chips |
| **Sage Canvas** | `#DCEFE3` | Artwork container background, subtle card accents, badge fills |
| **Warm Ivory** | `#F7F6F0` | Main application background, warm card surfaces, forms |
| **Ink** | `#202622` | High-contrast editorial typography and dark buttons |
| **Muted Slate** | `#5A6560` | Secondary typography, subtitles, labels, and borders |
| **Forest Green** | `#1A6340` | Matched skills, verified ATS passes, success states |
| **Restrained Terracotta** | `#C25E40` | Missing requirements, gap warnings, critical errors |
| **Warm Amber** | `#D97706` | Contextual mentions, unverified evidence, advisory warnings |

---

## The Parichay Product Experience

Parichay is organized into distinct, interactive product screens:

1. **Public Landing Page (`/` — Screen 1)**
   - Split hero layout with brand headline *"Where Your Potential Meets Opportunity."*
   - Clear value proposition and primary call-to-action pill *"Analyze My Resume"*.
   - 3-step numbered workflow indicator: `1 Upload Your Resume` &bull; `2 Add Job Description` &bull; `3 Get Detailed Insights`.
   - Brand artwork panel with overlapping diagonal gradient lozenges on sage canvas.
   - Core feature pillars, transparent methodology explanation, and privacy pledge.

2. **Secure Authentication (`/login` & `/signup` — Screens 2 & 3)**
   - Split card experience: left sage artwork canvas with brand header; right warm ivory form container.
   - Real backend authentication powered by SQLite (`parichay.db`) and Werkzeug secure password hashing (`generate_password_hash` / `check_password_hash`).
   - Secure cookie session management with cross-user data isolation.
   - Anonymous/guest candidates can still test the analysis engine without forced sign-up friction.

3. **Resume Intelligence Studio (`/studio` or `/app` — Screen 4)**
   - Two-column input layout:
     - Column 1: PDF resume dropzone with drag-and-drop, file size check, and one-click sample resume shortcut (`Aarav Sharma — Software Engineer`).
     - Column 2: Target job description textarea with one-click popular role presets (Software Engineer, Data Analyst, ML Engineer, DevOps Engineer).
   - Real-time analysis trigger via `POST /api/analyze`.

4. **Analysis Result Overview (Screen 5)**
   - Circular SVG match score gauge with Deep Teal and Mint ring animation.
   - Candidate contact metadata and verified links.
   - 4-pillar explainable breakdown table: Technical Skills (45%), Semantic TF-IDF (35%), Soft Skills (10%), Structure (10%).
   - 4 Key Insights summary cards (Matched Skills, Missing Skills, Strong Points, Recommendations).
   - Top action pills: *Export Report* (print PDF) and *New Analysis*.

5. **Skills Matrix (Screen 6)**
   - Tab filters: *Matched Skills*, *Missing Skills*, *Additional Skills* with live count pills.
   - Two-column interactive layout:
     - Left column: Skill list items with status icons and Required/Preferred tags.
     - Right column: Dynamic *Skill Details* card updating live upon clicking any skill, displaying description, verified evidence bullet points from the resume, and a calibrated confidence meter bar.

6. **AI Recommendations (Screen 7)**
   - Tabs: *Resume Improvements*, *Skill Development*, *Interview Preparation*.
   - 3 numbered recommendation cards with *"View Suggestion"* modal popups containing Google X-Y-Z bullet rewrites and gap mitigation project plans.

7. **Parichay AI Assistant (Screen 8)**
   - Dedicated conversational chatbot panel accessible from the sidebar.
   - Context-grounded in candidate's parsed skills, missing gaps, and target role description.
   - Suggestion prompt chips for immediate career guidance.
   - Supported by Google Gemini API server-side with reliable, grounded fallback.

8. **Document Audit (Screen 9 Left)**
   - 6 ATS checks: File Format, Resume Length, Contact Information, Section Structure, Action Verbs, and Readability.

9. **Profile & Settings (Screen 9 Right)**
   - Profile tab for updating full name and reviewing account tier.
   - Connected to SQLite backend via `POST /api/settings`.

10. **Persistent User History ("My Analyses")**
    - Automatically records analysis reports for logged-in users.
    - View, reload, and delete historical resume analyses.

---

## Technical Architecture

```
d:\Parichay\
├── app.py                      # Flask factory, public & protected routes, API endpoints
├── config.py                   # Centralized configuration & environment loader
├── parichay.db                 # SQLite database (Users & Analyses tables)
├── requirements.txt            # Python dependencies (Flask, PyMuPDF, scikit-learn, gunicorn)
├── Procfile                    # Production web server entrypoint (Gunicorn)
├── render.yaml                 # Render cloud deployment configuration
├── .env.example                # Environment variables template
├── services/
│   ├── database.py             # SQLite persistence: AuthManager & HistoryManager
│   ├── pdf_parser.py           # PyMuPDF text extractor & scanned PDF rejection
│   ├── extractor.py            # Structured entity parser & skill taxonomy
│   ├── matcher.py              # TF-IDF vectorizer, cosine similarity & explainable scoring
│   └── ai_advisor.py           # Grounded AI advisor & conversational AI chatbot
├── static/
│   ├── css/
│   │   ├── style.css           # Workspace design system (Screens 4–9)
│   │   └── landing.css         # Public landing page (Screen 1) & auth screens (Screens 2 & 3)
│   ├── js/
│   │   └── main.js             # Multi-view navigation, circular gauge, skills detail panel, chatbot
│   └── images/
│       ├── parichay-art.svg    # Split-screen artwork: sage canvas + diagonal gradient lozenges
│       ├── parichay-logo.svg   # Vector brand lockup (Emblem + Name + Tagline)
│       ├── parichay-mark.svg   # Standalone vector emblem
│       └── favicon.svg         # High-precision vector favicon
├── templates/
│   ├── landing.html            # Public marketing landing page (Screen 1)
│   ├── auth_gateway.html       # Authentication gateway screen
│   ├── login.html              # Sign-in page (Screen 2)
│   ├── signup.html             # Registration page (Screen 3)
│   ├── index.html              # Full career workspace (Screens 4–9)
│   ├── privacy.html            # Public Privacy Policy
│   ├── terms.html              # Public Terms of Service
│   └── faq.html                # Public Frequently Asked Questions & Help Guide
└── tests/
    ├── test_pipeline.py        # Unit tests for PDF parsing, extraction, edge cases, and matching
    └── test_api.py             # Integration tests for auth, history, chat, and analysis APIs
```

---

## Running the Application Locally

### 1. Prerequisites & Virtual Environment
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```
*(Optional)* Add your `GEMINI_API_KEY` for live generative responses. If no key is configured, Parichay automatically operates using its grounded deterministic recommendation engine.

### 3. Start the Server
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your web browser.

### 4. Running Tests
Execute the complete automated test suite:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
All 31 unit and integration tests pass out-of-the-box.

---

## Cloud Deployment Guide (Render / Heroku)

Parichay includes production-ready deployment configurations:
- **`Procfile`**: `web: gunicorn app:app --workers 2 --timeout 120`
- **`render.yaml`**: Pre-configured Blueprint for 1-click Render deployment with Python 3.11+.

### Deploying to Render
1. Push the repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New +** &rarr; **Blueprint** (or **Web Service**).
3. Connect your repository. Render automatically reads `render.yaml` and `requirements.txt`.
4. In Environment Variables, set:
   - `SECRET_KEY`: A secure random hex string.
   - `GEMINI_API_KEY`: *(Optional)* Your Google Gemini API key.
   - `FLASK_DEBUG`: `False`.
5. Deploy. Gunicorn will serve the application on port `$PORT`.

---

## Privacy & Security Architecture

- **In-Memory PDF Processing**: Resumes are parsed strictly in memory using PyMuPDF. Raw PDF documents are never saved to disk or persistent storage.
- **Secure Authentication & Data Isolation**: Access to the Resume Intelligence Studio is protected with session cookies and salted password hashing (Werkzeug PBKDF2/scrypt). User analyses in SQLite are strictly filtered by foreign-key `user_id` ownership.
- **Protected API Credentials**: AI credentials (`GEMINI_API_KEY`) and secret keys are loaded exclusively from server environment variables via `config.py`. No secrets or API keys are ever committed to Git or exposed to client-side JavaScript.
- **Deterministic Offline Fallback**: In the absence of an external AI API key or network failure, Parichay gracefully falls back to a deterministic recommendation engine without leaking stack traces or internal errors.

