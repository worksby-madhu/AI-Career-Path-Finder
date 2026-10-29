
# role_matcher.py

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
    "hugging face": "huggingface",
    "powerbi": "power bi",
    "object detection": "object detection",
    "dsa": "data structures and algorithms",
    "opencv": "opencv",
    "github": "git and github",
    "git": "git and github",
    "flask": "flask",
    "django": "django",
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
}


def normalize_text(value):
    """Normalize text for comparisons."""
    value = str(value).strip().casefold()
    value = re.sub(r"[^a-z0-9+#. ]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_skill(skill):
    """Convert common skill variations into standard names."""
    skill = normalize_text(skill)

    if skill in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[skill]

    # Handle ESCO labels such as Python (computer programming).
    if skill == "python (computer programming)":
        return "python"

    if skill == "javascript (computer programming)":
        return "javascript"

    if skill == "sql (computer programming)":
        return "sql"

    return skill


def normalize_skills(skills):
    """Normalize skills and remove duplicates."""
    result = []
    seen = set()

    for skill in skills:
        if not isinstance(skill, str) or not skill.strip():
            continue

        normalized = normalize_skill(skill)

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result


# --------------------------------------------------
# 2. PRACTICAL SKILL PROFILES
# --------------------------------------------------
# These profiles provide a practical baseline for common
# career paths. They complement ESCO; they do not replace it.

ROLE_PROFILES = {
    "python developer": [
        "python",
        "object-oriented programming",
        "data structures and algorithms",
        "sql",
        "git and github",
        "debugging",
        "unit testing",
        "rest apis",
        "database fundamentals",
        "virtual environments",
        "django or flask",
    ],

    "web developer": [
        "html",
        "css",
        "javascript",
        "responsive design",
        "git and github",
        "http fundamentals",
        "browser developer tools",
        "rest apis",
        "frontend framework",
        "backend fundamentals",
    ],

    "frontend developer": [
        "html",
        "css",
        "javascript",
        "responsive design",
        "react",
        "git and github",
        "browser developer tools",
        "accessibility",
        "rest apis",
        "frontend testing",
    ],

    "software developer": [
        "programming fundamentals",
        "object-oriented programming",
        "data structures and algorithms",
        "git and github",
        "debugging",
        "unit testing",
        "sql",
        "software design",
        "rest apis",
        "problem solving",
    ],

    "ai engineer": [
        "python",
        "machine learning",
        "deep learning",
        "statistics",
        "linear algebra",
        "data preprocessing",
        "model evaluation",
        "sql",
        "git and github",
        "rest apis",
        "generative ai",
        "deep learning framework",
    ],

    "machine learning engineer": [
        "python",
        "machine learning",
        "deep learning",
        "statistics",
        "data preprocessing",
        "feature engineering",
        "model evaluation",
        "scikit-learn",
        "deep learning framework",
        "git and github",
        "sql",
        "model deployment",
    ],

    "data analyst": [
        "sql",
        "python",
        "pandas",
        "numpy",
        "excel",
        "data visualization",
        "statistics",
        "power bi",
        "data cleaning",
        "business analysis",
    ],

    "computer vision engineer": [
        "python",
        "computer vision",
        "opencv",
        "machine learning",
        "deep learning",
        "object detection",
        "image processing",
        "model evaluation",
        "numpy",
        "deep learning framework",
        "git and github",
    ],
}


ROLE_ALIASES = {
    "python developer": ["python developer"],
    "python dev": ["python developer"],
    "python devloper": ["python developer"],
    "software developer": ["software developer"],
    "software engineer": ["software developer"],
    "web developer": ["web developer"],
    "frontend developer": ["frontend developer"],
    "front end developer": ["frontend developer"],
    "front-end developer": ["frontend developer"],
    "ai engineer": ["ai engineer"],
    "artificial intelligence engineer": ["ai engineer"],
    "ml engineer": ["machine learning engineer"],
    "machine learning engineer": ["machine learning engineer"],
    "data analyst": ["data analyst"],
    "computer vision engineer": ["computer vision engineer"],
}


# --------------------------------------------------
# 3. MAP ESCO OCCUPATIONS TO PRACTICAL PROFILES
# --------------------------------------------------

def get_profile_name(role):
    """Return a practical profile for a recognized occupation."""
    title = normalize_text(role)

    # More specific titles must be checked first.
    if "computer vision engineer" in title:
        return "computer vision engineer"

    if "machine learning engineer" in title:
        return "machine learning engineer"

    if "artificial intelligence engineer" in title:
        return "ai engineer"

    if title == "ai engineer":
        return "ai engineer"

    if "data analyst" in title:
        return "data analyst"

    if "frontend developer" in title or "front end developer" in title:
        return "frontend developer"

    if "web developer" in title:
        return "web developer"

    if "python developer" in title:
        return "python developer"

    if "software developer" in title:
        return "software developer"

    return None


def expand_profile_skill(skill):
    """
    Expand a practical skill into accepted alternatives.

    Alternatives are treated as equivalent for that requirement.
    """
    alternatives = {
        "django or flask": ["django", "flask"],
        "frontend framework": ["react", "angular", "vue"],
        "deep learning framework": [
            "pytorch", "tensorflow", "keras"
        ],
        "programming fundamentals": [
            "python", "java", "javascript", "c", "c++"
        ],
        "object-oriented programming": [
            "object-oriented programming", "oop"
        ],
        "database fundamentals": [
            "sql", "mysql", "postgresql", "mongodb"
        ],
        "debugging": ["debugging", "debugging tools"],
        "unit testing": ["unit testing", "pytest", "testing"],
        "rest apis": [
            "rest apis", "rest api", "api development"
        ],
        "data visualization": [
            "data visualization", "matplotlib", "power bi"
        ],
        "business analysis": [
            "business analysis", "data analysis"
        ],
        "model deployment": [
            "model deployment", "docker", "fastapi"
        ],
    }

    return [
        normalize_skill(item)
        for item in alternatives.get(skill, [skill])
    ]


def skill_is_present(required_skill, user_skills):
    """Check whether a skill requirement is satisfied."""
    alternatives = expand_profile_skill(required_skill)
    return any(item in user_skills for item in alternatives)


# --------------------------------------------------
# 4. SEARCH FOR A TARGET CAREER
# --------------------------------------------------
def search_target_roles(search_term, roles, limit=10):
    """Search ESCO titles and prioritize relevant title matches."""

    query = normalize_text(search_term)

    if not query:
        return []

    # Expand common career names and correct common spelling mistakes.
    aliases = {
        "python developer": [
            "python developer",
            "python programmer",
            "software developer",
        ],
        "python dveloper": [
            "python developer",
            "python programmer",
            "software developer",
        ],
        "web developer": [
            "web developer",
            "web programmer",
        ],
        "ai engineer": [
            "artificial intelligence engineer",
            "ai engineer",
        ],
        "machine learning engineer": [
            "machine learning engineer",
            "machine learning specialist",
        ],
    }

    canonical = aliases.get(query, ROLE_ALIASES.get(query, [query]))

    # Handle a single common typo even if it isn't explicitly listed.
    if query not in aliases and query not in ROLE_ALIASES:
        from difflib import get_close_matches

        known_roles = [
            "python developer",
            "web developer",
            "ai engineer",
            "machine learning engineer",
            "data analyst",
        ]

        close = get_close_matches(
            query, known_roles, n=1, cutoff=0.75
        )

        if close:
            canonical = aliases.get(
                close[0], ROLE_ALIASES.get(close[0], [close[0]])
            )

    results = []

    for role, role_data in roles.items():
        title = normalize_text(role)
        score = 0.0

        for term in canonical:
            term = normalize_text(term)

            if title == term:
                candidate_score = 100
            elif title.startswith(term):
                candidate_score = 95
            elif term in title:
                candidate_score = 90
            elif title in term:
                candidate_score = 85
            else:
                candidate_score = (
                    SequenceMatcher(None, term, title).ratio() * 70
                )

            # Prioritize the actual requested technology or role.
            if query in (
                "python developer",
                "python dveloper",
            ) and "python" in title:
                candidate_score += 25

            if query == "web developer" and "web developer" in title:
                candidate_score += 15

            score = max(score, candidate_score)

        if score >= 55:
            results.append({
                "role": role,
                "description": role_data.get("description", ""),
                "search_score": round(score, 2),
            })

    results.sort(
        key=lambda item: (
            item["search_score"],
            item["role"].casefold(),
        ),
        reverse=True,
    )

    return results[:limit]

# --------------------------------------------------
# 5. ANALYZE A SELECTED TARGET ROLE
# --------------------------------------------------

def analyze_target_role(user_skills, role, role_data):
    """
    Analyze a target role using a practical skill profile when
    available, otherwise use the occupation's ESCO skill list.
    """
    user_skill_set = set(normalize_skills(user_skills))
    profile_name = get_profile_name(role)

    if profile_name:
        required_skills = ROLE_PROFILES[profile_name]
        source = "practical role profile"
    else:
        required_skills = role_data.get("skills", [])
        source = "ESCO occupation data"

    matched_skills = [
        skill for skill in required_skills
        if skill_is_present(skill, user_skill_set)
    ]

    missing_skills = [
        skill for skill in required_skills
        if not skill_is_present(skill, user_skill_set)
    ]

    total = len(required_skills)

    coverage = (
        len(matched_skills) / total * 100
        if total else 0.0
    )

    return {
        "role": role,
        "description": role_data.get("description", ""),
        "skill_match_percentage": round(coverage, 2),
        "matched_skill_count": len(matched_skills),
        "required_skill_count": total,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_data_source": source,
    }


# --------------------------------------------------
# 6. RECOMMEND CAREERS FROM THE USER'S PROFILE
# --------------------------------------------------

def find_matching_roles(
    user_skills,
    roles,
    interests=None,
    top_n=10,
):
    """Rank occupations using relevant skill coverage."""

    user_skill_set = set(normalize_skills(user_skills))

    normalized_interests = [
        normalize_text(item)
        for item in (interests or [])
        if isinstance(item, str) and item.strip()
    ]

    results = []

    for role, role_data in roles.items():
        analysis = analyze_target_role(
            list(user_skill_set),
            role,
            role_data,
        )

        if analysis["matched_skill_count"] == 0:
            continue

        title = normalize_text(role)

        interest_match = any(
            interest in title or title in interest
            for interest in normalized_interests
        )

        # Profile overlap measures the share of entered skills
        # that are relevant to this role.
        profile_overlap = (
            analysis["matched_skill_count"] / len(user_skill_set) * 100
            if user_skill_set else 0.0
        )

        results.append({
            **analysis,
            "profile_overlap_percentage": round(profile_overlap, 2),
            "interest_match": interest_match,
        })

    results.sort(
        key=lambda item: (
            item["skill_match_percentage"],
            item["interest_match"],
            item["matched_skill_count"],
            item["role"].casefold(),
        ),
        reverse=True,
    )

    return results[:top_n]
