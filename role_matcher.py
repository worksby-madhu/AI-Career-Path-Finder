"""Career matching with practical core-skill profiles and ESCO fallback."""

import re
from difflib import SequenceMatcher


# --------------------------------------------------
# 1. SKILL NORMALIZATION
# --------------------------------------------------

SKILL_SYNONYMS = {
    "py": "python",
    "pyhton": "python",
    "python3": "python",
    "js": "javascript",
    "ecmascript": "javascript",
    "ts": "typescript",
    "html5": "html",
    "css3": "css",
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "genai": "generative ai",
    "gen ai": "generative ai",
    "dl": "deep learning",
    "postgres": "postgresql",
    "sklearn": "scikit-learn",
    "hugging face": "hugging face",
    "hugging faces": "hugging face",
    "huggingface": "hugging face",
    "powerbi": "power bi",
    "dsa": "data structures and algorithms",
    "github": "git and github",
    "git": "git and github",
    "oop": "object-oriented programming",
    "api": "rest apis",
    "rest api": "rest apis",
    "restful api": "rest apis",
    "object detection": "object detection",
}


def normalize_text(value):
    """Normalize text for comparisons without losing common tech symbols."""
    value = str(value).strip().casefold()
    value = re.sub(r"[^a-z0-9+#. ]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_skill(skill):
    """Convert common skill variations into standard names."""
    skill = normalize_text(skill)

    if skill in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[skill]

    # ESCO sometimes adds a parenthetical context to a skill label.
    for base in (
        "python",
        "javascript",
        "sql",
        "java",
        "html",
        "css",
        "c++",
        "c#",
        "machine learning",
        "artificial intelligence",
    ):
        if skill == f"{base} (computer programming)":
            return base

    return skill


def normalize_skills(skills):
    """Normalize skills and remove duplicates while preserving order."""
    result = []
    seen = set()

    for skill in skills or []:
        if not isinstance(skill, str) or not skill.strip():
            continue

        normalized = normalize_skill(skill)

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result


# --------------------------------------------------
# 2. PRACTICAL ROLE PROFILES
# --------------------------------------------------
# Core skills determine the skill coverage percentage.
# Optional skills are tracked separately.

ROLE_PROFILES = {
    "frontend developer": {
        "core": [
            "html",
            "css",
            "javascript",
            "react",
            "responsive design",
            "git and github",
        ],
        "optional": [
            "typescript",
            "accessibility",
            "frontend testing",
            "browser developer tools",
        ],
    },
    "web developer": {
        "core": [
            "html",
            "css",
            "javascript",
            "responsive design",
            "frontend framework",
            "rest apis",
            "git and github",
        ],
        "optional": [
            "http fundamentals",
            "browser developer tools",
            "accessibility",
            "frontend testing",
        ],
    },
    "full stack developer": {
        "core": [
            "html",
            "css",
            "javascript",
            "frontend framework",
            "backend framework",
            "rest apis",
            "sql",
            "git and github",
        ],
        "optional": [
            "typescript",
            "testing",
            "authentication",
            "deployment",
            "docker",
        ],
    },
    "python developer": {
        "core": [
            "python",
            "object-oriented programming",
            "sql",
            "rest apis",
            "git and github",
            "debugging",
        ],
        "optional": [
            "data structures and algorithms",
            "unit testing",
            "virtual environments",
            "django",
            "flask",
        ],
    },
    "software developer": {
        "core": [
            "programming fundamentals",
            "object-oriented programming",
            "data structures and algorithms",
            "git and github",
            "debugging",
            "sql",
        ],
        "optional": [
            "unit testing",
            "rest apis",
            "software design",
        ],
    },
    "ai engineer": {
        "core": [
            "python",
            "machine learning",
            "deep learning",
            "statistics",
            "data preprocessing",
            "model evaluation",
        ],
        "optional": [
            "sql",
            "generative ai",
            "deep learning framework",
            "git and github",
            "rest apis",
        ],
    },
    "machine learning engineer": {
        "core": [
            "python",
            "machine learning",
            "statistics",
            "data preprocessing",
            "feature engineering",
            "model evaluation",
            "scikit-learn",
        ],
        "optional": [
            "deep learning",
            "deep learning framework",
            "sql",
            "git and github",
            "model deployment",
        ],
    },
    "data analyst": {
        "core": [
            "sql",
            "excel",
            "data cleaning",
            "data visualization",
            "statistics",
            "power bi",
        ],
        "optional": [
            "python",
            "pandas",
            "numpy",
            "business analysis",
        ],
    },
    "computer vision engineer": {
        "core": [
            "python",
            "computer vision",
            "opencv",
            "image processing",
            "object detection",
            "machine learning",
        ],
        "optional": [
            "deep learning",
            "deep learning framework",
            "numpy",
            "model evaluation",
            "git and github",
        ],
    },
}


# --------------------------------------------------
# 3. ROLE NAME ALIASES
# --------------------------------------------------

ROLE_ALIASES = {
    "front end developer": "frontend developer",
    "front-end developer": "frontend developer",
    "frontend dev": "frontend developer",
    "fullstack developer": "full stack developer",
    "full-stack developer": "full stack developer",
    "full stack dev": "full stack developer",
    "python dev": "python developer",
    "python devloper": "python developer",
    "python dveloper": "python developer",
    "software engineer": "software developer",
    "web dev": "web developer",
    "ai developer": "ai engineer",
    "artificial intelligence engineer": "ai engineer",
    "ml engineer": "machine learning engineer",
}


def canonical_role_name(role):
    """Convert role-name variations to a consistent title."""
    title = normalize_text(role)
    return ROLE_ALIASES.get(title, title)


def get_profile_name(role):
    """Map occupation titles to practical role profiles."""
    title = canonical_role_name(role)

    if "computer vision engineer" in title:
        return "computer vision engineer"

    if "machine learning engineer" in title:
        return "machine learning engineer"

    if "artificial intelligence engineer" in title or title == "ai engineer":
        return "ai engineer"

    if "data analyst" in title:
        return "data analyst"

    if "frontend developer" in title or "front end developer" in title:
        return "frontend developer"

    if "full stack developer" in title or "fullstack developer" in title:
        return "full stack developer"

    if "web developer" in title:
        return "web developer"

    if "python developer" in title:
        return "python developer"

    if "software developer" in title:
        return "software developer"

    return title if title in ROLE_PROFILES else None


# --------------------------------------------------
# 4. SKILL EQUIVALENTS
# --------------------------------------------------

def expand_profile_skill(skill):
    """Return accepted equivalents for a role requirement."""
    alternatives = {
        "frontend framework": [
            "react",
            "angular",
            "vue",
        ],
        "backend framework": [
            "django",
            "flask",
            "fastapi",
            "express",
            "spring boot",
        ],
        "deep learning framework": [
            "pytorch",
            "tensorflow",
            "keras",
        ],
        "programming fundamentals": [
            "python",
            "java",
            "javascript",
            "c",
            "c++",
        ],
        "object-oriented programming": [
            "object-oriented programming",
            "oop",
        ],
        "debugging": [
            "debugging",
            "debugging tools",
        ],
        "rest apis": [
            "rest apis",
            "api development",
            "fastapi",
            "django rest framework",
        ],
        "data visualization": [
            "data visualization",
            "matplotlib",
            "power bi",
            "tableau",
        ],
        "testing": [
            "testing",
            "unit testing",
            "pytest",
        ],
    }

    return [
        normalize_skill(item)
        for item in alternatives.get(skill, [skill])
    ]


def skill_is_present(required_skill, user_skills):
    """Check whether an accepted equivalent is present."""
    user_set = set(user_skills)

    return any(
        item in user_set
        for item in expand_profile_skill(required_skill)
    )


def _profile_data(profile_name):
    """Get core and optional skills for a known profile."""
    profile = ROLE_PROFILES[profile_name]
    return profile["core"], profile.get("optional", [])


# --------------------------------------------------
# 5. TARGET CAREER ANALYSIS
# --------------------------------------------------

def analyze_target_role(user_skills, role, role_data):
    """
    Analyze a target role using a practical profile when available.
    Unknown roles use a limited ESCO skill list.
    """
    user_skill_list = normalize_skills(user_skills)
    user_skill_set = set(user_skill_list)

    profile_name = get_profile_name(role)

    if profile_name:
        required_skills, optional_skills = _profile_data(profile_name)
        source = "practical role profile"
    else:
        esco_skills = normalize_skills(role_data.get("skills", []))
        required_skills = esco_skills[:12]
        optional_skills = esco_skills[12:20]
        source = "ESCO occupation data (limited list)"

    # Core skills the user already has.
    matched_skills = [
        skill
        for skill in required_skills
        if skill_is_present(skill, user_skill_set)
    ]

    # Core skills the user still needs.
    missing_skills = [
        skill
        for skill in required_skills
        if not skill_is_present(skill, user_skill_set)
    ]

    # Optional skills the user already has.
    matched_optional = [
        skill
        for skill in optional_skills
        if skill_is_present(skill, user_skill_set)
    ]

    total = len(required_skills)

    coverage = (
        len(matched_skills) / total * 100
        if total else 0.0
    )

    # Display actual technologies for grouped requirements.
    display_names = {
        "frontend framework": next(
            (
                skill.title()
                for skill in ("react", "angular", "vue")
                if skill in user_skill_set
            ),
            "React, Angular or Vue",
        ),
        "backend framework": next(
            (
                skill.title()
                for skill in (
                    "django",
                    "flask",
                    "fastapi",
                    "express",
                    "spring boot",
                )
                if skill in user_skill_set
            ),
            "Django, Flask, FastAPI or another backend framework",
        ),
        "deep learning framework": next(
            (
                skill.title()
                for skill in ("pytorch", "tensorflow", "keras")
                if skill in user_skill_set
            ),
            "PyTorch, TensorFlow or Keras",
        ),
    }

    return {
        "role": role,
        "description": role_data.get("description", ""),
        "skill_match_percentage": round(coverage, 2),
        "matched_skill_count": len(matched_skills),
        "required_skill_count": total,
        "matched_skills": [
            display_names.get(skill, skill)
            for skill in matched_skills
        ],
        "missing_skills": [
            display_names.get(skill, skill)
            for skill in missing_skills
        ],
        "optional_skills": [
            skill
            for skill in optional_skills
            if skill not in matched_optional
        ],
        "matched_optional_skills": matched_optional,
        "skill_data_source": source,
    }


# --------------------------------------------------
# 6. TARGET CAREER SEARCH
# --------------------------------------------------

def search_target_roles(search_term, roles, limit=10):
    """Search ESCO titles while prioritizing practical role names."""
    query = canonical_role_name(search_term)
    # Common career-title aliases map to dataset terminology.
    alias_map = {"ui ux designer": "user interface designer", "ui/ux designer": "user interface designer", "ux designer": "user experience designer", "ml engineer": "machine learning engineer"}
    query = canonical_role_name(alias_map.get(str(search_term).strip().casefold(), query))

    if not query:
        return []

    results = []

    for role, role_data in roles.items():
        title = normalize_text(role)

        if title == query:
            score = 100
        elif title.startswith(query):
            score = 92
        elif query in title:
            score = 88
        elif title in query:
            score = 82
        else:
            score = SequenceMatcher(
                None,
                query,
                title,
            ).ratio() * 70

        if title == query and get_profile_name(title):
            score += 5

        if score >= 55:
            results.append({
                "role": role,
                "description": role_data.get("description", ""),
                "search_score": round(score, 2),
            })

    results.sort(
        key=lambda item: (
            -item["search_score"],
            item["role"].casefold(),
        )
    )

    return results[:limit]


# --------------------------------------------------
# 7. TOP CAREERS BASED ON RESUME SKILLS
# --------------------------------------------------

def find_resume_matching_roles(user_skills, roles, top_n=10):
    """
    Rank careers using skill coverage only.
    Selected interests do not affect this ranking.
    """
    user_skill_list = normalize_skills(user_skills)
    user_skill_set = set(user_skill_list)

    results = []

    for role, role_data in roles.items():
        analysis = analyze_target_role(
            user_skill_list,
            role,
            role_data,
        )

        # Resume matches must have at least one matched skill.
        if analysis["matched_skill_count"] == 0:
            continue

        # Percentage of the user's skills relevant to this role.
        profile_overlap = (
            analysis["matched_skill_count"] / len(user_skill_set) * 100
            if user_skill_set else 0.0
        )

        results.append({
            **analysis,
            "profile_overlap_percentage": round(profile_overlap, 2),
        })

    # Rank by role skill coverage, not interests.
    results.sort(
        key=lambda item: (
            item["skill_match_percentage"],
            item["matched_skill_count"],
            item["role"].casefold(),
        ),
        reverse=True,
    )

    return results[:top_n]


# --------------------------------------------------
# 8. CAREERS BASED ON SELECTED INTERESTS
# --------------------------------------------------

def find_interest_matching_roles(
    interests,
    roles,
    user_skills=None,
    top_n=10,
):
    """Match interests against role titles, descriptions, and ESCO skills.

    Interest matching is a relevance signal, not a skill-coverage score.
    Existing role/skill data remains the source of career names and details.
    """
    interest_aliases = {
        "python development": ["python developer", "python programming", "python"],
        "web development": ["web developer", "web development", "frontend", "backend", "full stack"],
        "frontend development": ["frontend", "front end", "web interface"],
        "backend development": ["backend", "back end", "server side"],
        "full stack development": ["full stack", "frontend", "backend", "web developer"],
        "software engineering": ["software developer", "software engineer", "software development"],
        "data analysis": ["data analyst", "data analysis", "business intelligence", "data visualization"],
        "data analytics": ["data analyst", "data analysis", "business intelligence"],
        "data science": ["data scientist", "data science", "statistical analysis"],
        "machine learning": ["machine learning", "ml engineer", "predictive model"],
        "artificial intelligence": ["artificial intelligence", "ai engineer", "machine learning"],
        "natural language processing": ["natural language processing", "nlp", "text mining"],
        "computer vision": ["computer vision", "image processing", "image recognition"],
        "cybersecurity": ["cybersecurity", "security analyst", "information security"],
        "cloud computing": ["cloud engineer", "cloud computing", "cloud infrastructure"],
        "devops": ["devops", "site reliability", "deployment automation"],
        "ui/ux design": ["ui ux", "user experience", "user interface", "interaction design", "figma"],
        "software testing": ["software tester", "quality assurance", "test automation", "testing"],
        "mobile app development": ["mobile app", "android developer", "ios developer", "mobile application"],
        "database management": ["database", "database administrator", "sql"],
        "data engineering": ["data engineer", "data pipeline", "data warehouse"],
        "business analysis": ["business analyst", "business analysis", "requirements analysis"],
    }

    normalized_interests = [
        normalize_text(item)
        for item in (interests or [])
        if isinstance(item, str) and item.strip()
    ]
    if not normalized_interests:
        return []

    results = []
    skills_for_analysis = user_skills or []
    for role, role_data in roles.items():
        title = normalize_text(role)
        role_skills = [normalize_text(x) for x in role_data.get("skills", []) if isinstance(x, str)]
        matched_interests = []
        for interest in normalized_interests:
            aliases = [normalize_text(alias) for alias in interest_aliases.get(interest, [interest])]
            # Prefer explicit occupation-title matches. Skill labels provide a
            # secondary signal; generic description phrases are deliberately
            # not enough on their own because they create unrelated matches.
            title_match = any(alias and alias in title for alias in aliases)
            # Broad interests such as data analysis should not match every
            # occupation that merely lists analysis as a transferable skill.
            broad_interest = interest in {"data analysis", "data analytics", "software engineering", "web development"}
            skill_match = (not broad_interest) and any(
                alias and any(alias == skill for skill in role_skills)
                for alias in aliases
            )
            if title_match or skill_match:
                matched_interests.append(interest)
        if not matched_interests:
            continue
        analysis = analyze_target_role(skills_for_analysis, role, role_data)
        results.append({
            **analysis,
            "matched_interests": matched_interests,
            "interest_match_count": len(matched_interests),
        })

    results.sort(
        key=lambda item: (
            item["interest_match_count"],
            item["skill_match_percentage"],
            item["role"].casefold(),
        ),
        reverse=True,
    )
    return results[:top_n]


# --------------------------------------------------
# 9. BACKWARD COMPATIBILITY
# --------------------------------------------------

def find_matching_roles(user_skills, roles, interests=None, top_n=10):
    """
    Keep the original function available for existing imports.
    This function now returns resume-based recommendations only.
    """
    return find_resume_matching_roles(
        user_skills,
        roles,
        top_n=top_n,
    )