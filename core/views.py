from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import ProfileForm, ProgressLogForm
from .utils import generate_exercise_plan
from .models import Profile, ProgressLog


@login_required
def dashboard_view(request):
    """
    Simple design-first dashboard.
    Uses real data where available, placeholders elsewhere.
    """
    profile = Profile.objects.filter(user=request.user).first()
    last_log = ProgressLog.objects.filter(user=request.user).order_by("-date", "-id").first()

    return render(request, "dashboard.html", {
        "profile": profile,
        "last_log": last_log,
    })


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile.html", {"form": form})


@login_required
def log_progress(request):
    if request.method == "POST":
        form = ProgressLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.money_saved = max(0, (20 - int(log.cigarettes_smoked)) * 0.5)
            log.save()
            return redirect("dashboard")
    else:
        form = ProgressLogForm()

    return render(request, "log_progress.html", {"form": form})


@login_required
def plan_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Must have profile basics
    if profile.age is None or profile.cigarettes_per_day is None:
        return render(request, "plan.html", {
            "plan": "Please complete your profile first.",
        })

    last_log = ProgressLog.objects.filter(user=request.user).order_by("-date", "-id").first()

    # Use latest logged values when available (more realistic)
    cigarettes_for_plan = last_log.cigarettes_smoked if last_log else profile.cigarettes_per_day
    craving_for_plan = last_log.craving_level if last_log else getattr(profile, "craving_level", None)

    # If craving is still missing for any reason, default to 0 (safe baseline)
    if craving_for_plan is None:
        craving_for_plan = 0

    plan_text = generate_exercise_plan(
        profile.age,
        int(cigarettes_for_plan),
        int(craving_for_plan)
    )

    notes = []
    if getattr(profile, "has_asthma", False):
        notes.append("Asthma considered")
    if hasattr(profile, "can_run") and not profile.can_run:
        notes.append("Running avoided")
    if hasattr(profile, "can_swim") and not profile.can_swim:
        notes.append("Swimming avoided")
    if getattr(profile, "activity_level", "") == "active":
        notes.append("Active level allows longer sessions when cravings are low")

    if notes:
        plan_text += "\n\nPersonalisation:\n- " + "\n- ".join(notes)

    return render(request, "plan.html", {"plan": plan_text})
