def find_matching_roles(user_skills, roles):
    
    matching_roles = []

    for role, required_skills in roles.items():

        matched_skills = []

        for skill in required_skills:
            if skill.lower() in user_skills:
                matched_skills.append(skill)

        match_count = len(matched_skills)
        total_skills = len(required_skills)

        match_percentage = (match_count / total_skills) * 100

        missing_skills = [
            skill for skill in required_skills
            if skill.lower() not in user_skills
        ]

        matching_roles.append({
            "role": role,
            "match_percentage": round(match_percentage, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        })

    matching_roles.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return matching_roles