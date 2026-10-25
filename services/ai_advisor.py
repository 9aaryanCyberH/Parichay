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
      "recommended_action": "Actionable rewrite following Google's X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z]).",
      "original": "Example of generic before bullet",
      "enhanced": "Google X-Y-Z enhanced rewrite",
      "rationale": "Why this enhancement works"
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
            action_text = f"Engineered a {top_matched} service that reduced API latency by 35% across 10K+ daily requests using connection pooling and async handlers."
            bullet_enhancements.append({
                "focus_area": f"Strengthen {top_matched} Project Impact",
                "critique": f"Descriptions involving {top_matched} often list tasks rather than measurable engineering throughput.",
                "recommended_action": f"Structure bullet points with metrics: '{action_text}'",
                "original": f"Worked on {top_matched} backend features and handled database queries.",
                "enhanced": action_text,
                "rationale": "Google's X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z]) demonstrates quantifiable engineering impact and ownership."
            })

        if has_projects:
            arch_action = "Designed a microservices architecture with decoupled background workers, integrating Redis caching to handle peak traffic without degradation."
            bullet_enhancements.append({
                "focus_area": "Technical Architecture in Project Bullets",
                "critique": "Project bullet points often omit the underlying architecture, data flow, or deployment details.",
                "recommended_action": f"Specify architectural choices: '{arch_action}'",
                "original": "Built a full stack project with web interface and backend API.",
                "enhanced": arch_action,
                "rationale": "Articulating architectural constraints and database choices signals senior engineering judgment."
            })
        else:
            bullet_enhancements.append({
                "focus_area": "Add a Dedicated Projects Section",
                "critique": "No dedicated Projects section was isolated by the parser. Independent projects are vital for evidencing practical skills.",
                "recommended_action": "Include 2-3 production-grade personal or academic projects with GitHub repositories and live deployment URLs.",
                "original": "Skills listed without repository links or live deployments.",
                "enhanced": "Architected and published 2 open-source services with CI/CD automation, Dockerfiles, and comprehensive test suites.",
                "rationale": "Verified public repositories provide direct proof of technical execution."
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

    @classmethod
    def chat(
        cls,
        message: str,
        history: List[Dict[str, str]] = None,
        candidate_data: Dict[str, Any] = None,
        skills_data: Dict[str, Any] = None,
        job_data: Dict[str, Any] = None,
        alignment_data: Dict[str, Any] = None,
        api_key: str = "",
        model: str = "gemini-1.5-flash"
    ) -> Dict[str, Any]:
        """
        Interactive career chatbot endpoint.
        Understands candidate resume context, target role description, and alignment metrics.
        """
        history = history or []
        candidate_data = dict(candidate_data or {})
        skills_data = skills_data or {}
        job_data = job_data or {}
        alignment_data = alignment_data or {}

        # Merge skills_data into candidate_data if missing
        if not candidate_data.get("matched_skills") and skills_data.get("matched_technical"):
            candidate_data["matched_skills"] = skills_data.get("matched_technical", [])
        if not candidate_data.get("missing_skills") and skills_data.get("missing_technical"):
            candidate_data["missing_skills"] = skills_data.get("missing_technical", [])
        if not candidate_data.get("unique_skills") and skills_data.get("candidate_unique"):
            candidate_data["unique_skills"] = skills_data.get("candidate_unique", [])

        api_key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()

        # Try Google Gemini if key is provided and valid
        if api_key and not api_key.startswith("your_"):
            try:
                gemini_reply, active_model = cls._call_gemini_chat(
                    message=message,
                    history=history,
                    candidate_data=candidate_data,
                    job_data=job_data,
                    alignment_data=alignment_data,
                    api_key=api_key,
                    model=model
                )
                if gemini_reply:
                    return {
                        "success": True,
                        "reply": gemini_reply,
                        "engine": f"Google Gemini ({active_model})",
                        "is_ai_live": True
                    }
            except Exception as e:
                logger.warning(f"Gemini chat request failed: {e}. Falling back to grounded conversational intelligence.")

        # Grounded conversational fallback
        fallback_reply = cls._generate_grounded_chat_fallback(message, history, candidate_data, job_data, alignment_data)
        return {
            "success": True,
            "reply": fallback_reply,
            "engine": "Parichay Grounded AI Copilot",
            "is_ai_live": False
        }

    @classmethod
    def _call_gemini_chat(
        cls,
        message: str,
        history: List[Dict[str, str]],
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        alignment_data: Dict[str, Any],
        api_key: str,
        model: str
    ) -> tuple:
        """
        Invokes Gemini REST API with sanitized multiturn conversation history,
        rich resume context, and multi-model failover support.
        Returns (reply_text: str, active_model: str).
        """
        candidate_name = candidate_data.get("name", "Candidate")
        matched_tech = candidate_data.get("matched_skills", [])
        missing_tech = candidate_data.get("missing_skills", [])
        unique_tech = candidate_data.get("unique_skills", [])
        score = alignment_data.get("score", 0)
        fit_tier = alignment_data.get("fit_tier", "Evaluation Complete")
        role_level = job_data.get("role_level", "Standard")
        exp_years = job_data.get("experience_years", "Not specified")

        system_instruction = f"""You are Parichay's Lead Technical Career Advisor and AI Career Copilot.
You are assisting {candidate_name} with their resume, career development, and job application.
You are grounded in this exact candidate session data:
- Candidate Name: {candidate_name}
- Overall Role Match Score: {score}% ({fit_tier})
- Target Role Seniority: {role_level} (Experience Target: {exp_years})
- Verified Matched Skills: {', '.join(matched_tech) if matched_tech else 'None currently verified'}
- Identified Missing Skills in Target Role: {', '.join(missing_tech) if missing_tech else 'None identified'}
- Candidate Unique Bonus Skills: {', '.join(unique_tech) if unique_tech else 'None'}

Core Persona & Rules:
1. Speak as an encouraging, pragmatic, senior engineering career advisor and hiring strategist.
2. Be technically rigorous and specific. Address the candidate's exact technologies (e.g. {', '.join(matched_tech[:3]) if matched_tech else 'their stack'}).
3. When suggesting resume bullet points, ALWAYS format them using Google's X-Y-Z formula: "Accomplished [X] as measured by [Y], by doing [Z]".
4. When asked about skills to learn or gaps, suggest concrete micro-projects, architectural patterns, and production implementations.
5. When asked about interview questions, provide realistic technical and architectural questions specific to the matched and missing technologies.
6. Use clean GitHub Markdown: bold key terms, use bullet points, and provide concise code or configuration snippets when relevant.
7. Answer any career, technical, interview, resume, or salary negotiation question thoroughly.
"""

        # 1. Clean and normalize conversation history
        # Exclude the current message if the frontend pushed it to the end of history
        hist = list(history) if history else []
        if hist and hist[-1].get("role") in ("user", "human") and hist[-1].get("content", "").strip() == message.strip():
            hist = hist[:-1]

        raw_turns = []
        for turn in hist:
            role = "user" if turn.get("role") in ("user", "human") else "model"
            content = (turn.get("content") or "").strip()
            if not content:
                continue
            # Merge consecutive turns of the same role to satisfy Gemini's strict alternating turn requirement
            if raw_turns and raw_turns[-1]["role"] == role:
                raw_turns[-1]["text"] += f"\n\n{content}"
            else:
                raw_turns.append({"role": role, "text": content})

        # Gemini requires contents to start with 'user'. Drop leading 'model' turns
        while raw_turns and raw_turns[0]["role"] != "user":
            raw_turns.pop(0)

        # Keep last 8 turns to stay within token budget
        raw_turns = raw_turns[-8:]

        contents = []
        for item in raw_turns:
            contents.append({
                "role": item["role"],
                "parts": [{"text": item["text"]}]
            })

        # Append current user prompt
        user_turn_content = message.strip()
        # If no prior turns, prepend quick session grounding to user prompt
        if not contents:
            user_turn_content = f"[Session: Candidate={candidate_name}, Match={score}%, Matched={matched_tech[:6]}, Missing={missing_tech[:6]}]\n\n{user_turn_content}"

        contents.append({
            "role": "user",
            "parts": [{"text": user_turn_content}]
        })

        # 2. Ordered list of models to try
        models_to_try = []
        preferred_models = [model, "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-2.5-flash"]
        for m in preferred_models:
            if m and m not in models_to_try:
                models_to_try.append(m)

        headers = {"Content-Type": "application/json"}

        for target_model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={api_key}"
            
            payload = {
                "contents": contents,
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                },
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 1000
                }
            }

            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=12)
                if resp.status_code == 200:
                    res_json = resp.json()
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "").strip()
                            if text:
                                return text, target_model

                # If systemInstruction caused a 400, retry with inlined system instruction
                if resp.status_code == 400 and "systemInstruction" in resp.text:
                    inline_contents = list(contents)
                    if inline_contents:
                        first_text = inline_contents[0]["parts"][0]["text"]
                        inline_contents[0]["parts"][0]["text"] = f"{system_instruction}\n\n---\n\n{first_text}"
                        retry_payload = {
                            "contents": inline_contents,
                            "generationConfig": {
                                "temperature": 0.4,
                                "maxOutputTokens": 1000
                            }
                        }
                        retry_resp = requests.post(url, headers=headers, json=retry_payload, timeout=12)
                        if retry_resp.status_code == 200:
                            candidates = retry_resp.json().get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                if parts:
                                    text = parts[0].get("text", "").strip()
                                    if text:
                                        return text, target_model

                logger.warning(f"Gemini API model {target_model} returned HTTP {resp.status_code}: {resp.text[:300]}")
            except Exception as ex:
                logger.warning(f"Gemini API call to model {target_model} raised exception: {ex}")

        return "", ""

    @classmethod
    def _generate_grounded_chat_fallback(
        cls,
        message: str,
        history: List[Dict[str, str]],
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        alignment_data: Dict[str, Any]
    ) -> str:
        """
        Deep grounded deterministic response generator that answers questions
        based on the candidate's exact parsed skills, gaps, score, and job requirements.
        """
        msg_lower = message.lower()
        candidate_name = candidate_data.get("name", "Candidate")
        matched_tech = candidate_data.get("matched_skills", [])
        missing_tech = candidate_data.get("missing_skills", [])
        unique_tech = candidate_data.get("unique_skills", [])
        score = alignment_data.get("score", 0)
        fit_tier = alignment_data.get("fit_tier", "Evaluation Complete")

        # 1. Gaps / Three most important gaps inquiry
        if any(w in msg_lower for w in ["gap", "gaps", "three most important", "missing"]):
            if missing_tech:
                top_gaps = missing_tech[:3]
                gap_items = "\n".join([f"{i+1}. **{g}** — Demonstrating hands-on project implementations with {g} will directly close this requirement." for i, g in enumerate(top_gaps)])
                return (
                    f"### Priority Skill Gaps for **{candidate_name}**\n\n"
                    f"Based on your target job description, here are the top competencies required that were not verified in your resume:\n\n"
                    f"{gap_items}\n\n"
                    f"**Next Steps:**\n"
                    f"- Add these keywords to your projects or coursework if you have prior exposure.\n"
                    f"- Review the tailored learning roadmap in the **Gap Mitigation** tab for step-by-step project architectures."
                )
            elif score < 75:
                return (
                    f"### Skill Gap Analysis for **{candidate_name}** (Alignment Score: **{score}%**)\n\n"
                    f"While your resume matches core technical keywords, your alignment score (**{score}%**) indicates opportunities in **depth, system design, and architectural evidence**:\n\n"
                    f"1. **Production Infrastructure & CI/CD:** Add evidence of containerization (Docker), deployment automation, and cloud hosting (AWS/GCP).\n"
                    f"2. **Quantified Engineering Impact:** The target role expects demonstrable throughput metrics (e.g. latency reduction, request scale, uptime) rather than generic task lists.\n"
                    f"3. **Testing & Code Quality:** Explicitly cite test frameworks (e.g. PyTest, Jest, JUnit) and CI pipeline testing.\n\n"
                    f"**Recommended Action:** Use Google's X-Y-Z formula to rewrite your experience bullets to showcase end-to-end engineering ownership."
                )
            else:
                return (
                    f"### Skill Gap Analysis for **{candidate_name}**\n\n"
                    f"Strong alignment detected (**{score}%**)! You cover all primary technical requirements.\n\n"
                    f"To make your profile stand out against other qualified candidates:\n"
                    f"1. **Quantifying Engineering Outcomes:** Use Google's X-Y-Z formula on your project bullets.\n"
                    f"2. **Highlighting Unique Strengths:** Emphasize bonus skills like {', '.join(unique_tech[:3]) if unique_tech else 'system design & cloud architecture'}."
                )

        # 2. Priority Skills to Learn inquiry
        if any(w in msg_lower for w in ["prioritize learning", "skills to learn", "which skills", "what should i learn", "priority skills"]):
            if missing_tech:
                skill_list = "\n".join([f"{i+1}. **{s}** (Target Requirement): Build a targeted project feature or microservice using {s} and commit it to GitHub with a clean README." for i, s in enumerate(missing_tech[:3])])
                return (
                    f"### High-Priority Skills Roadmap for **{candidate_name}**\n\n"
                    f"To maximize your hiring probability for this role, prioritize learning in this exact sequence:\n\n"
                    f"{skill_list}\n\n"
                    f"**Suggested Strategy:** Rather than spending months on theoretical courses, build one cohesive full-stack application that integrates these missing competencies with your existing strengths ({', '.join(matched_tech[:2]) if matched_tech else 'core stack'})."
                )
            else:
                return (
                    f"### High-Priority Skills Roadmap for **{candidate_name}**\n\n"
                    f"Your core technical coverage matches the primary job requirements! To maximize your competitive advantage over other applicants, prioritize learning:\n\n"
                    f"1. **Cloud & DevOps (Docker, Kubernetes, AWS/GCP):** Demonstrating containerized production deployments sets you apart from entry/mid candidates.\n"
                    f"2. **System Design & High Concurrency (Redis, Kafka, PostgreSQL):** Emphasize caching layers, asynchronous task queues, and DB indexing.\n"
                    f"3. **Automated Testing & CI/CD (GitHub Actions, PyTest):** Highlighting automated test suites proves production-ready engineering hygiene."
                )

        # 3. Score Calculation inquiry
        if any(w in msg_lower for w in ["calculate", "calculated", "formula", "how was my score", "score calculation"]):
            return (
                f"### Alignment Score Methodology (**{score}%** • {fit_tier})\n\n"
                f"Your Parichay alignment score is calculated through a hybrid deterministic and semantic pipeline:\n\n"
                f"1. **TF-IDF Vector Cosine Similarity (30% weight):** Measures vocabulary and conceptual overlap between your resume text and the job description.\n"
                f"2. **Core Technical Skills Match (45% weight):** Ratio of verified required technical competencies present in your resume against the target role requirements.\n"
                f"3. **Experience & Seniority Alignment (15% weight):** Assesses verified work history against the role's target seniority level.\n"
                f"4. **Soft Skills & Architectural Context (10% weight):** Evaluates teamwork, leadership, testing, and deployment competencies.\n\n"
                f"Closing the missing skills in your Skills Matrix will provide the largest direct increase to your score."
            )

        # 4. Project description improvement
        if any(w in msg_lower for w in ["improve project", "project description", "project bullet", "help me improve"]):
            sample_skill = matched_tech[0] if matched_tech else "Python"
            return (
                f"### How to Elevate Your Project Descriptions\n\n"
                f"Transform task-based bullets into high-impact engineering accomplishments using **Google's X-Y-Z Formula** (*Accomplished [X] as measured by [Y], by doing [Z]*):\n\n"
                f"**Before (Task-focused):**\n"
                f"> *\"Built a web application using {sample_skill} and handled database operations.\"*\n\n"
                f"**After (X-Y-Z Formula):**\n"
                f"> *\"Architected an asynchronous {sample_skill} service that reduced query latency by **38%** across 15,000 daily requests by implementing connection pooling and Redis caching.\"*\n\n"
                f"**3 Quick Checks for Every Project Bullet:**\n"
                f"- [ ] Did you include a metric (%, time saved, users served)?\n"
                f"- [ ] Did you specify the core technologies and architectural patterns?\n"
                f"- [ ] Did you link to a public GitHub repository or live deployment?"
            )

        # 5. Check for specific skill inquiry
        for skill in missing_tech + matched_tech:
            if skill.lower() in msg_lower:
                if skill in missing_tech:
                    return (
                        f"### Action Plan for **{skill}** (High-Priority Missing Requirement)\n\n"
                        f"Because **{skill}** is explicitly required by this job description, adding proof of competence will directly elevate your alignment score.\n\n"
                        f"**1. Recommended Hands-On Project:**\n"
                        f"- Build a standalone micro-project or refactor an existing repository to incorporate **{skill}**.\n"
                        f"- Commit the code to GitHub with a clean `README.md` and architecture diagram.\n\n"
                        f"**2. Resume Bullet Point Template (Google X-Y-Z):**\n"
                        f"- *\"Integrated **{skill}** into the deployment pipeline, accelerating delivery cycle by **28%** and reducing deployment errors by doing automated container validation.\"*\n\n"
                        f"**3. Interview Question You Will Face:**\n"
                        f"- *\"Why did you choose {skill} over alternatives in your project, and what trade-offs did you encounter in production?\"*"
                    )
                else:
                    return (
                        f"### Maximizing Your Verified Skill: **{skill}**\n\n"
                        f"Great news: **{skill}** is already verified in your resume and matches the target job description requirements!\n\n"
                        f"To make your experience stand out against other candidates with {skill}:\n"
                        f"- **Quantify Throughput:** Don't just mention you used {skill}; specify request volumes, data sizes, or latency benchmarks.\n"
                        f"- **Highlight Architecture:** Mention whether you used {skill} in a monolithic, microservices, or serverless design pattern.\n"
                        f"- **Example Bullet Rewrite:** *\"Architected a high-concurrency service in **{skill}**, maintaining **99.9% uptime** across 50K+ daily active users by implementing asynchronous processing and connection pooling.\"*"
                    )

        # 6. X-Y-Z Formula / Bullet Point Rewriting
        if any(w in msg_lower for w in ["bullet", "rewrite", "x-y-z", "xyz", "rephrase", "experience"]):
            tech_sample = matched_tech[0] if matched_tech else "Python"
            return (
                f"### Google's X-Y-Z Formula for **{candidate_name}**\n\n"
                f"Top tech recruiters look for: **\"Accomplished [X] as measured by [Y], by doing [Z]\"**.\n\n"
                f"Here are 3 tailored bullet rewrites for your target role:\n\n"
                f"1. **Core Engineering:**\n"
                f"   * *\"Engineered a scalable data pipeline using **{tech_sample}**, reducing batch execution time by **42%** by parallelizing I/O bottlenecks and indexing query filters.\"*\n\n"
                f"2. **Reliability & Testing:**\n"
                f"   * *\"Increased test coverage from 55% to **92%**, eliminating production regression incidents over 6 release cycles by writing comprehensive integration tests.\"*\n\n"
                f"3. **Bridging Gaps:**\n"
                f"   * *\"Designed and deployed containerized services using **{missing_tech[0] if missing_tech else 'Docker'}**, slashing environment onboarding time for new developers from 2 days to **under 15 minutes**.\"*\n\n"
                f"💡 *Tip: Click 'Copy Bullet' on any recommendation in the AI Recommendations tab to quickly use them.*"
            )

        # 7. Technical Interview Prep
        if any(w in msg_lower for w in ["interview", "questions", "prep", "ask", "technical round", "practice"]):
            return (
                f"### High-Probability Technical Interview Questions\n\n"
                f"Based on your current alignment (**{score}%**) and the target role criteria, technical interviewers will likely focus on:\n\n"
                f"1. **Deep Dive on Matched Stack ({', '.join(matched_tech[:2]) if matched_tech else 'Core Languages'}):**\n"
                f"   * *\"Explain how memory management and concurrency work under the hood in your primary language.\"*\n\n"
                f"2. **Mitigating Gap Awareness ({', '.join(missing_tech[:2]) if missing_tech else 'System Tools'}):**\n"
                f"   * *\"The role relies heavily on {missing_tech[0] if missing_tech else 'distributed systems'}. How would you design a fault-tolerant service using it?\"*\n\n"
                f"3. **System Architecture Scenario:**\n"
                f"   * *\"Walk me through how you would diagnose and debug a 500ms latency spike occurring intermittently in an API service under high traffic.\"*\n\n"
                f"4. **Behavioral STAR Question:**\n"
                f"   * *\"Tell me about a time you had to deliver a feature with incomplete specifications or unfamiliar tooling. How did you navigate the trade-offs?\"*"
            )

        # 8. Alignment Score / How to improve / Boost
        if any(w in msg_lower for w in ["score", "improve", "increase", "boost", "match", "align"]):
            missing_str = ", ".join(f"**{m}**" for m in missing_tech[:3]) if missing_tech else "specialized tooling"
            return (
                f"### Strategy to Elevate Your Alignment Score (Currently **{score}%** • {fit_tier})\n\n"
                f"To transition your profile into the top candidate tier, follow this 3-step action roadmap:\n\n"
                f"1. **Incorporate Missing Technical Keywords:**\n"
                f"   * Target JD requires: {missing_str}.\n"
                f"   * If you have used these in academic coursework, side projects, or internships, ensure they appear explicitly in your skills list and project descriptions.\n\n"
                f"2. **Strengthen Contextual Keyword Density:**\n"
                f"   * Mirror the terminology used in the job description (e.g. *\"CI/CD pipelines\"*, *\"RESTful API design\"*, *\"microservices\"*).\n\n"
                f"3. **Add Measurable Impact to Bullets:**\n"
                f"   * Every project should list at least one quantitative metric (% speedup, users served, data processed, test coverage).\n\n"
                f"Would you like me to rewrite a specific project bullet point for you?"
            )

        # 9. Competitive Advantage
        if any(w in msg_lower for w in ["advantage", "strength", "stand out", "edge"]):
            return (
                f"### Your Competitive Edge for this Target Role\n\n"
                f"Here is what positions **{candidate_name}** strongly for this position:\n\n"
                f"- **Verified Technical Foundation:** You have verified competency in {', '.join(matched_tech[:4]) if matched_tech else 'key software engineering skills'}.\n"
                f"- **Structural Profile Integrity:** Your resume demonstrates clear section segmentation and solid engineering fundamentals.\n"
                f"- **Next Step:** By addressing the {len(missing_tech)} missing competencies highlighted in your Skills Matrix, you will have a comprehensive application that passes both automated ATS screens and engineering manager evaluations."
            )

        # 10. General / Greeting / Fallback
        matched_str = ', '.join(matched_tech[:3]) if matched_tech else ('Verified from Resume' if score >= 60 else 'Under Evaluation')
        gaps_str = ', '.join(missing_tech[:3]) if missing_tech else ('Infrastructure & Quantified Impact' if score < 75 else 'None identified')
        return (
            f"Hello **{candidate_name}**! I am your **Parichay AI Career Intelligence Copilot**.\n\n"
            f"I have reviewed your resume against the target role:\n"
            f"- **Alignment Score:** **{score}%** ({fit_tier})\n"
            f"- **Matched Core Technologies:** {matched_str}\n"
            f"- **Priority Skill Gaps:** {gaps_str}\n\n"
            f"**Here are a few things you can ask me:**\n"
            f"1. *\"What are the three most important gaps in my resume?\"*\n"
            f"2. *\"Which skills should I prioritize learning?\"*\n"
            f"3. *\"Explain how my alignment score was calculated.\"*\n"
            f"4. *\"Rewrite my experience bullet points using Google's X-Y-Z formula.\"*\n"
            f"5. *\"What technical interview questions will they ask me for this role?\"*"
        )

