
import json
from pathlib import Path

import pandas as pd


# Locate the project folders automatically
BASE_DIR = Path(__file__).resolve().parent
ESCO_DIR = BASE_DIR / "data" / "esco"
OUTPUT_DIR = BASE_DIR / "data" / "processed"


def load_esco_data():
    """Read the three ESCO CSV files."""

    occupations = pd.read_csv(ESCO_DIR / "occupations_en.csv")
    skills = pd.read_csv(ESCO_DIR / "skills_en.csv")
    relations = pd.read_csv(
        ESCO_DIR / "occupationSkillRelations_en.csv"
    )

    print("ESCO files loaded successfully!")
    print("Occupations:", len(occupations))
    print("Skills:", len(skills))
    print("Relationships:", len(relations))

    return occupations, skills, relations


def build_role_skill_data(occupations, skills, relations):
    """Connect occupation names to their associated skills."""

    # Select and rename the occupation columns
    occupation_data = occupations[
        ["conceptUri", "preferredLabel", "description"]
    ].copy()

    occupation_data = occupation_data.rename(
        columns={
            "conceptUri": "occupationUri",
            "preferredLabel": "role",
            "description": "role_description",
        }
    )

    # Select and rename the skill columns
    skill_data = skills[
        ["conceptUri", "preferredLabel"]
    ].copy()

    skill_data = skill_data.rename(
        columns={
            "conceptUri": "skillUri",
            "preferredLabel": "skill",
        }
    )

    # Join each relationship to its occupation
    data = relations.merge(
        occupation_data,
        on="occupationUri",
        how="inner",
    )

    # Join each skill URI to its skill name
    data = data.merge(
        skill_data,
        on="skillUri",
        how="inner",
    )

    role_data = {}

    for _, row in data.iterrows():
        role = row["role"]
        skill = row["skill"]

        if not isinstance(role, str) or not isinstance(skill, str):
            continue

        if role not in role_data:
            role_data[role] = {
                "description": (
                    row["role_description"]
                    if isinstance(row["role_description"], str)
                    else ""
                ),
                "skills": [],
            }

        if skill not in role_data[role]["skills"]:
            role_data[role]["skills"].append(skill)

    return role_data


def save_role_skill_data(role_data):
    """Save the processed data as JSON."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "role_skill_data.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            role_data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\nProcessed data saved successfully!")
    print("Total occupations with linked skills:", len(role_data))


def main():
    occupations, skills, relations = load_esco_data()

    role_data = build_role_skill_data(
        occupations,
        skills,
        relations,
    )

    save_role_skill_data(role_data)

    # Display one example
    if role_data:
        example_role = next(iter(role_data))

        print("\nExample occupation:", example_role)
        print("Associated skills:")

        for skill in role_data[example_role]["skills"][:10]:
            print("-", skill)


if __name__ == "__main__":
    main()
