
import json
from pathlib import Path

from resume_parser import get_user_profile
from role_matcher_updated import (
    find_matching_roles,
    search_target_roles,
    analyze_target_role,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "processed" / "role_skill_data.json"


def load_roles():
    """Load processed ESCO career data."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"\nCareer data not found: {DATA_FILE}\n"
            "Please run esco_loader.py first."
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def display_career_details(role_data):
    """Display matched and missing skills for a career."""

    print("\n" + "=" * 50)
    print("CAREER SKILL ANALYSIS")
    print("=" * 50)

    print(f"Career: {role_data['role']}")

    description = role_data.get("description", "")
    if description:
        print(f"Description: {description}")

    matched_skills = role_data.get("matched_skills", [])
    missing_skills = role_data.get("missing_skills", [])

    matched_count = role_data.get(
        "matched_skill_count", len(matched_skills)
    )
    total_count = role_data.get(
        "required_skill_count",
        matched_count + len(missing_skills),
    )

    if total_count > 0:
        coverage = role_data.get("skill_match_percentage", 0)
        print(f"Skill coverage: {coverage}%")
        print(f"Matched skills: {matched_count}/{total_count}")
        print(
            "Analysis based on:",
            role_data.get("skill_data_source", "Unknown")
        )
    else:
        print("Skill coverage: Cannot be calculated.")
        print("No linked skills are available for this occupation.")
        print(
            "Analysis based on:",
            role_data.get("skill_data_source", "Unknown")
        )

    print("\nMATCHED SKILLS")

    if matched_skills:
        for skill in matched_skills:
            print(f"  + {skill}")
    else:
        print("  No matching skills found.")

    print("\nSKILLS TO LEARN")

    if missing_skills:
        for skill in missing_skills[:15]:
            print(f"  - {skill}")

        remaining = len(missing_skills) - 15

        if remaining > 0:
            print(f"  ...and {remaining} more skills")
    else:
        print("  No missing skills in the available data.")

    print(
        "\nNote: Skill coverage measures how many listed role "
        "skills match your profile. It is not a hiring probability."
    )


def choose_career(careers):
    """Let the user select a career from a numbered list."""

    if not careers:
        print("\nNo careers available to select.")
        return None

    while True:
        choice = input(
            "\nEnter your career number (0 to cancel): "
        ).strip()

        if choice.isdigit():
            number = int(choice)

            if number == 0:
                return None

            if 1 <= number <= len(careers):
                return careers[number - 1]

        print(
            f"Enter a number from 1 to {len(careers)}, "
            "or 0 to cancel."
        )


def display_recommendations(careers, limit=10):
    """Display careers that match the user's existing skills."""

    print("\n" + "=" * 50)
    print("CAREERS SUITABLE FOR YOUR PROFILE")
    print("=" * 50)

    if not careers:
        print("No skill-based career recommendations found.")
        print("Try adding more skills to your profile.")
        return

    for index, career in enumerate(careers[:limit], start=1):
        print(
            f"{index}. {career['role']} - "
            f"{career['skill_match_percentage']}% skill coverage"
        )


def get_target_career(roles):
    """Search the complete occupation catalogue for a target role."""

    while True:
        search_term = input(
            "\nEnter your target career "
            "(e.g., AI Engineer, Python Developer): "
        ).strip()

        if search_term:
            break

        print("Please enter a career name.")

    target_options = search_target_roles(
        search_term,
        roles,
        limit=10,
    )

    if not target_options:
        print("\nNo similar occupation titles found.")
        print("Try another title or a broader career name.")
        return None

    print("\nMATCHING TARGET CAREERS")

    for index, item in enumerate(target_options, start=1):
        print(f"{index}. {item['role']}")

    return choose_career(target_options)


def display_alternative_careers(
    careers, selected_role, limit=5
):
    """Display alternative career recommendations."""

    alternatives = [
        career
        for career in careers
        if career["role"] != selected_role
    ]

    if not alternatives:
        return

    print("\n" + "=" * 50)
    print("OTHER SUITABLE CAREER OPTIONS")
    print("=" * 50)

    for index, career in enumerate(alternatives[:limit], start=1):
        print(
            f"{index}. {career['role']} - "
            f"{career['skill_match_percentage']}% skill coverage"
        )


def main():
    print("=" * 50)
    print("          AI CAREER PATH FINDER")
    print("=" * 50)

    # Step 1: Collect the user's profile.
    user = get_user_profile()

    if not isinstance(user, dict):
        print("Unable to read the user profile.")
        return

    user_skills = user.get("skills", [])
    interests = user.get("interests", [])

    if not isinstance(user_skills, list):
        print("The profile's skills must be a list.")
        return

    # Step 2: Load the processed career dataset.
    roles = load_roles()

    # Step 3: Generate profile-based recommendations.
    print("\nAnalyzing your profile...")

    all_matches = find_matching_roles(
        user_skills,
        roles,
        interests=interests,
        top_n=len(roles),
    )

    display_recommendations(all_matches, limit=10)

    # Step 4: Ask whether the user has a target career.
    while True:
        answer = input(
            "\nDo you have a specific career role in mind? "
            "(yes/no): "
        ).strip().casefold()

        if answer in ("yes", "y", "no", "n"):
            break

        print("Please enter yes or no.")

    selected_role = None

    if answer in ("yes", "y"):
        selected = get_target_career(roles)

        if selected is None:
            print("\nTarget career selection cancelled.")
        else:
            selected_role = selected["role"]

    else:
        if all_matches:
            selected = choose_career(all_matches[:10])

            if selected is not None:
                selected_role = selected["role"]
            else:
                print("\nCareer selection cancelled.")
                return

        else:
            print(
                "\nNo skill-based recommendations are available."
            )
            print("You can still search for a target career.")

            selected = get_target_career(roles)

            if selected is not None:
                selected_role = selected["role"]

    # Step 5: Analyze the selected role independently.
    if selected_role:
        selected_analysis = analyze_target_role(
            user_skills,
            selected_role,
            roles[selected_role],
        )

        display_career_details(selected_analysis)

        # Step 6: Show alternative suitable careers.
        display_alternative_careers(
            all_matches,
            selected_role,
            limit=5,
        )

        # Step 7: Roadmap will be added in the next stage.
        print("\n" + "=" * 50)
        print("NEXT STEP")
        print("=" * 50)
        print(
            "A personalized learning roadmap based on your "
            "missing skills will be added in the next stage."
        )

    print("\nThank you for using AI Career Path Finder!")


if __name__ == "__main__":
    main()
    

