def get_user_profile():
    print("\n========== USER INFORMATION ==========")

    name = input("Enter your name: ")
    education = input("Enter your education: ")
    experience = input("Enter your experience: ")

    skills = input("Enter your skills (comma separated): ")
    interests = input("Enter your interests (comma separated): ")

    skills = [skill.strip().lower() for skill in skills.split(",")]
    interests = [interest.strip().lower() for interest in interests.split(",")]

    return {
        "name": name,
        "education": education,
        "experience": experience,
        "skills": skills,
        "interests": interests
    }