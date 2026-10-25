"""
services/matcher.py - TF-IDF vectorization, cosine similarity, and explainable alignment scoring.
Calculates transparent alignment between resumes and job descriptions using scikit-learn.
"""
from typing import Dict, List, Any, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ResumeJobMatcher:
    """Computes explainable semantic similarity and skills overlap."""

    # Transparent weighting schema (sums to 100%)
    WEIGHT_CONTEXTUAL = 0.35      # TF-IDF Cosine Similarity of full content
    WEIGHT_TECH_SKILLS = 0.45     # Hard Technical Skills overlap ratio
    WEIGHT_SOFT_SKILLS = 0.10     # Soft Skills & Engineering Practices overlap
    WEIGHT_COMPLETENESS = 0.10    # Resume structural completeness & experience evidence

    @classmethod
    def match(
        cls,
        resume_text: str,
        jd_text: str,
        resume_skills: Dict[str, Any],
        jd_skills: Dict[str, Any],
        resume_sections: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Executes complete alignment evaluation between a candidate resume and job description.
        """
        # 1. TF-IDF Cosine Similarity & Vocabulary Coverage
        sim_data = cls._calculate_tfidf_similarity(resume_text, jd_text)
        cosine_sim = sim_data["calibrated_similarity"]
        raw_cosine = sim_data["raw_cosine"]
        vocab_coverage = sim_data["vocabulary_coverage"]

        # 2. Skill Gap Analysis
        resume_tech_set = set(resume_skills.get("technical_skills", []))
        jd_tech_set = set(jd_skills.get("technical_skills", []))

        resume_soft_set = set(resume_skills.get("soft_skills", []))
        jd_soft_set = set(jd_skills.get("soft_skills", []))

        matched_tech = sorted(list(resume_tech_set.intersection(jd_tech_set)))
        missing_tech = sorted(list(jd_tech_set.difference(resume_tech_set)))
        candidate_unique_tech = sorted(list(resume_tech_set.difference(jd_tech_set)))

        matched_soft = sorted(list(resume_soft_set.intersection(jd_soft_set)))
        missing_soft = sorted(list(jd_soft_set.difference(resume_soft_set)))

        # Skill Ratios
        if len(jd_tech_set) > 0:
            tech_match_ratio = len(matched_tech) / len(jd_tech_set)
        else:
            # If JD specified no explicit tech skills, fallback to contextual similarity
            tech_match_ratio = cosine_sim

        if len(jd_soft_set) > 0:
            soft_match_ratio = len(matched_soft) / len(jd_soft_set)
        else:
            soft_match_ratio = 0.7  # Neutral default if no soft skills mentioned in JD

        # 3. Structural & Content Completeness Evaluation
        completeness_score = cls._evaluate_completeness(resume_sections, resume_text)

        # 4. Composite Alignment Score Calculation
        # Adjusted dynamically if JD lacks hard skills
        if len(jd_tech_set) == 0:
            raw_score = (cosine_sim * 0.65) + (completeness_score * 0.25) + (soft_match_ratio * 0.10)
        else:
            raw_score = (
                (cosine_sim * cls.WEIGHT_CONTEXTUAL) +
                (tech_match_ratio * cls.WEIGHT_TECH_SKILLS) +
                (soft_match_ratio * cls.WEIGHT_SOFT_SKILLS) +
                (completeness_score * cls.WEIGHT_COMPLETENESS)
            )

        # Scale to 0 - 100 percentage
        alignment_percentage = int(round(min(1.0, max(0.0, raw_score)) * 100))

        # Categorize alignment band
        if alignment_percentage >= 80:
            fit_tier = "Strong Alignment"
            tier_badge = "high"
        elif alignment_percentage >= 60:
            fit_tier = "Moderate Alignment"
            tier_badge = "medium"
        elif alignment_percentage >= 40:
            fit_tier = "Partial Alignment"
            tier_badge = "partial"
        else:
            fit_tier = "Limited Alignment"
            tier_badge = "low"

        # 5. Identify unverified / potential skills
        # Keywords prominent in JD that have partial substring overlap or ambiguity
        unverified_skills = cls._identify_unverified_skills(jd_text, resume_text, missing_tech)

        # 6. Detailed Transparent Calculation Breakdown
        score_breakdown = {
            "overall_score": alignment_percentage,
            "fit_tier": fit_tier,
            "tier_badge": tier_badge,
            "raw_cosine": raw_cosine,
            "vocabulary_coverage_percent": int(round(vocab_coverage * 100)),
            "components": [
                {
                    "name": "Technical Skills Match",
                    "weight_percent": 45,
                    "achieved_percent": int(round(tech_match_ratio * 100)),
                    "contribution_points": round(tech_match_ratio * cls.WEIGHT_TECH_SKILLS * 100, 1),
                    "description": f"{len(matched_tech)} of {len(jd_tech_set)} target technical competencies matched." if len(jd_tech_set) > 0 else "Evaluated via semantic alignment (no explicit keywords detected in JD)."
                },
                {
                    "name": "Contextual & Semantic Similarity",
                    "weight_percent": 35,
                    "achieved_percent": int(round(cosine_sim * 100)),
                    "contribution_points": round(cosine_sim * cls.WEIGHT_CONTEXTUAL * 100, 1),
                    "description": f"TF-IDF cosine similarity ({raw_cosine}) with {int(round(vocab_coverage * 100))}% vocabulary coverage."
                },
                {
                    "name": "Soft Skills & Engineering Practices",
                    "weight_percent": 10,
                    "achieved_percent": int(round(soft_match_ratio * 100)),
                    "contribution_points": round(soft_match_ratio * cls.WEIGHT_SOFT_SKILLS * 100, 1),
                    "description": f"{len(matched_soft)} of {len(jd_soft_set)} organizational & process attributes matched." if len(jd_soft_set) > 0 else "Neutral baseline."
                },
                {
                    "name": "Resume Profile Completeness",
                    "weight_percent": 10,
                    "achieved_percent": int(round(completeness_score * 100)),
                    "contribution_points": round(completeness_score * cls.WEIGHT_COMPLETENESS * 100, 1),
                    "description": "Presence of verified sections: Experience, Education, Projects, and Certifications."
                }
            ],
            "formula_explanation": (
                "The match percentage represents an estimated alignment measure calculated as: "
                "(45% × Technical Skills Ratio) + (35% × TF-IDF Contextual Similarity) + "
                "(10% × Soft Skills Ratio) + (10% × Structural Completeness). "
                "This score indicates alignment with the posted requirements and is not a hiring guarantee or candidate ranking."
            )
        }

        # 7. Strengths & High Priority Improvement Areas
        strengths = []
        improvements = []

        if matched_tech:
            top_tech = ", ".join(matched_tech[:5])
            strengths.append(f"Strong verified coverage in key required technologies: {top_tech}.")
        if cosine_sim >= 0.5:
            strengths.append("High vocabulary and domain synergy between your resume experience and the role's responsibilities.")
        if len(candidate_unique_tech) >= 3:
            sample_unique = ", ".join(candidate_unique_tech[:4])
            strengths.append(f"Valuable additional technical proficiencies not strictly required: {sample_unique}.")
        if "projects" in resume_sections:
            strengths.append("Dedicated project portfolio evidence demonstrating practical engineering execution.")

        if missing_tech:
            critical_missing = missing_tech[:4]
            improvements.append({
                "area": "Critical Missing Technologies",
                "details": f"The job description explicitly emphasizes {', '.join(critical_missing)}. If you have academic, project, or open-source experience with these, make sure they are prominently listed.",
                "priority": "High"
            })
        if cosine_sim < 0.4:
            improvements.append({
                "area": "Keyword & Domain Alignment",
                "details": "The phrasing in your bullet points uses different terminology than the target role. Incorporate standard industry terminology and role-specific action verbs.",
                "priority": "Medium"
            })
        if "certifications" not in resume_sections:
            improvements.append({
                "area": "Credentials & Certifications",
                "details": "No certifications section was detected. Relevant vendor or cloud certifications (AWS, GCP, Coursera, Meta) can validate specialized skills.",
                "priority": "Low"
            })

        return {
            "score": alignment_percentage,
            "fit_tier": fit_tier,
            "tier_badge": tier_badge,
            "cosine_similarity": round(float(cosine_sim), 4),
            "score_breakdown": score_breakdown,
            "skills_analysis": {
                "matched_technical": matched_tech,
                "missing_technical": missing_tech,
                "candidate_unique": candidate_unique_tech,
                "matched_soft": matched_soft,
                "missing_soft": missing_soft,
                "unverified_skills": unverified_skills,
                "counts": {
                    "matched_tech_count": len(matched_tech),
                    "missing_tech_count": len(missing_tech),
                    "total_jd_tech": len(jd_tech_set),
                    "candidate_total_tech": len(resume_tech_set)
                }
            },
            "strengths": strengths,
            "improvement_priorities": improvements
        }

    @classmethod
    def _calculate_tfidf_similarity(cls, text1: str, text2: str) -> Dict[str, float]:
        """
        Computes TF-IDF Cosine Similarity and calibrated vocabulary coverage.
        text1: Resume text
        text2: Job Description text
        """
        if not text1.strip() or not text2.strip():
            return {"raw_cosine": 0.0, "calibrated_similarity": 0.0, "vocabulary_coverage": 0.0}

        try:
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                max_features=2500,
                sublinear_tf=True
            )
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            raw_cosine = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            raw_cosine = float(np.nan_to_num(raw_cosine, nan=0.0))

            # Calculate vocabulary coverage: proportion of JD's TF-IDF features found in resume
            v_resume = tfidf_matrix[0].toarray()[0]
            v_jd = tfidf_matrix[1].toarray()[0]
            total_jd_weight = float(np.sum(v_jd))
            if total_jd_weight > 0:
                matched_jd_weight = float(np.sum(v_jd[v_resume > 0]))
                vocab_coverage = matched_jd_weight / total_jd_weight
            else:
                vocab_coverage = raw_cosine

            # Calibrate contextual similarity:
            # In pairwise text matching with unequal lengths, raw cosine rarely exceeds 0.35.
            # We scale raw cosine (factor 2.5) and combine with vocabulary coverage (scaled relative to 0.45).
            norm_cosine = min(1.0, raw_cosine * 2.5)
            norm_coverage = min(1.0, vocab_coverage / 0.45)
            calibrated_sim = min(1.0, (0.5 * norm_cosine) + (0.5 * norm_coverage))

            return {
                "raw_cosine": round(raw_cosine, 4),
                "calibrated_similarity": round(calibrated_sim, 4),
                "vocabulary_coverage": round(vocab_coverage, 4)
            }
        except Exception:
            return {"raw_cosine": 0.0, "calibrated_similarity": 0.0, "vocabulary_coverage": 0.0}


    @staticmethod
    def _evaluate_completeness(sections: Dict[str, str], full_text: str) -> float:
        """
        Scores resume structural health based on section presence and depth.
        """
        score = 0.2  # baseline
        
        if "education" in sections:
            score += 0.25
        if "experience" in sections or "internships" in sections:
            score += 0.30
        if "projects" in sections:
            score += 0.15
        if "skills" in sections:
            score += 0.10

        # Word count bonus (ideal resume is 250 - 900 words)
        word_count = len(full_text.split())
        if 200 <= word_count <= 1200:
            score += 0.0
        elif word_count < 150:
            score = max(0.2, score - 0.2)

        return min(1.0, score)

    @staticmethod
    def _identify_unverified_skills(jd_text: str, resume_text: str, missing_tech: List[str]) -> List[str]:
        """
        Identifies skills that appear conceptually or partially in resume text
        without full explicit confirmation in the candidate's core skills section.
        """
        unverified = []
        resume_lower = resume_text.lower()
        
        for skill in missing_tech:
            # Check if skill name root or abbreviation appears anywhere in text
            skill_tokens = [tok for tok in skill.lower().split() if len(tok) > 2]
            if skill_tokens and any(tok in resume_lower for tok in skill_tokens):
                unverified.append(f"{skill} (Mentioned contextually, but not structured as a primary skill)")

        return unverified[:5]
