"""
app.py - Main Flask application for Parichay (AI-Powered Resume Intelligence).
Provides web routes, file upload handling, and analysis pipeline endpoints.
"""
import os
import json
import logging
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

from config import Config
from services.pdf_parser import PDFParser, PDFParsingError
from services.extractor import ResumeExtractor, JobDescriptionParser
from services.matcher import ResumeJobMatcher
from services.ai_advisor import AIAdvisor
from services.database import AuthManager, HistoryManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)


def is_safe_url(target: str) -> bool:
    """Validates that a redirect target is a safe relative URL to prevent open redirects."""
    if not target:
        return False
    # Must start with a single forward slash, not double-slash or backslash
    return target.startswith("/") and not target.startswith("//") and "\\" not in target


def login_required(f):
    """Decorator ensuring that routes are protected against unauthenticated access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        user = AuthManager.get_user_by_id(user_id) if user_id else None
        if not user:
            if user_id:
                session.clear()
            dest = request.full_path if request.query_string else request.path
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "authenticated": False,
                    "error_type": "AuthenticationRequired",
                    "message": "Authentication required. Please sign in to access Parichay Resume Studio.",
                    "redirect": url_for("auth_gateway", next=dest)
                }), 401
            return redirect(url_for("auth_gateway", next=dest))
        return f(*args, **kwargs)
    return decorated_function


# Context processor to make current_user available in all templates
@app.context_processor
def inject_current_user():
    user_id = session.get("user_id")
    if user_id:
        user = AuthManager.get_user_by_id(user_id)
        if user:
            return {"current_user": user}
        session.clear()
    return {"current_user": None}


# Load sample JDs into memory for quick serving
SAMPLE_JDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "sample_jds.json")
sample_jds_cache = []
if os.path.exists(SAMPLE_JDS_PATH):
    try:
        with open(SAMPLE_JDS_PATH, "r", encoding="utf-8") as f:
            sample_jds_cache = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load sample JDs: {e}")


# ============================================================================
# PUBLIC & WORKSPACE ROUTES
# ============================================================================
@app.route("/")
def landing():
    """Renders the public Parichay landing page."""
    return render_template("landing.html")


@app.route("/auth")
def auth_gateway():
    """
    Authentication gateway page.
    Displays when unauthenticated users attempt to Launch Studio or open protected views.
    Offers 'Sign In' or 'Create Account' with the mint/peach split-screen branding.
    """
    user_id = session.get("user_id")
    if user_id:
        if AuthManager.get_user_by_id(user_id):
            return redirect(url_for("studio"))
        session.clear()
    next_url = request.args.get("next", "")
    if not is_safe_url(next_url):
        next_url = url_for("studio")
    return render_template("auth_gateway.html", next_url=next_url)


@app.route("/privacy")
def privacy():
    """Renders the clear, transparent Parichay privacy policy."""
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    """Renders the clear, readable Parichay terms of service."""
    return render_template("terms.html")


@app.route("/faq")
def faq():
    """Renders the comprehensive Parichay help & FAQ guide."""
    return render_template("faq.html")


@app.route("/docs/<path:filename>")
def serve_docs(filename):
    """Serves verified document assets like the creator's resume PDF."""
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "docs")
    return send_from_directory(docs_dir, secure_filename(filename))


@app.route("/app")
@app.route("/studio")
@login_required
def studio():
    """Renders the main Parichay resume intelligence studio (Protected)."""
    return render_template("index.html")


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """Renders login page and handles user sign-in with safe post-auth redirect."""
    next_url = request.args.get("next") or request.form.get("next") or url_for("studio")
    if not is_safe_url(next_url):
        next_url = url_for("studio")

    user_id = session.get("user_id")
    if user_id:
        if AuthManager.get_user_by_id(user_id):
            return redirect(next_url)
        session.clear()

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        auth_res = AuthManager.authenticate_user(email, password)

        if auth_res["success"]:
            user = auth_res["user"]
            session.permanent = True
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": True, "redirect": next_url})
            return redirect(next_url)
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": False, "message": auth_res["message"]}), 400
            return render_template("login.html", error=auth_res["message"], email=email, next_url=next_url)

    return render_template("login.html", next_url=next_url)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Renders sign-up page and handles user account creation with confirm password validation."""
    next_url = request.args.get("next") or request.form.get("next") or url_for("studio")
    if not is_safe_url(next_url):
        next_url = url_for("studio")

    user_id = session.get("user_id")
    if user_id:
        if AuthManager.get_user_by_id(user_id):
            return redirect(next_url)
        session.clear()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if confirm_password and password != confirm_password:
            error_msg = "Passwords do not match. Please re-enter your password."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            return render_template("signup.html", error=error_msg, name=name, email=email, next_url=next_url)

        reg_res = AuthManager.register_user(name, email, password)

        if reg_res["success"]:
            user = reg_res["user"]
            session.permanent = True
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": True, "redirect": next_url})
            return redirect(next_url)
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": False, "message": reg_res["message"]}), 400
            return render_template("signup.html", error=reg_res["message"], name=name, email=email, next_url=next_url)

    return render_template("signup.html", next_url=next_url)


@app.route("/logout")
def logout():
    """Clears user session and redirects to public landing page."""
    session.clear()
    return redirect(url_for("landing"))


@app.route("/api/health", methods=["GET"])
def health():
    """API health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Parichay Resume Intelligence",
        "version": "1.0.0",
        "gemini_api_configured": bool(Config.GEMINI_API_KEY and not Config.GEMINI_API_KEY.startswith("your_"))
    })


@app.route("/api/sample-jds", methods=["GET"])
def get_sample_jds():
    """Returns curated sample job descriptions for quick testing."""
    return jsonify({
        "success": True,
        "sample_jds": sample_jds_cache
    })

@app.route("/sample_data/<filename>", methods=["GET"])
def get_sample_file(filename):
    """Serves sample resume and testing files safely."""
    from flask import send_from_directory
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")
    return send_from_directory(sample_dir, secure_filename(filename))


@app.route("/api/analyze", methods=["POST"])
@login_required
def analyze_resume():
    """
    Main analysis endpoint.
    Accepts:
        - resume: PDF file
        - job_description: string text
    Returns:
        Structured analysis JSON with match score, explainable breakdown,
        skills gap matrix, section inventory, and grounded recommendations.
    """
    # 1. Validate Job Description
    job_description = request.form.get("job_description", "").strip()
    if not job_description:
        return jsonify({
            "success": False,
            "error_type": "ValidationError",
            "message": "Please provide a job description or select one of the curated example roles."
        }), 400

    if len(job_description.split()) < 10:
        return jsonify({
            "success": False,
            "error_type": "ValidationError",
            "message": "The provided job description is too brief. Please provide at least 2-3 sentences outlining the role requirements."
        }), 400

    # 2. Validate Resume File
    if "resume" not in request.files:
        return jsonify({
            "success": False,
            "error_type": "ValidationError",
            "message": "No resume file was attached. Please select a PDF resume to analyze."
        }), 400

    file = request.files["resume"]
    if not file or file.filename == "":
        return jsonify({
            "success": False,
            "error_type": "ValidationError",
            "message": "Please select a valid PDF resume file from your computer."
        }), 400

    filename = secure_filename(file.filename)
    if not filename.lower().endswith(".pdf"):
        return jsonify({
            "success": False,
            "error_type": "InvalidFileType",
            "message": "Only PDF files (.pdf) are supported. Please export your resume as a text-based PDF."
        }), 400

    # Read bytes safely in memory (enforces max size limits)
    try:
        pdf_bytes = file.read()
    except Exception as e:
        return jsonify({
            "success": False,
            "error_type": "FileReadError",
            "message": f"Unable to read the uploaded file: {str(e)}"
        }), 400

    if len(pdf_bytes) > Config.MAX_CONTENT_LENGTH:
        return jsonify({
            "success": False,
            "error_type": "FileSizeExceeded",
            "message": "File exceeds the 5 MB maximum upload limit. Please upload a smaller PDF."
        }), 413

    # 3. Parse PDF with PyMuPDF
    try:
        pdf_data = PDFParser.extract_text_from_bytes(pdf_bytes, filename=filename)
    except PDFParsingError as pe:
        logger.warning(f"PDF parsing error for {filename}: {pe}")
        return jsonify({
            "success": False,
            "error_type": "PDFParsingError",
            "message": str(pe)
        }), 400
    except Exception as e:
        logger.exception("Unexpected error while parsing PDF")
        return jsonify({
            "success": False,
            "error_type": "InternalParsingError",
            "message": f"An unexpected error occurred while parsing the PDF: {str(e)}"
        }), 500

    resume_text = pdf_data["text"]

    # 4. Extract Structured Entities & Skills from Resume
    contact_info = ResumeExtractor.extract_contact_info(resume_text)
    sections = ResumeExtractor.segment_sections(resume_text)
    resume_skills = ResumeExtractor.extract_skills(resume_text)
    experience_entries = ResumeExtractor.extract_experience_entries(sections.get("experience", "") or sections.get("internships", ""))
    education_entries = ResumeExtractor.extract_education_details(sections.get("education", ""))

    # 5. Parse Job Description
    jd_data = JobDescriptionParser.parse_job_description(job_description)

    # 6. Execute TF-IDF Matching & Explainable Scoring
    try:
        match_data = ResumeJobMatcher.match(
            resume_text=resume_text,
            jd_text=job_description,
            resume_skills=resume_skills,
            jd_skills=jd_data["skills"],
            resume_sections=sections
        )
    except Exception as e:
        logger.exception("Matching calculation failed")
        return jsonify({
            "success": False,
            "error_type": "MatchingError",
            "message": f"Failed to compute similarity alignment: {str(e)}"
        }), 500

    # 7. Generate Grounded AI Recommendations
    resume_summary = {
        "contact": contact_info,
        "sections": sections,
        "skills": resume_skills,
        "word_count": pdf_data["word_count"],
        "page_count": pdf_data["page_count"]
    }

    try:
        recommendations = AIAdvisor.generate_recommendations(
            resume_data=resume_summary,
            jd_data=jd_data,
            match_data=match_data,
            api_key=Config.GEMINI_API_KEY,
            model=Config.GEMINI_MODEL
        )
    except Exception as e:
        logger.warning(f"Advisor generation encountered error: {e}")
        recommendations = AIAdvisor._generate_grounded_fallback(resume_summary, jd_data, match_data)

    # 8. Assemble Complete Response
    response_payload = {
        "success": True,
        "filename": filename,
        "document_metrics": {
            "page_count": pdf_data["page_count"],
            "word_count": pdf_data["word_count"],
            "character_count": pdf_data["char_count"]
        },
        "candidate": {
            "name": contact_info.get("name") or "Candidate",
            "email": contact_info.get("email"),
            "phone": contact_info.get("phone"),
            "linkedin": contact_info.get("linkedin"),
            "github": contact_info.get("github"),
            "portfolio": contact_info.get("portfolio")
        },
        "job_profile": {
            "role_level": jd_data.get("role_level"),
            "experience_years": jd_data.get("experience_years"),
            "required_education": jd_data.get("required_education"),
            "word_count": jd_data.get("word_count")
        },
        "alignment": {
            "score": match_data["score"],
            "fit_tier": match_data["fit_tier"],
            "tier_badge": match_data["tier_badge"],
            "raw_cosine": match_data["score_breakdown"]["raw_cosine"],
            "vocabulary_coverage_percent": match_data["score_breakdown"]["vocabulary_coverage_percent"],
            "score_breakdown": match_data["score_breakdown"]
        },
        "skills": {
            "matched_technical": match_data["skills_analysis"]["matched_technical"],
            "missing_technical": match_data["skills_analysis"]["missing_technical"],
            "candidate_unique": match_data["skills_analysis"]["candidate_unique"],
            "matched_soft": match_data["skills_analysis"]["matched_soft"],
            "missing_soft": match_data["skills_analysis"]["missing_soft"],
            "unverified_skills": match_data["skills_analysis"]["unverified_skills"],
            "counts": match_data["skills_analysis"]["counts"],
            "candidate_all_categorized": resume_skills.get("categorized", {}),
            "jd_categorized": jd_data.get("skills", {}).get("categorized", {})
        },
        "sections_detected": {
            "available_sections": list(sections.keys()),
            "education_snippets": education_entries,
            "has_experience": bool(sections.get("experience") or sections.get("internships")),
            "has_projects": bool(sections.get("projects")),
            "has_certifications": bool(sections.get("certifications"))
        },
        "audit": {
            "strengths": match_data["strengths"],
            "improvement_priorities": match_data["improvement_priorities"]
        },
        "recommendations": recommendations
    }

    # Automatically save analysis to history for authenticated users
    user_id = session.get("user_id")
    if user_id:
        role_label = jd_data.get("role_title")
        if not role_label or role_label == "Standard":
            first_line = job_description.strip().split("\n")[0].strip()
            role_label = first_line[:40] if len(first_line) > 5 else "Target Role"
        analysis_id = HistoryManager.save_analysis(
            user_id=user_id,
            filename=filename,
            candidate_name=contact_info.get("name") or "Candidate",
            role_title=role_label,
            score=match_data["score"],
            fit_tier=match_data["fit_tier"],
            analysis_data=response_payload
        )
        response_payload["saved_history_id"] = analysis_id

    return jsonify(response_payload)


# ============================================================================
# USER HISTORY & ACCOUNT ENDPOINTS
# ============================================================================
@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    """Returns saved analysis history for the logged-in user."""
    user_id = session.get("user_id")
    items = HistoryManager.get_user_analyses(user_id)
    return jsonify({"success": True, "authenticated": True, "items": items, "analyses": items})


@app.route("/api/history/<int:analysis_id>", methods=["GET", "DELETE"])
@login_required
def manage_history_item(analysis_id):
    """Retrieves or deletes a specific analysis record."""
    user_id = session.get("user_id")
    if request.method == "DELETE":
        deleted = HistoryManager.delete_analysis(analysis_id, user_id)
        return jsonify({"success": deleted})

    item = HistoryManager.get_analysis_by_id(analysis_id, user_id)
    if not item:
        return jsonify({"success": False, "message": "Record not found."}), 404
    return jsonify({"success": True, "item": item, "analysis": item})


@app.route("/api/settings", methods=["POST"])
@login_required
def update_settings():
    """Updates profile information for the authenticated user."""
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or request.form
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    new_password = data.get("new_password", "").strip()

    res = AuthManager.update_profile(user_id, name, email, new_password)
    if res["success"]:
        session["user_name"] = name
        session["user_email"] = email
    return jsonify(res)


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    """
    Conversational AI Career Chatbot endpoint.
    Accepts JSON:
        - message: str
        - history: list of {"role": "user"|"assistant", "content": "..."}
        - candidate: dict (name, matched_skills, missing_skills, etc.)
        - job_profile: dict
        - alignment: dict (score, fit_tier)
    Returns:
        JSON with {"success": True, "reply": "...", "engine": "...", "is_ai_live": bool}
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({
            "success": False,
            "error_type": "ValidationError",
            "message": "Please enter a question or message for the AI Career Advisor."
        }), 400

    history = data.get("history", [])
    candidate = data.get("candidate", {})
    job_profile = data.get("job_profile", {})
    alignment = data.get("alignment", {})

    try:
        chat_res = AIAdvisor.chat(
            message=message,
            history=history,
            candidate_data=candidate,
            job_data=job_profile,
            alignment_data=alignment,
            api_key=Config.GEMINI_API_KEY,
            model=Config.GEMINI_MODEL
        )
        return jsonify(chat_res)
    except Exception as e:
        logger.exception("Chatbot request processing failed")
        return jsonify({
            "success": False,
            "error_type": "ChatbotError",
            "message": f"Unable to generate response: {str(e)}"
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error_type": "FileSizeExceeded",
        "message": "File exceeds the 5 MB maximum upload limit. Please upload a smaller PDF resume."
    }), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error_type": "NotFound",
        "message": "The requested resource could not be found."
    }), 404


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
