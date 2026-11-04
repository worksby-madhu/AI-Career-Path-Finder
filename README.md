

# AI Career Path Finder

**Discover suitable career paths, identify skill gaps, and plan your next steps.**

AI Career Path Finder is a Django-based career recommendation web application designed to help freshers explore career opportunities based on their skills, education, experience, and interests.

The system analyzes a user's profile, compares it with career-role requirements, and provides career matches, skill-gap insights, target-career analysis, and learning roadmaps.

## Project Overview

Choosing a career path can be challenging for freshers who are unsure which roles match their current skills or what they should learn next.

AI Career Path Finder helps users:

- Explore career roles suited to their profile
- Analyze their suitability for a target career
- Understand their skill match percentage
- Identify existing and missing skills
- Discover skills that need improvement
- Explore learning roadmaps for career development

## Features

### Resume-Based Career Analysis
- Upload a PDF or DOCX resume
- Extract resume text and identify relevant skills
- Generate career recommendations based on the extracted profile

### Interest-Based Career Exploration
- Enter skills, education, experience, and career interests
- Explore career roles based on profile information
- Search for career interests and target roles using suggestions

### Career Matching and Skill-Gap Analysis
- Compare user skills with career-role requirements
- View career match percentages
- Identify matched and missing skills
- Analyze the requirements of a selected target career

### Learning Roadmaps
- Generate learning roadmaps for career development
- Organize learning tasks into stages
- Track roadmap progress

### Profiles and Saved Analyses
- Create and manage career profiles
- Save career analyses
- Review previous analysis history
- Continue working toward career goals

### Career Comparison
- Compare career roles
- Review required skills and skill gaps
- Explore roadmaps for selected career roles

## Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Web Framework | Django |
| Frontend | HTML, CSS, JavaScript |
| Data Storage | SQLite, JSON |
| Resume Processing | PDF and DOCX parsing |
| Career Data | Role and skill datasets, including ESCO-derived data |
| Development Tools | Git, GitHub, Visual Studio Code |

## Project Structure

```text
AI-Career-Path-Finder/
│
├── career_web/                   # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── careers/                      # Main Django application
│   ├── migrations/               # Database migrations
│   ├── static/
│   │   └── careers/              # CSS and JavaScript assets
│   ├── templates/
│   │   └── careers/              # Application HTML templates
│   ├── templatetags/             # Custom Django template tags
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── roadmap_generator.py      # Learning roadmap generation
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── data/                         # Career and skill datasets
│   ├── roles.json
│   ├── career_skills.json
│   └── processed/
│       └── role_skill_data.json
│
├── tests/                        # Project tests
│   └── test_core_logic.py
│
├── esco_loader.py                # Career data loading utilities
├── main.py                       # Core career finder logic
├── resume_parser.py               # Resume text and skill extraction
├── role_matcher.py                # Career matching logic
├── role_matcher_updated.py        # Updated matching implementation
├── manage.py                      # Django management utility
├── requirements.txt                # Python dependencies
├── RUN_PROJECT.bat                 # Windows launch helper
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- Visual Studio Code (recommended)

### Installation on Windows

1. Clone the repository:

   ```powershell
   git clone https://github.com/worksby-madhu/AI-Career-Path-Finder.git
   ```

2. Open the project folder containing `manage.py` in VS Code.

3. Open **Terminal → New Terminal**.

4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   .\.venv\Scripts\Activate.ps1
   ```

5. Install the dependencies:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

6. Check the Django project and apply database migrations:

   ```powershell
   python manage.py check
   python manage.py migrate
   ```

7. Start the development server:

   ```powershell
   python manage.py runserver
   ```

8. Open the application:

   **http://127.0.0.1:8000/**

Keep the terminal open while using the application. Press `Ctrl + C` to stop the server.

### Using a Different Port

If port 8000 is already in use:

```powershell
python manage.py runserver 8003
```

Then open **http://127.0.0.1:8003/**.

## How It Works

1. The user uploads a resume or enters profile details manually.
2. The system extracts or receives the user's skills and career interests.
3. Career matching logic compares the profile with role requirements.
4. The application displays career recommendations and skill-gap insights.
5. The user can analyze a target career, compare roles, and explore learning roadmaps.
6. Saved profiles and analyses allow users to revisit their career planning.

## Dataset

The project uses structured career-role and skill data stored in JSON files. It also includes role and skill information derived from the **ESCO (European Skills, Competences, Qualifications and Occupations)** dataset.

These datasets support career matching, required-skill comparisons, and skill-gap analysis.

## Future Enhancements

- Improve semantic skill matching using NLP
- Expand career-role and skill coverage
- Enhance roadmap personalization
- Add career-specific interview preparation
- Improve recommendation quality using user feedback

## Limitations

- Resume parsing depends on the text available in the uploaded document.
- Scanned PDFs may not be readable because OCR is not included.
- Career recommendations depend on the coverage and quality of the role and skill dataset.
- This project is intended for local development and demonstration. Production deployment requires appropriate security and configuration changes.

## Contributing

Suggestions and improvements are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Commit with a descriptive message.
5. Submit a pull request.

## Author

**Madhu Lakshmi Subhadra**

GitHub: [worksby-madhu](https://github.com/worksby-madhu)

---

*AI Career Path Finder — Helping freshers turn their skills into a career plan.*

