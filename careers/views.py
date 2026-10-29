
import json
from pathlib import Path

from django.shortcuts import render

from role_matcher import (
    find_matching_roles,
    search_target_roles,
    analyze_target_role,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "role_skill_data.json"


def load_roles():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def home(request):
    if request.method != "POST":
        return render(request, "careers/skills_input.html")

    try:
        user_skills = json.loads(request.POST.get("skills", "[]"))
    except (json.JSONDecodeError, TypeError):
        return render(request, "careers/skills_input.html", {
            "error": "Invalid skills data. Please select your skills again."
        })

    if not isinstance(user_skills, list) or not all(
        isinstance(skill, str) for skill in user_skills
    ):
        return render(request, "careers/skills_input.html", {
            "error": "Please submit a valid list of skills."
        })

    user_skills = [skill.strip() for skill in user_skills if skill.strip()]

    if not user_skills:
        return render(request, "careers/skills_input.html", {
            "error": "Please select at least one skill."
        })

    education = request.POST.get("education", "").strip()
    experience = request.POST.get("experience", "0").strip()
    interests_text = request.POST.get("interests", "").strip()
    target_career = request.POST.get("target_career", "").strip()

    interests = [
        item.strip()
        for item in interests_text.split(",")
        if item.strip()
    ]

    try:
        experience_years = float(experience)
        if not 0 <= experience_years <= 60:
            raise ValueError
    except ValueError:
        return render(request, "careers/skills_input.html", {
            "error": "Enter a valid experience value between 0 and 60."
        })

    if not education:
        return render(request, "careers/skills_input.html", {
            "error": "Please enter your education."
        })

    try:
        roles = load_roles()

        recommendations = find_matching_roles(
            user_skills,
            roles,
            interests=interests,
            top_n=10,
        )

        target_analysis = None
        target_options = []

        if target_career:
            target_options = search_target_roles(
                target_career,
                roles,
                limit=10,
            )

            if target_options:
                # Analyze the highest-ranked title match.
                selected = target_options[0]
                target_analysis = analyze_target_role(
                    user_skills,
                    selected["role"],
                    roles[selected["role"]],
                )

        context = {
            "education": education,
            "experience": experience_years,
            "interests": interests,
            "user_skills": user_skills,
            "recommendations": recommendations,
            "target_career": target_career,
            "target_analysis": target_analysis,
            "target_options": target_options,
        }

        return render(request, "careers/results.html", context)

    except (FileNotFoundError, json.JSONDecodeError):
        return render(request, "careers/skills_input.html", {
            "error": (
                "Career data could not be loaded. "
                "Check data/processed/role_skill_data.json."
            )
        })
