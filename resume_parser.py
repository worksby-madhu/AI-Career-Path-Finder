"""Resume text extraction and skill identification for the web and CLI workflows.

Uploaded files are parsed in memory; this module does not save resumes to disk.
"""
from __future__ import annotations

from io import BytesIO
import re
from pathlib import Path

from docx import Document
from pypdf import PdfReader

# Keep this list focused on technical skills relevant to the current matcher.
# The matching engine normalizes the detected labels before scoring careers.
SKILL_TERMS = {
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "html", "css",
    "react", "node.js", "django", "flask", "fastapi", "sql", "nosql", "mysql",
    "postgresql", "sqlite", "mongodb", "redis", "pandas", "numpy", "matplotlib",
    "seaborn", "scikit-learn", "machine learning", "deep learning", "artificial intelligence",
    "generative ai", "natural language processing", "nlp", "computer vision", "opencv",
    "yolo", "tensorflow", "keras", "pytorch", "hugging face", "power bi", "tableau",
    "excel", "statistics", "data analysis", "data visualization", "data cleaning",
    "data structures and algorithms", "object-oriented programming", "oop", "git", "github",
    "docker", "kubernetes", "aws", "azure", "google cloud", "rest api", "rest apis",
    "api development", "debugging", "unit testing", "software testing", "selenium",
    "linux", "bash", "computer networks", "dbms", "database management", "agile",
    "scrum", "problem solving", "communication", "fastapi", "bootstrap", "jquery",
    "express.js", "express", "next.js", "angular", "vue.js", "php", "c++", "r programming",
    "data preprocessing", "feature engineering", "model evaluation", "model deployment",
    "linear algebra", "data mining", "etl", "spark", "hadoop", "airflow", "snowflake",
    "jira", "figma", "responsive design", "restful services", "machine vision"
}

# Common aliases in resumes mapped to the preferred labels used in the project.
ALIASES = {
    "js": "javascript",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "powerbi": "power bi",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "nodejs": "node.js",
    "reactjs": "react",
    "postgres": "postgresql",
    "restful api": "rest api",
    "restful apis": "rest apis",
    "object oriented programming": "object-oriented programming",
}


def get_user_profile():
    """Keep the original command-line profile collection workflow available."""
    print("\n========== USER INFORMATION ==========")
    name = input("Enter your name: ")
    education = input("Enter your education: ")
    experience = input("Enter your experience: ")
    skills = input("Enter your skills (comma separated): ")
    interests = input("Enter your interests (comma separated): ")
    skills = [skill.strip().lower() for skill in skills.split(",") if skill.strip()]
    interests = [interest.strip().lower() for interest in interests.split(",") if interest.strip()]
    return {"name": name, "education": education, "experience": experience,
            "skills": skills, "interests": interests}


def extract_text_from_resume(uploaded_file, extension=None):
    """Extract selectable text from a PDF or DOCX uploaded file-like object."""
    filename = getattr(uploaded_file, "name", "resume")
    extension = (extension or Path(filename).suffix).lower()
    raw = uploaded_file.read()
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    if not raw:
        raise ValueError("The uploaded file is empty.")

    try:
        if extension == ".pdf":
            reader = PdfReader(BytesIO(raw))
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as exc:
                    raise ValueError("This PDF is password-protected. Upload an unlocked PDF.") from exc
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif extension == ".docx":
            document = Document(BytesIO(raw))
            chunks = [paragraph.text for paragraph in document.paragraphs]
            for table in document.tables:
                for row in table.rows:
                    chunks.append(" ".join(cell.text for cell in row.cells))
            text = "\n".join(chunks)
        else:
            raise ValueError("Unsupported file type. Upload a PDF or DOCX resume.")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The resume could not be read. Please upload a valid PDF or DOCX file.") from exc

    text = re.sub(r"[ \t]+", " ", text).strip()
    if not text:
        raise ValueError(
            "No readable text was found. If this is a scanned PDF, use a text-based PDF or DOCX file."
        )
    return text


def extract_skills_from_text(text):
    """Find known skill terms in resume text and return unique labels."""
    searchable = re.sub(r"\s+", " ", text.casefold())
    found = []
    # Match longer phrases first to avoid a shorter term consuming a phrase.
    for term in sorted(SKILL_TERMS, key=len, reverse=True):
        escaped = re.escape(term.casefold()).replace(r"\ ", r"\s+")
        pattern = rf"(?<![a-z0-9+#]){escaped}(?![a-z0-9+#])"
        if re.search(pattern, searchable):
            canonical = ALIASES.get(term.casefold(), term.casefold())
            if canonical not in found:
                found.append(canonical)
    return found


def parse_uploaded_resume(uploaded_file, extension=None):
    """Return extracted text and skills for a Django UploadedFile."""
    text = extract_text_from_resume(uploaded_file, extension=extension)
    return {"text": text, "skills": extract_skills_from_text(text)}


def extract_education_from_text(text):
    """Best-effort education hint; users can override it in the form."""
    patterns = [
        r"\b(B\.?\s?Tech(?:nology)?(?:\s+in\s+[A-Za-z &]+)?)\b",
        r"\b(B\.?\s?E\.?)(?:\s+in\s+[A-Za-z &]+)?\b",
        r"\b(M\.?\s?Tech(?:nology)?(?:\s+in\s+[A-Za-z &]+)?)\b",
        r"\b(MCA|MBA|BCA|MCA|BSc|B\.Sc\.?|MSc|M\.Sc\.?|Bachelor(?:'s)? degree|Master(?:'s)? degree)\b",
        r"\b(Intermediate|Higher Secondary|Class XII|12th)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return re.sub(r"\s+", " ", match.group(0)).strip()
    return ""


def extract_experience_from_text(text):
    """Best-effort years-of-experience estimate, otherwise return None."""
    patterns = [
        r"\b(\d+(?:\.\d+)?)\s*\+?\s+years?\s+(?:of\s+)?(?:professional\s+)?experience\b",
        r"\b(\d+(?:\.\d+)?)\s*\+?\s+years?\s+in\s+(?:software|development|IT|data|engineering)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return min(float(match.group(1)), 60.0)
            except ValueError:
                pass
    return None


def extract_resume_section(text, headings):
    """Extract a readable section until the next common resume heading."""
    lines = [line.strip() for line in (text or "").splitlines()]
    heading_set = {h.casefold() for h in headings}
    stop_headings = {
        "education", "experience", "work experience", "skills", "technical skills",
        "projects", "project experience", "certifications", "certificates",
        "summary", "professional summary", "objective", "achievements",
        "publications", "interests", "languages", "contact", "references",
    }
    collecting = False
    captured = []
    for line in lines:
        normalized = re.sub(r"[^a-z ]", "", line.casefold()).strip()
        if normalized in heading_set:
            collecting = True
            continue
        if collecting and normalized in stop_headings:
            break
        if collecting and line:
            captured.append(line)
        if len(captured) >= 12:
            break
    return "\n".join(captured).strip()


def extract_projects_from_text(text):
    return extract_resume_section(text, {"projects", "project experience", "academic projects"})


def extract_certifications_from_text(text):
    return extract_resume_section(text, {"certifications", "certificates", "licenses and certifications"})
