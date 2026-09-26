import json

from resume_parser import get_user_profile
from role_matcher import find_matching_roles


def load_roles():
    with open("data/roles.json", "r") as file:
        return json.load(file)


def display_roles(matching_roles):

    print("\n===================================")
    print("       SUITABLE CAREER ROLES")
    print("===================================")

    for index, role_data in enumerate(matching_roles, start=1):

        print(f"\n{index}. {role_data['role']}")
        print(f"Match: {role_data['match_percentage']}%")

        print("Matched Skills:")
        if role_data["matched_skills"]:
            for skill in role_data["matched_skills"]:
                print(f"  ✓ {skill}")
        else:
            print("  None")

        print("Missing Skills:")
        if role_data["missing_skills"]:
            for skill in role_data["missing_skills"]:
                print(f"  ✗ {skill}")
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
        roles
    )

    display_roles(matching_roles)


if __name__ == "__main__":
    main()