
import json
import hashlib
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import CareerProfile, CareerAnalysis

from resume_parser import (
    extract_education_from_text,
    extract_experience_from_text,
    extract_projects_from_text,
    extract_certifications_from_text,
    parse_uploaded_resume,
)

from role_matcher import (
    find_resume_matching_roles,
    find_interest_matching_roles,
    search_target_roles,
    analyze_target_role,
)

from .roadmap_generator import generate_learning_roadmap


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "processed" / "role_skill_data.json"

MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}


def load_roles():
    """Load occupation data from the project's JSON file."""
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _stable_task_id(role, stage, task):
    """Stable identifier based on role, stage title, and task text."""
    raw = f"{role}|{stage.get('title', '')}|{task}".casefold()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _decorate_roadmap(roadmap, allowed_tasks):
    """Attach stable task IDs while retaining the original task strings."""
    role = str(roadmap.get("role", ""))
    for stage in roadmap.get("stages", []):
        stage["task_ids"] = []
        for task in stage.get("tasks", []):
            task_id = _stable_task_id(role, stage, task)
            stage["task_ids"].append(task_id)
            allowed_tasks[task_id] = role
    return roadmap


def render_input_error(request, message):
    """Return the input form with a validation message."""
    return render(
        request,
        "careers/skills_input.html",
        {"error": message},
        status=400,
    )


def home(request):
    """Handle the form and generate career recommendations."""

    if request.method != "POST":
        selected_profile=None
        if request.user.is_authenticated and request.GET.get("profile_id"):
            selected_profile=CareerProfile.objects.filter(pk=request.GET.get("profile_id"),user=request.user).first()
        return render(request, "careers/skills_input.html", {"selected_profile":selected_profile})

    resume_file = request.FILES.get("resume")

    resume_text = ""
    resume_skills = []
    parsed_education = ""
    parsed_experience = None
    parsed_projects = ""
    parsed_certifications = ""

    # --------------------------------------------------
    # 1. PROCESS THE UPLOADED RESUME
    # --------------------------------------------------

    if resume_file:
        extension = Path(resume_file.name).suffix.lower()

        if extension not in ALLOWED_RESUME_EXTENSIONS:
            return render_input_error(
                request,
                "Please upload a PDF or DOCX resume.",
            )

        if resume_file.size > MAX_RESUME_SIZE:
            return render_input_error(
                request,
                "Resume file is too large. Maximum allowed size is 5 MB.",
            )

        try:
            header = resume_file.read(8)
            resume_file.seek(0)

            if extension == ".pdf" and not header.startswith(b"%PDF-"):
                return render_input_error(
                    request,
                    "The selected file does not appear to be a valid PDF.",
                )

            if extension == ".docx" and not header.startswith(b"PK"):
                return render_input_error(
                    request,
                    "The selected file does not appear to be a valid DOCX document.",
                )

            parsed = parse_uploaded_resume(
                resume_file,
                extension=extension,
            )

            resume_text = parsed["text"]
            resume_skills = parsed["skills"]

            parsed_education = extract_education_from_text(resume_text)

            parsed_experience = extract_experience_from_text(resume_text)
            parsed_projects = extract_projects_from_text(resume_text)
            parsed_certifications = extract_certifications_from_text(resume_text)

        except ValueError as exc:
            return render_input_error(request, str(exc))

    # --------------------------------------------------
    # 2. READ MANUALLY SELECTED SKILLS
    # --------------------------------------------------

    try:
        manual_skills = json.loads(
            request.POST.get("skills", "[]")
        )

    except (json.JSONDecodeError, TypeError):
        return render_input_error(
            request,
            "Invalid skills data. Please select your skills again.",
        )

    if not isinstance(manual_skills, list) or not all(
        isinstance(skill, str) for skill in manual_skills
    ):
        return render_input_error(
            request,
            "Please submit a valid list of skills.",
        )

    manual_skills = [
        skill.strip()
        for skill in manual_skills
        if skill.strip()
    ]

    # Combine resume skills and manually selected skills.
    # Remove duplicates without changing their original order.

    user_skills = []
    seen_skills = set()

    for skill in resume_skills + manual_skills:
        cleaned_skill = skill.strip()
        key = cleaned_skill.casefold()

        if cleaned_skill and key not in seen_skills:
            seen_skills.add(key)
            user_skills.append(cleaned_skill)

    if not user_skills:
        message = (
            "We couldn't identify any supported skills in that resume. "
            "Add skills manually below, or upload a text-based PDF/DOCX "
            "that lists your technical skills."
            if resume_file
            else "Please upload a resume or select/add at least one skill."
        )

        return render_input_error(request, message)

    # --------------------------------------------------
    # 3. EDUCATION AND EXPERIENCE
    # --------------------------------------------------

    education = (
        request.POST.get("education", "").strip()
        or parsed_education
        or "Not provided"
    )

    experience = request.POST.get("experience", "").strip()

    if experience == "":
        experience_years = (
            parsed_experience
            if parsed_experience is not None
            else 0.0
        )

    else:
        try:
            experience_years = float(experience)

            if not 0 <= experience_years <= 60:
                raise ValueError

        except ValueError:
            return render_input_error(
                request,
                "Enter a valid experience value between 0 and 60.",
            )

    # --------------------------------------------------
    # 4. READ INTERESTS AND TARGET CAREER
    # --------------------------------------------------

    interests_text = request.POST.get("interests", "").strip()

    target_career = request.POST.get("target_career", "").strip()
    profile_name = request.POST.get("profile_name", "").strip()

    interests = [
        item.strip()
        for item in interests_text.split(",")
        if item.strip()
    ]

    # --------------------------------------------------
    # 5. GENERATE CAREER RECOMMENDATIONS
    # --------------------------------------------------

    try:
        roles = load_roles()

        # Stable task IDs are also used to validate progress updates.
        allowed_tasks = {}

        # Section 1: Careers ranked by resume skills.
        resume_recommendations = find_resume_matching_roles(
            user_skills,
            roles,
            top_n=10,
        )

        # Attach a role-specific roadmap to every recommended career.
        for item in resume_recommendations:
            item["roadmap"] = generate_learning_roadmap(
                target_role=item["role"], user_skills=user_skills,
                target_analysis=item, weeks=8,
            )
            _decorate_roadmap(item["roadmap"], allowed_tasks)

        # Section 2: Careers relevant to selected interests.
        interest_recommendations = find_interest_matching_roles(
            interests,
            roles,
            user_skills=user_skills,
            top_n=10,
        )
        interest_fallback = False
        if interests and not interest_recommendations and resume_recommendations:
            # Show grounded skill-based alternatives rather than an empty section.
            interest_recommendations = [dict(item) for item in resume_recommendations[:5]]
            interest_fallback = True

        for item in interest_recommendations:
            item["roadmap"] = generate_learning_roadmap(
                target_role=item["role"], user_skills=user_skills,
                target_analysis=item, weeks=8,
            )
            _decorate_roadmap(item["roadmap"], allowed_tasks)

        # Section 3: Analyze the user's selected target career.
        target_analysis = None
        target_options = []

        if target_career:
            target_options = search_target_roles(
                target_career,
                roles,
                limit=10,
            )

            if target_options:
                selected = target_options[0]

                target_analysis = analyze_target_role(
                    user_skills,
                    selected["role"],
                    roles[selected["role"]],
                )

        # --------------------------------------------------
        # 6. GENERATE THE PERSONALIZED LEARNING ROADMAP
        # --------------------------------------------------

        # Use the selected target career first.
        roadmap_role = target_career
        roadmap_analysis = target_analysis

        # If no target career was entered, use the top resume match.
        if not roadmap_role and resume_recommendations:
            roadmap_role = resume_recommendations[0]["role"]
            roadmap_analysis = resume_recommendations[0]

        roadmap = generate_learning_roadmap(
            target_role=roadmap_role,
            user_skills=user_skills,
            target_analysis=roadmap_analysis,
            weeks=8,
        )
        _decorate_roadmap(roadmap, allowed_tasks)
        request.session["allowed_roadmap_tasks"] = allowed_tasks

        # --------------------------------------------------
        # 7. SEND DATA TO THE RESULTS TEMPLATE
        # --------------------------------------------------

        progress = request.session.get("roadmap_progress", {})
        context = {
            "roadmap_progress": progress,
            "roadmap_progress_json": json.dumps(progress),
            "name": request.POST.get("name", "").strip(),
            "education": education,
            "experience": experience_years,
            "projects": request.POST.get("projects", "").strip() or parsed_projects,
            "certifications": request.POST.get("certifications", "").strip() or parsed_certifications,
            "interests": interests,
            "user_skills": user_skills,
            "resume_filename": (
                resume_file.name if resume_file else ""
            ),
            "input_source": (
                "resume and manual skills"
                if resume_file and manual_skills
                else "resume"
                if resume_file
                else "manual skills"
            ),

            # Separate recommendation lists.
            "resume_recommendations": resume_recommendations,
            "interest_recommendations": interest_recommendations,
            "interest_fallback": interest_fallback,

            # Target career details.
            "target_career": target_career,
            "target_analysis": target_analysis,
            "target_options": target_options,

            # Personalized learning roadmap.
            "roadmap": roadmap,
        }

        # Persist named profiles and immutable analysis snapshots for authenticated users.
        if request.user.is_authenticated:
            profile_id = request.POST.get("profile_id", "").strip()
            if profile_id:
                profile = get_object_or_404(CareerProfile, pk=profile_id, user=request.user)
            else:
                profile = CareerProfile(user=request.user, name=(profile_name or target_career or "Career Profile")[:120])
            profile.extracted_skills = user_skills
            profile.interests = interests
            profile.target_career = target_career or roadmap_role
            profile.education = education
            profile.experience_years = experience_years
            profile.projects = context["projects"]
            profile.certifications = context["certifications"]
            if resume_file:
                resume_file.seek(0)
                profile.resume = resume_file
            profile.save()
            snapshot = {key: context[key] for key in ("name", "education", "experience", "projects", "certifications", "interests", "user_skills", "resume_filename", "input_source", "resume_recommendations", "interest_recommendations", "interest_fallback", "target_career", "target_analysis", "target_options", "roadmap")}
            analysis = CareerAnalysis.objects.create(profile=profile, snapshot=snapshot, roadmap_progress=progress)
            context["saved_profile"] = profile
            context["saved_analysis"] = analysis
            request.session["current_analysis_id"] = analysis.pk

        return render(request, "careers/results.html", context)

    except (FileNotFoundError, json.JSONDecodeError):
        return render_input_error(
            request,
            "Career data could not be loaded. "
            "Check data/processed/role_skill_data.json.",
        )


@require_POST
def toggle_task(request):
    """Persist roadmap task completion in the anonymous Django session."""
    try:
        payload = json.loads(request.body.decode("utf-8"))
        career = str(payload.get("career", ""))[:180]
        task_id = str(payload.get("task_id", ""))[:180]
        completed = payload.get("completed")
        if not career or not task_id or not isinstance(completed, bool):
            return JsonResponse({"ok": False, "error": "Invalid task update."}, status=400)
        progress = request.session.get("roadmap_progress", {})
        allowed_tasks = request.session.get("allowed_roadmap_tasks", {})
        if not isinstance(allowed_tasks, dict) or task_id not in allowed_tasks:
            return JsonResponse({"ok": False, "error": "Unknown roadmap task."}, status=400)
        if allowed_tasks.get(task_id) != career:
            return JsonResponse({"ok": False, "error": "Task does not belong to this career."}, status=400)
        career_progress = progress.get(career, {})
        if not isinstance(career_progress, dict):
            career_progress = {}
        if completed:
            career_progress[task_id] = True
        else:
            career_progress.pop(task_id, None)
        progress[career] = career_progress
        request.session["roadmap_progress"] = progress
        current_id=request.session.get("current_analysis_id")
        if request.user.is_authenticated and current_id:
            saved=CareerAnalysis.objects.filter(pk=current_id,profile__user=request.user).first()
            if saved:
                saved.roadmap_progress=progress; saved.save(update_fields=["roadmap_progress"])
        request.session.modified = True
        return JsonResponse({"ok": True})
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid request."}, status=400)


# Account, profile history, comparison, and PDF report views.
def register_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    if request.method == "POST":
        from django.contrib.auth.models import User
        username=request.POST.get("username","").strip(); password=request.POST.get("password","")
        if not username or len(password)<8: return render(request,"careers/register.html",{"error":"Enter a username and password with at least 8 characters."})
        if User.objects.filter(username=username).exists(): return render(request,"careers/register.html",{"error":"That username is already taken."})
        user=User.objects.create_user(username=username,password=password); login(request,user); return redirect("dashboard")
    return render(request,"careers/register.html")

def login_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    if request.method=="POST":
        user=authenticate(request,username=request.POST.get("username",""),password=request.POST.get("password",""))
        if user: login(request,user); return redirect("dashboard")
        return render(request,"careers/login.html",{"error":"Username or password is incorrect."})
    return render(request,"careers/login.html")

def logout_view(request):
    logout(request); return redirect("home")

@login_required
def dashboard(request):
    profiles=list(CareerProfile.objects.filter(user=request.user).prefetch_related("analyses").order_by("name", "-updated_at"))
    # Profiles with the same user-defined name represent one logical profile card.
    grouped={}
    for profile in profiles:
        key=profile.name.strip().casefold()
        grouped.setdefault(key, {"profile":profile,"analyses":[]})["analyses"].extend(list(profile.analyses.all()))
    profile_rows=[]
    for group in grouped.values():
        profile=group["profile"]
        analyses=sorted(group["analyses"],key=lambda a:a.created_at,reverse=True)
        latest=analyses[0] if analyses else None; done=total=0; pct=0
        if latest:
            roadmap=latest.snapshot.get("roadmap",{})
            role=roadmap.get("role",profile.target_career)
            seen=set()
            for stage in roadmap.get("stages",[]):
                for tid in stage.get("task_ids",[]):
                    if tid not in seen:
                        seen.add(tid); total+=1
                        done+=bool(latest.roadmap_progress.get(role,{}).get(tid))
            pct=round(done/total*100) if total else 0
        profile_rows.append({"profile":profile,"latest":latest,"done":done,"total":total,"pct":pct,"analysis_count":len(analyses)})
    return render(request,"careers/dashboard.html",{"profile_rows":profile_rows})

@login_required
def create_profile(request):
    if request.method=="POST":
        name=request.POST.get("name","").strip()
        if name: profile=CareerProfile.objects.create(user=request.user,name=name[:120]); return redirect("profile_edit",profile_id=profile.pk)
    return render(request,"careers/profile_form.html")

@login_required
def profile_edit(request,profile_id):
    profile=get_object_or_404(CareerProfile,pk=profile_id,user=request.user)
    if request.method=="POST":
        profile.name=request.POST.get("name",profile.name).strip()[:120] or profile.name
        profile.target_career=request.POST.get("target_career",profile.target_career).strip()
        profile.interests=[x.strip() for x in request.POST.get("interests","").split(",") if x.strip()]
        profile.save(); return redirect("dashboard")
    return render(request,"careers/profile_form.html",{"profile":profile,"role_names":sorted(load_roles().keys())})

@login_required
def profile_history(request,profile_id):
    profile=get_object_or_404(CareerProfile,pk=profile_id,user=request.user)
    related=CareerProfile.objects.filter(user=request.user,name__iexact=profile.name)
    analyses=CareerAnalysis.objects.filter(profile__in=related).select_related("profile").order_by("-created_at")
    return render(request,"careers/history.html",{"profile":profile,"analyses":analyses})

@login_required
def open_analysis(request,analysis_id):
    analysis=get_object_or_404(CareerAnalysis,pk=analysis_id,profile__user=request.user)
    context=dict(analysis.snapshot); context.update({"roadmap_progress":analysis.roadmap_progress,"roadmap_progress_json":json.dumps(analysis.roadmap_progress),"saved_profile":analysis.profile,"saved_analysis":analysis})
    # Rebuild task authorization for persisted roadmap checkboxes.
    allowed={}
    for road in [context.get("roadmap",{})]+[x.get("roadmap",{}) for x in context.get("resume_recommendations",[])]+[x.get("roadmap",{}) for x in context.get("interest_recommendations",[])]:
        _decorate_roadmap(road,allowed)
    request.session["allowed_roadmap_tasks"]=allowed
    request.session["current_analysis_id"]=analysis.pk
    request.session["roadmap_progress"]=analysis.roadmap_progress or {}
    return render(request,"careers/results.html",context)

@login_required
def compare_careers(request):
    roles=load_roles(); role_names=sorted(roles.keys()); selected=[]; profiles=CareerProfile.objects.filter(user=request.user)
    user_skills=[]; profile=None
    if request.method=="POST":
        selected=[request.POST.get("role_a",""),request.POST.get("role_b","")]
        pid=request.POST.get("profile_id","")
        if pid: profile=profiles.filter(pk=pid).first(); user_skills=profile.extracted_skills if profile else []
    comparison=[]
    for role in selected:
        if role in roles:
            analysis=analyze_target_role(user_skills,role,roles[role]); roadmap=generate_learning_roadmap(role,user_skills,analysis,weeks=8)
            comparison.append({"role":role,"analysis":analysis,"roadmap":roadmap})
    required_sets=[set(x["analysis"].get("matched_skills",[])+x["analysis"].get("missing_skills",[])) for x in comparison]
    shared=required_sets[0] & required_sets[1] if len(required_sets)==2 else set()
    return render(request,"careers/compare.html",{"roles":role_names,"comparison":comparison,"selected":selected,"profiles":profiles,"profile":profile,"shared_skills":sorted(shared)})

@login_required
def export_analysis_pdf(request,analysis_id):
    analysis=get_object_or_404(CareerAnalysis,pk=analysis_id,profile__user=request.user)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from io import BytesIO
        data=analysis.snapshot; buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=letter,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42); styles=getSampleStyleSheet(); story=[]
        story.append(Paragraph("AI Career Path Finder — Career Report",styles["Title"]))
        story.append(Paragraph(f"Profile: {analysis.profile.name}",styles["Heading2"]))
        story.append(Paragraph(f"Target career: {data.get('target_career') or analysis.profile.target_career or 'Not selected'}",styles["Heading2"]))
        story.append(Paragraph("Skill profile",styles["Heading3"]))
        story.append(Paragraph(", ".join(data.get("user_skills",[])) or "No skills recorded",styles["BodyText"]))
        target=data.get("target_analysis") or {}; story.append(Paragraph(f"Skill coverage: {target.get('skill_match_percentage','Not available')}%",styles["BodyText"]))
        story.append(Paragraph("Matched skills: "+", ".join(target.get("matched_skills",[])),styles["BodyText"]))
        story.append(Paragraph("Missing skills: "+", ".join(target.get("missing_skills",[])),styles["BodyText"]))
        story.append(Paragraph("Career recommendations",styles["Heading2"]))
        for item in data.get("resume_recommendations",[])[:10]: story.append(Paragraph(f"• {item.get('role')} — {item.get('match_percentage',item.get('score',''))}",styles["BodyText"]))
        story.append(Paragraph("Personalized roadmap",styles["Heading2"]))
        for stage in data.get("roadmap",{}).get("stages",[]):
            story.append(Paragraph(stage.get("title","Stage"),styles["Heading3"]))
            for task in stage.get("tasks",[]): story.append(Paragraph("☐ "+str(task),styles["BodyText"]))
        def footer(canvas,doc): canvas.saveState(); canvas.setFont("Helvetica",9); canvas.drawString(42,24,f"AI Career Path Finder · Page {doc.page}"); canvas.restoreState()
        doc.build(story,onFirstPage=footer,onLaterPages=footer); response=HttpResponse(buf.getvalue(),content_type="application/pdf"); response["Content-Disposition"]=f'attachment; filename="career-report-{analysis.pk}.pdf"'; return response
    except ImportError: return HttpResponse("PDF export dependency is missing. Install requirements.txt.",status=500)
