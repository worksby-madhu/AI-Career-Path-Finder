import json

from resume_parser import get_user_profile
from role_matcher import find_matching_roles


import json
from pathlib import Path


def load_roles():
    project_dir = Path(__file__).resolve().parent

    roles_file = (
        project_dir
        / "data"
        / "processed"
        / "role_skill_data.json"
    )

    with roles_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def display_roles(matching_roles):
    print("\n===================================")
    print("       SUITABLE CAREER ROLES")
    print("===================================")

    if not matching_roles:
        print("\nNo suitable roles found.")
        print("Try adding more skills or updating your interests.")
        return

    for index, role_data in enumerate(matching_roles, start=1):
        print(f"\n{index}. {role_data['role']}")
        print(f"Overall Match: {role_data['match_percentage']}%")
        print(f"Skill Match: {role_data['skill_match_percentage']}%")

        print("Matched Skills:")
        if role_data["matched_skills"]:
            for skill in role_data["matched_skills"]:
                print(f"  ✓ {skill}")
        else:
            print("  None")

        print("Missing Skills (top 10):")
        if role_data["missing_skills"]:
            for skill in role_data["missing_skills"][:10]:
                print(f"  ✗ {skill}")

            remaining = len(role_data["missing_skills"]) - 10

            if remaining > 0:
                print(f"  ...and {remaining} more skills")
        else:
            print("  None")


def main():

    print("======================================")
    print("       AI CAREER PATH FINDER")
    print("======================================")

    user = get_user_profile()

    roles = load_roles()

    matching_roles = find_matching_roles(
    user["skills"],
    roles,
    interests=user["interests"],
    top_n=10,
)
    

    display_roles(matching_roles)


if __name__ == "__main__":
    main()