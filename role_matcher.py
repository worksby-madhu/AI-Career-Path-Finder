# Common skill names and abbreviations
SKILL_SYNONYMS = {
    # Programming languages
    "pyhton": "python (computer programming)",
    "python": "python (computer programming)",
    "py": "python (computer programming)",
    "js": "javascript",

    # Machine learning and AI
    "ml": "machine learning",
    "ai": "artificial intelligence",

    # Web development
    "react": "react",
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "node js": "node.js",
    "html5": "html",
    "css3": "css",
    "full stack": "fullstack",

    # Data and databases
    "postgres": "postgresql",
    "scikit-learn": "scikit learn",
}


def normalize_skill(skill):
    """Normalize common skill names and variations."""

    skill = skill.strip().casefold()
    return SKILL_SYNONYMS.get(skill, skill)


def find_matching_roles(user_skills, roles, interests=None, top_n=10):
    """Rank ESCO occupations using skill matches and interests."""

    # Normalize and remove duplicate user skills
    user_skills = {
        normalize_skill(skill)
        for skill in user_skills
        if isinstance(skill, str) and skill.strip()
    }

    interests = [
        interest.strip().casefold()
        for interest in (interests or [])
        if isinstance(interest, str) and interest.strip()
    ]

    results = []

    # Examine every occupation provided by the ESCO catalogue
    for role, role_data in roles.items():

        required_skills = role_data.get("skills", [])

        normalized_required = {
            normalize_skill(skill)
            for skill in required_skills
            if isinstance(skill, str) and skill.strip()
        }

        if not normalized_required:
            continue

        # Find skills the user already has
        matched_skill_names = user_skills & normalized_required

        # Ignore occupations with no matching skills
        if not matched_skill_names:
            continue

        matched_skills = [
            skill for skill in required_skills
            if isinstance(skill, str)
            and normalize_skill(skill) in matched_skill_names
        ]

        missing_skills = [
            skill for skill in required_skills
            if isinstance(skill, str)
            and normalize_skill(skill) not in user_skills
        ]

        # Percentage of the user's entered skills matched
        skill_score = (
            len(matched_skill_names) / len(user_skills) * 100
            if user_skills else 0
        )

        # Check whether the occupation title relates to an interest
        role_name = role.casefold()
        interest_words = {
            word
            for interest in interests
            for word in interest.split()
            if len(word) > 2
}
        role_words = set(role_name.split())
        interest_match = bool(interest_words & role_words)
        # interest_match = any(
        #     interest in role_name
        #     for interest in interests
        # )

        results.append({
            "role": role,
            "description": role_data.get("description", ""),
            "match_percentage": round(skill_score, 2),
            "skill_match_percentage": round(skill_score, 2),
            "interest_match": interest_match,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        })

    # Rank by skill overlap first, then interest relevance
    results.sort(
        key=lambda item: (
            item["interest_match"],
            item["skill_match_percentage"],
            len(item["matched_skills"]),
        ),
        reverse=True,
    )

    return results[:top_n]
