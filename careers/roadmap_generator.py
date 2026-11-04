
"""
Generate a structured, personalized career learning roadmap.

This version uses existing skill-gap analysis and reusable learning
templates. It does not require an external AI API.
"""

from collections import OrderedDict


# Reusable learning guidance for common skill gaps.
# Add more skills here as your career dataset grows.
SKILL_GUIDANCE = {
    "python": {
        "topic": "Python programming",
        "tasks": [
            "Practise functions, collections, loops and error handling.",
            "Write small programs and test different inputs.",
        ],
    },
    "object-oriented programming": {
        "topic": "Object-oriented programming",
        "tasks": [
            "Learn classes, objects, inheritance and composition.",
            "Refactor a small program using classes.",
        ],
    },
    "data structures and algorithms": {
        "topic": "Data structures and algorithms",
        "tasks": [
            "Practise arrays, strings, dictionaries, stacks and queues.",
            "Solve beginner-level problems and explain your approach.",
        ],
    },
    "sql": {
        "topic": "SQL and databases",
        "tasks": [
            "Practise SELECT, JOIN, GROUP BY and subqueries.",
            "Design a small relational database and query it.",
        ],
    },
    "git and github": {
        "topic": "Git and GitHub",
        "tasks": [
            "Practise commits, branches, merges and resolving conflicts.",
            "Push a project to GitHub with a clear README.",
        ],
    },
    "debugging": {
        "topic": "Debugging and problem solving",
        "tasks": [
            "Read tracebacks and identify the source of errors.",
            "Use breakpoints and test edge cases.",
        ],
    },
    "unit testing": {
        "topic": "Testing",
        "tasks": [
            "Learn assertions and basic unit testing.",
            "Write tests for successful cases and invalid inputs.",
        ],
    },
    "rest apis": {
        "topic": "REST APIs",
        "tasks": [
            "Understand HTTP methods, status codes and JSON.",
            "Build or consume a small API.",
        ],
    },
    "django": {
        "topic": "Django web development",
        "tasks": [
            "Practise URL routing, views, templates and forms.",
            "Connect a Django view to data and handle validation errors.",
        ],
    },
    "html": {
        "topic": "HTML fundamentals",
        "tasks": [
            "Build accessible page structures using semantic HTML.",
            "Create a multi-section page with a form.",
        ],
    },
    "css": {
        "topic": "CSS and responsive design",
        "tasks": [
            "Practise layouts, Flexbox, Grid and responsive styling.",
            "Make a page usable on mobile and desktop screens.",
        ],
    },
    "javascript": {
        "topic": "JavaScript fundamentals",
        "tasks": [
            "Practise functions, arrays, objects and DOM events.",
            "Build an interactive form with validation.",
        ],
    },
    "responsive design": {
        "topic": "Responsive web design",
        "tasks": [
            "Learn media queries and mobile-first layouts.",
            "Test the interface at different screen sizes.",
        ],
    },
    "react": {
        "topic": "React fundamentals",
        "tasks": [
            "Learn components, props, state and event handling.",
            "Build a small reusable component-based interface.",
        ],
    },
    "machine learning": {
        "topic": "Machine learning fundamentals",
        "tasks": [
            "Study supervised learning, data splitting and evaluation.",
            "Train and evaluate a small model on a suitable dataset.",
        ],
    },
    "deep learning": {
        "topic": "Deep learning fundamentals",
        "tasks": [
            "Learn neural network basics and training workflows.",
            "Build a small model and evaluate its results.",
        ],
    },
    "computer vision": {
        "topic": "Computer vision",
        "tasks": [
            "Practise image loading, preprocessing and basic analysis.",
            "Build a small image-processing or image-classification demo.",
        ],
    },
    "opencv": {
        "topic": "OpenCV",
        "tasks": [
            "Practise reading images, resizing, color conversion and drawing.",
            "Create a small computer-vision application.",
        ],
    },
    "data visualization": {
        "topic": "Data visualization",
        "tasks": [
            "Choose suitable charts and label them clearly.",
            "Create a dashboard or report from a small dataset.",
        ],
    },
    "statistics": {
        "topic": "Statistics for data analysis",
        "tasks": [
            "Review distributions, averages, variation and correlation.",
            "Interpret statistical summaries from a real dataset.",
        ],
    },
    "figma": {
        "topic": "Figma and interface design",
        "tasks": [
            "Practise frames, components, auto layout and design variants.",
            "Create a clickable prototype for a simple application.",
        ],
    },
    "wireframing": {
        "topic": "Wireframing",
        "tasks": [
            "Sketch the key screens and user flow before visual design.",
            "Create low-fidelity wireframes for a real user problem.",
        ],
    },
    "prototyping": {
        "topic": "Prototyping",
        "tasks": [
            "Connect screens into a clickable user journey.",
            "Test the prototype with a few users and record feedback.",
        ],
    },
    "user research": {
        "topic": "User research",
        "tasks": [
            "Learn to write neutral interview questions.",
            "Summarize user needs and turn them into design requirements.",
        ],
    },
    "usability testing": {
        "topic": "Usability testing",
        "tasks": [
            "Write task scenarios for a prototype.",
            "Observe users, record issues and prioritize improvements.",
        ],
    },
    "ui/ux principles": {
        "topic": "UI/UX design principles",
        "tasks": [
            "Study visual hierarchy, consistency, accessibility and usability.",
            "Review an existing interface and identify design improvements.",
        ],
    },
}


ROLE_PROJECTS = {
    "python": (
        "Build a Python application that solves a practical problem, "
        "validates inputs, handles errors and includes a README."
    ),
    "software": (
        "Build a small software application with clear modules, "
        "tests, version control and documentation."
    ),
    "web": (
        "Build a responsive website or web application with a usable "
        "interface, form validation and documented features."
    ),
    "data": (
        "Analyse a public dataset, clean the data, visualize findings "
        "and explain the conclusions in a short report."
    ),
    "machine learning": (
        "Build a machine-learning project with a documented dataset, "
        "baseline, evaluation metrics and limitations."
    ),
    "computer vision": (
        "Build an image-based application and document its test cases, "
        "results and limitations."
    ),
    "ui/ux": (
        "Design a user flow, wireframes and a clickable prototype; "
        "conduct usability testing and document the improvements."
    ),
    "mobile": (
        "Build a small mobile app with multiple screens, input validation "
        "and a clear explanation of its main user flow."
    ),
    "default": (
        "Build a small portfolio project related to the target career. "
        "Document its goals, process, results and what you learned."
    ),
}


def _clean_skills(skills):
    """Return unique, readable skill labels."""
    cleaned = []
    seen = set()

    for skill in skills or []:
        if not isinstance(skill, str):
            continue

        label = skill.strip()
        key = label.casefold()

        if label and key not in seen:
            seen.add(key)
            cleaned.append(label)

    return cleaned


def _guidance_for_skill(skill):
    """Find reusable learning guidance for a missing skill."""
    key = skill.casefold().strip()

    if key in SKILL_GUIDANCE:
        return SKILL_GUIDANCE[key]

    # Support related skill labels in larger career datasets.
    for known_skill, guidance in SKILL_GUIDANCE.items():
        if known_skill in key or key in known_skill:
            return guidance

    return {
        "topic": skill.title(),
        "tasks": [
            f"Learn the fundamentals of {skill} from a trusted tutorial.",
            f"Complete a small practical exercise using {skill}.",
        ],
    }


def _project_for_role(role):
    """Choose a project suggestion using broad career keywords."""
    title = (role or "").casefold()

    if any(word in title for word in ("ui/ux", "ux designer", "ui designer")):
        return ROLE_PROJECTS["ui/ux"]
    if any(word in title for word in ("mobile", "android", "ios")):
        return ROLE_PROJECTS["mobile"]
    if any(word in title for word in ("computer vision", "vision engineer")):
        return ROLE_PROJECTS["computer vision"]
    if any(word in title for word in ("machine learning", "ai engineer", "artificial intelligence")):
        return ROLE_PROJECTS["machine learning"]
    if any(word in title for word in ("data analyst", "data scientist", "analytics")):
        return ROLE_PROJECTS["data"]
    if any(word in title for word in ("web", "frontend", "front-end", "full stack")):
        return ROLE_PROJECTS["web"]
    if "python" in title:
        return ROLE_PROJECTS["python"]
    if any(word in title for word in ("software", "developer", "engineer")):
        return ROLE_PROJECTS["software"]

    return ROLE_PROJECTS["default"]


def generate_learning_roadmap(
    target_role,
    user_skills,
    target_analysis=None,
    weeks=8,
):
    """
    Generate a roadmap based on the selected career and skill gaps.

    target_analysis may be the dictionary returned by analyze_target_role().
    The function still works if no target analysis is available.
    """
    role = (target_role or "").strip() or "Your selected career"
    current_skills = _clean_skills(user_skills)
    current_skill_set = {skill.casefold() for skill in current_skills}

    analysis = target_analysis or {}
    missing_skills = _clean_skills(analysis.get("missing_skills", []))
    matched_skills = _clean_skills(analysis.get("matched_skills", []))

    # If target analysis is unavailable, use a general roadmap.
    if not missing_skills and not analysis:
        missing_skills = [
            "Core fundamentals",
            "Practical tools",
            "Project development",
            "Interview preparation",
        ]

    # Group learning tasks by topic so repeated skills don't create
    # separate, tiny stages.
    grouped = OrderedDict()

    for skill in missing_skills:
        guidance = _guidance_for_skill(skill)
        topic = guidance["topic"]

        if topic not in grouped:
            grouped[topic] = {
                "skills": [],
                "tasks": [],
            }

        grouped[topic]["skills"].append(skill)

        for task in guidance["tasks"]:
            if task not in grouped[topic]["tasks"]:
                grouped[topic]["tasks"].append(task)

    # Always include practical work and career preparation.
    stages = []
    grouped_items = list(grouped.items())

    if grouped_items:
        for index, (topic, details) in enumerate(grouped_items, start=1):
            stages.append({
                "number": index,
                "title": topic,
                "duration": "Learn and practise",
                "skills": details["skills"],
                "tasks": details["tasks"],
                "project": "",
                "milestone": (
                    "Complete the exercises and explain the concept "
                    "in your own words."
                ),
                "completed": False,
            })
    else:
        stages.append({
            "number": 1,
            "title": "Strengthen career fundamentals",
            "duration": "Start here",
            "skills": [],
            "tasks": [
                f"Review the essential skills for {role}.",
                "Practise one beginner exercise for each unfamiliar topic.",
            ],
            "project": "",
            "milestone": "Identify the skills you can demonstrate independently.",
            "completed": False,
        })

    stages.append({
        "number": len(stages) + 1,
        "title": "Build a portfolio project",
        "duration": "After the learning stages",
        "skills": [],
        "tasks": [
            "Break the project into small milestones.",
            "Build, test and document the project.",
            "Publish the work in a portfolio or GitHub repository when appropriate.",
        ],
        "project": _project_for_role(role),
        "milestone": "Finish a working project and explain the decisions you made.",
        "completed": False,
    })

    stages.append({
        "number": len(stages) + 1,
        "title": "Review and prepare for opportunities",
        "duration": "Final stage",
        "skills": [],
        "tasks": [
            "Practise interview questions relevant to the target career.",
            "Update your resume to describe relevant skills and project outcomes.",
            "Review job descriptions and identify any remaining gaps.",
        ],
        "project": "",
        "milestone": "Be able to explain your skills and demonstrate your project.",
        "completed": False,
    })

    # Assign a simple suggested week range across the stages.
    total_weeks = max(1, int(weeks))
    stage_count = len(stages)

    for index, stage in enumerate(stages):
        start_week = min(total_weeks, index + 1)
        end_week = min(
            total_weeks,
            max(start_week, round((index + 1) * total_weeks / stage_count)),
        )
        stage["duration"] = (
            f"Week {start_week}"
            if start_week == end_week
            else f"Weeks {start_week}-{end_week}"
        )

    coverage = analysis.get("skill_match_percentage", None)

    return {
        "role": role,
        "current_skills": current_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_percentage": coverage,
        "stages": stages,
        "total_stages": len(stages),
        "estimated_weeks": total_weeks,
        "project_suggestion": _project_for_role(role),
        "has_skill_gaps": bool(missing_skills),
    }
