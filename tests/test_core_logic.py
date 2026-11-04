"""Lightweight tests for matching, roadmap generation, and resume parsing."""
import json
import unittest
from pathlib import Path

from role_matcher import find_resume_matching_roles, find_interest_matching_roles, analyze_target_role
from careers.roadmap_generator import generate_learning_roadmap
from resume_parser import extract_education_from_text, extract_experience_from_text, extract_projects_from_text, extract_certifications_from_text

ROOT = Path(__file__).resolve().parents[1]
ROLES = json.loads((ROOT / "data/processed/role_skill_data.json").read_text(encoding="utf-8"))


class CareerCoreTests(unittest.TestCase):
    def test_resume_matching_returns_ranked_roles(self):
        matches = find_resume_matching_roles(["Python", "SQL", "Pandas"], ROLES, top_n=10)
        self.assertTrue(matches)
        self.assertLessEqual(len(matches), 10)
        self.assertIn("skill_match_percentage", matches[0])

    def test_interest_matching_uses_interest_signal(self):
        matches = find_interest_matching_roles(["Data Analysis"], ROLES, user_skills=[], top_n=10)
        self.assertTrue(matches)
        self.assertTrue(any("data" in item["role"].casefold() for item in matches))

    def test_target_analysis_and_roadmap(self):
        role = "data analyst"
        analysis = analyze_target_role(["SQL", "Excel"], role, ROLES[role])
        roadmap = generate_learning_roadmap(role, ["SQL", "Excel"], analysis, weeks=8)
        self.assertIn("skill_match_percentage", analysis)
        self.assertTrue(roadmap.get("stages"))
        self.assertTrue(all(stage.get("tasks") for stage in roadmap["stages"]))

    def test_resume_section_extraction(self):
        text = "Education\nB.Tech\nProjects\nEV battery monitor\nCertifications\nPython course\nSkills\nPython"
        self.assertIn("B.Tech", extract_education_from_text(text))
        self.assertIn("EV battery monitor", extract_projects_from_text(text))
        self.assertIn("Python course", extract_certifications_from_text(text))
        self.assertIsNone(extract_experience_from_text(text))


if __name__ == "__main__":
    unittest.main()
