"""
services/ai_advisor.py - Contextual, grounded AI career suggestions engine.
Integrates with Google Gemini API when configured, with an intelligent deterministic fallback.
"""
import os
import json
import logging
import requests
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class AIAdvisor:
    """Generates grounded recommendations tailored to resume and job description inputs."""

    @classmethod
    def generate_recommendations(
        cls,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        match_data: Dict[str, Any],
        api_key: str = "",
        model: str = "gemini-1.5-flash"
    ) -> Dict[str, Any]:
        """
        Generates actionable suggestions. Attempts Google Gemini API first if key exists,
        falling back to deep grounded deterministic advice if offline or unconfigured.
        """
        api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

        if api_key and api_key.strip() and not api_key.startswith("your_"):
            try:
                gemini_result = cls._call_gemini_api(resume_data, jd_data, match_data, api_key, model)
                if gemini_result:
                    return gemini_result
            except Exception as e:
                logger.warning(f"Gemini API request failed or timed out: {e}. Falling back to grounded analysis.")

        # Deterministic grounded recommendation engine
        return cls._generate_grounded_fallback(resume_data, jd_data, match_data)

    @classmethod
    def _call_gemini_api(
        cls,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        match_data: Dict[str, Any],
        api_key: str,
        model: str
    ) -> Dict[str, Any]:
        """Calls Google Gemini REST API with structured response instructions."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        candidate_name = resume_data.get("contact", {}).get("name", "Candidate")
        matched_tech = match_data.get("skills_analysis", {}).get("matched_technical", [])
        missing_tech = match_data.get("skills_analysis", {}).get("missing_technical", [])
        score = match_data.get("score", 0)
        sections = list(resume_data.get("sections", {}).keys())
        role_level = jd_data.get("role_level", "Standard")

        prompt = f"""
You are Parichay's Lead Technical Career Advisor. Analyze this real candidate resume against the provided job description.
DO NOT use generic advice, buzzwords, or marketing copy. Be grounded, specific, and technically rigorous.

Candidate Profile:
- Name: {candidate_name}
- Matched Technologies: {', '.join(matched_tech) if matched_tech else 'None explicitly matched'}
- Missing Technologies in JD: {', '.join(missing_tech) if missing_tech else 'None'}
- Current Alignment Score: {score}%
- Verified Resume Sections: {', '.join(sections)}
- Target Role Seniority: {role_level}

Job Description Context:
- Target Technical Requirements: {', '.join(jd_data.get('skills', {}).get('technical_skills', []))}
- Experience Target: {jd_data.get('experience_years', 'Not specified')}

Respond ONLY with a valid JSON object matching this schema:
{{
  "executive_summary": "2-3 sentences evaluating the candidate's alignment and primary gap for this role.",
  "bullet_enhancements": [
    {{
      "focus_area": "Technology or project to highlight",
      "critique": "Why the current representation may lack impact",
      "recommended_action": "Actionable rewrite following Google's X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z])."
    }}
  ],
  "gap_mitigation_plan": [
    {{
      "missing_skill": "Skill name",
      "concrete_action": "A specific project feature, micro-architecture, or lab to build to demonstrate this skill."
    }}
  ],
  "interview_preparation_topics": [
    "Specific technical or architectural questions the candidate will likely face based on these requirements"
  ]
}}
"""
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            data = response.json()
            text_response = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_json = json.loads(text_response)
            parsed_json["advisor_engine"] = f"Gemini AI ({model})"
            parsed_json["is_ai_live"] = True
            return parsed_json
        else:
            raise RuntimeError(f"Gemini API returned status {response.status_code}: {response.text}")

    @classmethod
    def _generate_grounded_fallback(
        cls,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        High-fidelity deterministic advice engine grounded directly in extracted entities.
        Ensures 100% functionality and high utility even without an external API key.
        """
        candidate_name = resume_data.get("contact", {}).get("name", "The candidate")
        matched_tech = match_data.get("skills_analysis", {}).get("matched_technical", [])
        missing_tech = match_data.get("skills_analysis", {}).get("missing_technical", [])
        unique_tech = match_data.get("skills_analysis", {}).get("candidate_unique", [])
        score = match_data.get("score", 0)
        sections = resume_data.get("sections", {})
        has_projects = "projects" in sections
        has_experience = "experience" in sections or "internships" in sections

        # 1. Executive Summary
        if score >= 75:
            summary = (
                f"{candidate_name} exhibits strong baseline alignment ({score}%) for this position, with direct coverage "
                f"across core competencies ({', '.join(matched_tech[:3]) if matched_tech else 'detected stack'}). "
                "The primary opportunity lies in explicitly quantifying engineering outcomes and addressing minor stack gaps."
            )
        elif score >= 50:
            summary = (
                f"{candidate_name} demonstrates meaningful overlap ({score}%) with several required proficiencies. "
                f"However, key requirements like {', '.join(missing_tech[:3]) if missing_tech else 'specialized tools'} "
                "are absent from the resume. Bridging these through project demonstrations will notably elevate alignment."
            )
        else:
            summary = (
                f"Currently, there is a divergence between the resume profile and the role requirements ({score}%). "
                f"The job requires hands-on depth in {', '.join(missing_tech[:4]) if missing_tech else 'specific frameworks'}. "
                "A targeted revision emphasizing transferable system concepts and relevant technical achievements is recommended."
            )

        # 2. Bullet Enhancements grounded in missing or matched technologies
        bullet_enhancements = []
        if matched_tech:
            top_matched = matched_tech[0]
            bullet_enhancements.append({
                "focus_area": f"Strengthen {top_matched} Project Impact",
                "critique": f"Descriptions involving {top_matched} often list tasks rather than measurable engineering throughput.",
                "recommended_action": f"Structure bullet points with metrics: 'Engineered a {top_matched} service that reduced API latency by 35% across 10K+ daily requests using connection pooling and async handlers.'"
            })

        if has_projects:
            bullet_enhancements.append({
                "focus_area": "Technical Architecture in Project Bullets",
                "critique": "Project bullet points often omit the underlying architecture, data flow, or deployment details.",
                "recommended_action": "Specify architectural choices: 'Designed a microservices architecture with decoupled background workers, integrating Redis caching to handle peak traffic without degradation.'"
            })
        else:
            bullet_enhancements.append({
                "focus_area": "Add a Dedicated Projects Section",
                "critique": "No dedicated Projects section was isolated by the parser. Independent projects are vital for evidencing practical skills.",
                "recommended_action": "Include 2-3 production-grade personal or academic projects with GitHub repositories and live deployment URLs."
            })

        # 3. Gap Mitigation Plan grounded in real missing technologies
        gap_mitigation = []
        for missing in missing_tech[:4]:
            if missing in ["Docker", "Kubernetes", "CI/CD"]:
                action = f"Containerize your existing projects using a multi-stage Dockerfile and set up a GitHub Actions CI/CD pipeline to prove production-readiness in {missing}."
            elif missing in ["AWS", "Google Cloud (GCP)", "Microsoft Azure"]:
                action = f"Deploy your application onto {missing} utilizing managed services (e.g., Cloud Run, EC2, or S3/CloudFront) and document the IAM and networking choices."
            elif missing in ["PostgreSQL", "MongoDB", "Redis", "MySQL"]:
                action = f"Implement indexing, query optimization, or caching strategies with {missing} in a sample service, benchmarking latency improvements under simulated load."
            elif missing in ["Machine Learning", "Deep Learning", "PyTorch", "TensorFlow"]:
                action = f"Build an end-to-end ML pipeline with {missing}, from exploratory data analysis and feature engineering to model evaluation and serving via a REST endpoint."
            elif missing in ["React", "Next.js", "Vue.js", "TypeScript"]:
                action = f"Refactor a frontend module into {missing} with strict typing, state management, and responsive accessible components."
            else:
                action = f"Incorporate {missing} into a focused proof-of-concept project or contribute a bug fix to an open-source repository utilizing it."

            gap_mitigation.append({
                "missing_skill": missing,
                "concrete_action": action
            })

        # 4. Realistic Interview Preparation Topics
        interview_topics = []
        if matched_tech:
            interview_topics.append(f"Deep dive on internals and concurrency models in {matched_tech[0]}.")
        if missing_tech:
            interview_topics.append(f"Conceptual trade-offs when choosing {missing_tech[0]} vs alternative industry standards.")
        interview_topics.append("System design: Designing scalable architectures, fault tolerance, and data consistency.")
        interview_topics.append("Behavioral STAR methodology: Communicating technical challenges and trade-offs made under tight deadlines.")

        return {
            "executive_summary": summary,
            "bullet_enhancements": bullet_enhancements,
            "gap_mitigation_plan": gap_mitigation,
            "interview_preparation_topics": interview_topics,
            "advisor_engine": "Parichay Grounded Advisor Engine",
            "is_ai_live": False
        }
