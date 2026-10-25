"""
services/extractor.py - Structured entity and section extraction from resumes and job descriptions.
Extracts contact info, segmented sections, categorized technical skills, and soft skills.
"""
import re
from typing import Dict, List, Set, Any, Optional

# Comprehensive categorized taxonomy of skills
SKILLS_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "languages": {
        "Python": ["python", "python3", "py"],
        "JavaScript": ["javascript", "js", "ecmascript"],
        "TypeScript": ["typescript", "ts"],
        "Java": ["java", "core java", "j2ee"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp", "c sharp"],
        "C": [r"\bc\b", "c language", "c programming"],
        "Go": ["golang", r"\bgo\b"],
        "Rust": ["rust"],
        "Ruby": ["ruby"],
        "PHP": ["php"],
        "Swift": ["swift"],
        "Kotlin": ["kotlin"],
        "Dart": ["dart"],
        "SQL": ["sql", "t-sql", "pl/sql"],
        "R": [r"\br\b", "r programming", "r-project"],
        "Scala": ["scala"],
        "HTML/CSS": ["html", "html5", "css", "css3"],
        "Bash/Shell": ["bash", "shell scripting", "powershell", "zsh"]
    },
    "frameworks_and_libraries": {
        "React": ["react", "react.js", "reactjs"],
        "Next.js": ["next.js", "nextjs"],
        "Node.js": ["node.js", "nodejs", "node"],
        "Express": ["express.js", "expressjs", "express"],
        "Flask": ["flask"],
        "Django": ["django"],
        "FastAPI": ["fastapi", "fast-api"],
        "Spring Boot": ["spring boot", "springboot", "spring framework"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Angular": ["angular", "angularjs"],
        "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],
        "Bootstrap": ["bootstrap"],
        "Redux": ["redux", "redux toolkit"],
        "GraphQL": ["graphql", "apollo"],
        "REST APIs": ["rest api", "restful", "rest apis", "rest web services", "restful api"]
    },
    "ai_ml_data": {
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning", "dl"],
        "PyTorch": ["pytorch", "torch"],
        "TensorFlow": ["tensorflow", "tf"],
        "Keras": ["keras"],
        "Scikit-Learn": ["scikit-learn", "sklearn"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Data Analysis": ["data analysis", "data analytics", "eda", "exploratory data analysis"],
        "Computer Vision": ["computer vision", "opencv", "cv", "image processing", "yolo"],
        "NLP": ["natural language processing", "nlp", "text mining", "spacy", "nltk"],
        "LLMs": ["llm", "llms", "large language models", "prompt engineering", "langchain", "rag", "retrieval augmented generation", "gemini", "gpt", "transformers", "hugging face"],
        "Data Visualization": ["data visualization", "matplotlib", "seaborn", "tableau", "power bi", "powerbi"],
        "Statistical Modeling": ["statistics", "statistical modeling", "hypothesis testing", "regression analysis"]
    },
    "cloud_and_devops": {
        "Docker": ["docker", "containerization", "containers"],
        "Kubernetes": ["kubernetes", "k8s"],
        "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "Google Cloud (GCP)": ["gcp", "google cloud", "google cloud platform", "bigquery"],
        "Microsoft Azure": ["azure", "microsoft azure"],
        "CI/CD": ["ci/cd", "ci-cd", "continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"],
        "Terraform": ["terraform", "iac", "infrastructure as code"],
        "Linux": ["linux", "ubuntu", "unix", "debian", "redhat"],
        "Microservices": ["microservices", "microservice architecture"]
    },
    "databases": {
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite"],
        "Firebase": ["firebase", "firestore"],
        "Supabase": ["supabase"],
        "Elasticsearch": ["elasticsearch"],
        "Vector Databases": ["vector database", "pinecone", "chromadb", "weaviate", "milvus", "qdrant"]
    },
    "tools_and_methods": {
        "Git": ["git", "github", "gitlab"],
        "Jira": ["jira"],
        "Agile/Scrum": ["agile", "scrum", "kanban", "sprint planning"],
        "Unit Testing": ["unit testing", "pytest", "jest", "test driven development", "tdd", "cypress", "selenium"],
        "System Design": ["system design", "software architecture", "scalability", "distributed systems"],
        "Postman": ["postman", "api testing"]
    },
    "soft_skills": {
        "Problem Solving": ["problem solving", "problem-solving", "analytical thinking"],
        "Communication": ["communication", "verbal communication", "written communication", "presentation skills"],
        "Team Collaboration": ["collaboration", "teamwork", "team player", "cross-functional collaboration"],
        "Leadership": ["leadership", "team leadership", "mentorship", "guiding junior engineers"],
        "Adaptability": ["adaptability", "fast learner", "quick learner", "resilience"],
        "Critical Thinking": ["critical thinking", "logical reasoning"],
        "Time Management": ["time management", "prioritization", "deadline-oriented"],
        "Attention to Detail": ["attention to detail", "meticulous", "quality-focused"]
    }
}


class ResumeExtractor:
    """Extracts structured entities, sections, and competencies from resume text."""

    SECTION_HEADERS = {
        "education": [
            r"education", r"academic background", r"academic qualification",
            r"academic history", r"educational background", r"degrees"
        ],
        "experience": [
            r"experience", r"work experience", r"professional experience",
            r"employment history", r"career history", r"work history"
        ],
        "internships": [
            r"internships", r"internship experience", r"industrial training",
            r"summer internship", r"trainee"
        ],
        "projects": [
            r"projects", r"personal projects", r"academic projects",
            r"key projects", r"selected projects", r"portfolio projects",
            r"software projects", r"notable projects"
        ],
        "skills": [
            r"skills", r"technical skills", r"technologies", r"technical competencies",
            r"core competencies", r"skills & expertise", r"tech stack", r"skills & tools"
        ],
        "certifications": [
            r"certifications", r"licenses & certifications", r"certificates",
            r"courses & certifications", r"professional certifications", r"credentials"
        ],
        "achievements": [
            r"achievements", r"awards", r"honors", r"accomplishments",
            r"publications", r"extracurricular activities", r"leadership"
        ]
    }

    @classmethod
    def extract_contact_info(cls, text: str) -> Dict[str, Any]:
        """Extracts email, phone, links, and candidate name heuristic."""
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        email = email_match.group(0) if email_match else None

        # Phone matching: support international and Indian formats (+91, 10 digits, parentheses, dashes)
        phone_match = re.search(r'(?:(?:\+|00)\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,5}[\s-]?\d{4,5}', text)
        phone = phone_match.group(0).strip() if phone_match else None
        # Discard invalid or too short numeric fragments
        if phone and len(re.sub(r'\D', '', phone)) < 10:
            phone = None

        # LinkedIn & GitHub
        linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|profile)/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
        linkedin = linkedin_match.group(0) if linkedin_match else None

        github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
        github = github_match.group(0) if github_match else None

        # Portfolio / website
        portfolio_match = re.search(r'(?:https?://)?([a-zA-Z0-9-]+\.(?:dev|io|me|portfolio|vercel\.app|netlify\.app))', text, re.IGNORECASE)
        portfolio = portfolio_match.group(0) if portfolio_match else None

        # Name heuristic: First non-empty line of resume usually contains the candidate's name
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        candidate_name = "Candidate"
        for line in lines[:5]:
            # If line is not an email, URL, phone, or section header, and has 2-4 words
            if "@" not in line and "http" not in line and not re.search(r'\d{5,}', line):
                clean_line = re.sub(r'[^a-zA-Z\s]', '', line).strip()
                words = clean_line.split()
                if 1 <= len(words) <= 4 and len(clean_line) < 35:
                    # Exclude common headers
                    lower_line = line.lower()
                    if not any(header in lower_line for headers in cls.SECTION_HEADERS.values() for header in headers):
                        candidate_name = clean_line.title()
                        break

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio
        }

    @classmethod
    def segment_sections(cls, text: str) -> Dict[str, str]:
        """
        Segments the resume text into distinct logical sections.
        """
        lines = text.split("\n")
        sections: Dict[str, List[str]] = {
            "header": [],
            "education": [],
            "experience": [],
            "internships": [],
            "projects": [],
            "skills": [],
            "certifications": [],
            "achievements": [],
            "other": []
        }

        current_section = "header"

        # Build a regex matching section headers when they appear as standalone or clear lines
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            clean_header = re.sub(r'[^a-zA-Z\s]', '', stripped).strip().lower()
            
            # Check if this line is a section header (usually short, <= 4 words)
            detected_section = None
            if len(clean_header.split()) <= 4:
                for sec_name, keywords in cls.SECTION_HEADERS.items():
                    if any(clean_header == kw or clean_header.startswith(kw + " ") or clean_header.endswith(" " + kw) for kw in keywords):
                        detected_section = sec_name
                        break

            if detected_section:
                current_section = detected_section
            else:
                sections[current_section].append(stripped)

        # Merge internships into experience if experience is empty or preserve internships
        joined_sections: Dict[str, str] = {
            k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()
        }
        
        return joined_sections

    @classmethod
    def extract_skills(cls, text: str) -> Dict[str, Any]:
        """
        Scans text against the comprehensive SKILLS_TAXONOMY.
        Returns:
            - all_skills: list of standardized skill names found
            - technical_skills: list of hard technical skills found
            - soft_skills: list of soft skills found
            - categorized: dict of category -> list of standardized skill names
            - total_count: int
        """
        text_lower = " " + text.lower() + " "
        
        categorized_results: Dict[str, List[str]] = {}
        all_skills: Set[str] = set()
        technical_skills: Set[str] = set()
        soft_skills: Set[str] = set()

        for category, skill_dict in SKILLS_TAXONOMY.items():
            category_found = []
            is_soft = (category == "soft_skills")

            for canonical_name, patterns in skill_dict.items():
                matched = False
                for pattern in patterns:
                    # Check regex or word boundary match
                    if pattern.startswith(r"\b") or pattern.endswith(r"\b"):
                        if re.search(pattern, text, re.IGNORECASE if canonical_name != "C" and canonical_name != "R" else 0):
                            matched = True
                            break
                    else:
                        # Standard word boundary matching
                        escaped = re.escape(pattern)
                        regex = rf'(?:^|[\s,;/|•\(\)\[\]]){escaped}(?:$|[\s,;/|•\(\)\[\]])'
                        if re.search(regex, text_lower):
                            matched = True
                            break

                if matched:
                    category_found.append(canonical_name)
                    all_skills.add(canonical_name)
                    if is_soft:
                        soft_skills.add(canonical_name)
                    else:
                        technical_skills.add(canonical_name)

            if category_found:
                categorized_results[category] = sorted(category_found)

        return {
            "all_skills": sorted(list(all_skills)),
            "technical_skills": sorted(list(technical_skills)),
            "soft_skills": sorted(list(soft_skills)),
            "categorized": categorized_results,
            "total_count": len(all_skills)
        }

    @classmethod
    def extract_experience_entries(cls, text: str) -> List[Dict[str, str]]:
        """Extracts rough experience or role blocks with dates/titles."""
        # Simple heuristic split on date ranges like '2022 - 2024', 'Jan 2023 - Present'
        date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*(?:-|–|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current)'
        
        lines = text.split("\n")
        entries = []
        current_entry = []

        for line in lines:
            if re.search(date_pattern, line, re.IGNORECASE) and current_entry:
                entries.append("\n".join(current_entry).strip())
                current_entry = [line]
            else:
                current_entry.append(line)

        if current_entry:
            entries.append("\n".join(current_entry).strip())

        return [{"content": e} for e in entries if len(e) > 15]

    @classmethod
    def extract_education_details(cls, text: str) -> List[str]:
        """Detects degrees, universities, and graduation years."""
        degrees = [
            r"B\.?Tech|Bachelor of Technology",
            r"B\.?E\.?|Bachelor of Engineering",
            r"B\.?S\.?|B\.?Sc\.?|Bachelor of Science",
            r"BCA|Bachelor of Computer Applications",
            r"M\.?Tech|Master of Technology",
            r"M\.?S\.?|M\.?Sc\.?|Master of Science",
            r"MCA|Master of Computer Applications",
            r"MBA|Master of Business Administration",
            r"Ph\.?D\.?|Doctor of Philosophy",
            r"Higher Secondary|12th Grade|High School"
        ]
        
        found = []
        for line in text.split("\n"):
            line_clean = line.strip()
            for deg_pattern in degrees:
                if re.search(deg_pattern, line_clean, re.IGNORECASE):
                    found.append(line_clean)
                    break
        return found


class JobDescriptionParser:
    """Extracts required competencies, education levels, and criteria from job descriptions."""

    @classmethod
    def parse_job_description(cls, jd_text: str) -> Dict[str, Any]:
        """
        Parses the job description to extract target skills, required experience level, and key demands.
        """
        clean_text = jd_text.strip()
        if not clean_text:
            return {
                "skills": {"all_skills": [], "technical_skills": [], "soft_skills": [], "categorized": {}},
                "experience_years": None,
                "role_level": "Unspecified",
                "required_education": []
            }

        skills_data = ResumeExtractor.extract_skills(clean_text)

        # Experience years heuristic: e.g. "3+ years", "2-5 years of experience"
        exp_match = re.search(r'(\d+)(?:\+|-(\d+))?\s*(?:years|yrs)\b(?:\s*of\s*experience)?', clean_text, re.IGNORECASE)
        exp_years = None
        if exp_match:
            min_years = exp_match.group(1)
            max_years = exp_match.group(2)
            exp_years = f"{min_years}-{max_years} years" if max_years else f"{min_years}+ years"

        # Role seniority heuristic
        role_level = "Mid Level"
        lower_jd = clean_text.lower()
        if any(term in lower_jd for term in ["intern", "internship", "graduate", "fresher", "entry level", "entry-level", "junior"]):
            role_level = "Entry Level / Fresher"
        elif any(term in lower_jd for term in ["senior", "sr.", "lead", "principal", "staff engineer", "architect", "manager"]):
            role_level = "Senior / Lead"

        # Education requirements
        education_reqs = []
        if re.search(r'\b(bachelor|b\.?tech|b\.?e|bs|b\.?sc)\b', lower_jd):
            education_reqs.append("Bachelor's Degree in Computer Science or related STEM field")
        if re.search(r'\b(master|m\.?tech|ms|m\.?sc|mca)\b', lower_jd):
            education_reqs.append("Master's Degree (Preferred/Required)")
        if re.search(r'\b(phd|doctorate)\b', lower_jd):
            education_reqs.append("Ph.D. / Research background")

        return {
            "skills": skills_data,
            "experience_years": exp_years,
            "role_level": role_level,
            "required_education": education_reqs,
            "word_count": len(clean_text.split())
        }
