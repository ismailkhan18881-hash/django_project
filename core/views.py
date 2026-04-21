# views.py
# This file contains all the view functions for the QuitCig application.
# Each view function handles a specific page of the website.
# When a user visits a URL, Django calls the matching view function here
# which collects the data needed and passes it to the HTML template to display.
# I also have some helper functions at the top that the views share between them.

import json
from datetime import date, timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .forms import ProfileForm, ProgressLogForm, QuestionnaireForm
from .utils import generate_exercise_plan, calculate_score
from .models import Profile, ProgressLog, Achievement


# ─────────────────────────────────────────────
# HELPER FUNCTION: check_and_award_badges
# This runs every time the dashboard loads.
# It checks if the user has earned any new badges
# and saves them to the database if they have.
# I use get_or_create so a badge is never awarded twice.
# ─────────────────────────────────────────────

def check_and_award_badges(user, all_logs, days_smoke_free, total_money_saved):

    # Small inner function to award a badge without duplicating code
    # get_or_create either finds the existing badge or creates a new one
    def award(badge_name):
        Achievement.objects.get_or_create(user=user, badge=badge_name)

    # First Step badge - given when the user completes the questionnaire
    profile = Profile.objects.filter(user=user).first()
    if profile and profile.questionnaire_done:
        award("first_step")

    # Logger badge - given for logging 3 days in a row
    if all_logs.count() >= 3:
        recent = list(all_logs.order_by("-date")[:3])
        if len(recent) == 3:
            # Check the difference between each log date is exactly 1 day
            diff1 = (recent[0].date - recent[1].date).days
            diff2 = (recent[1].date - recent[2].date).days
            if diff1 == 1 and diff2 == 1:
                award("logger")

    # On Fire badge - given for 7 consecutive smoke free days
    if days_smoke_free >= 7:
        award("on_fire")

    # Two Weeks badge - given for 14 smoke free days
    if days_smoke_free >= 14:
        award("two_weeks")

    # One Month badge - given for 30 smoke free days
    if days_smoke_free >= 30:
        award("one_month")

    # Money Saver badge - given when the user has saved at least 10 pounds
    if total_money_saved >= 10:
        award("money_saver")

    # Calm Mind badge - given for 3 days in a row with craving under 3
    if all_logs.count() >= 3:
        recent_3 = list(all_logs.order_by("-date")[:3])
        # Check every log in the last 3 days has craving below 3
        if all(log.craving_level < 3 for log in recent_3):
            award("calm_mind")

    # Dedicated badge - given for logging every single day for a week
    if all_logs.count() >= 7:
        recent_7 = list(all_logs.order_by("-date")[:7])
        dates = [log.date for log in recent_7]
        # Build a list of what the last 7 dates should look like
        expected = [date.today() - timedelta(days=i) for i in range(7)]
        # If the actual dates match the expected dates the user logged every day
        if sorted(dates, reverse=True) == expected:
            award("dedicated")


# ─────────────────────────────────────────────
# HELPER FUNCTION: get_reminder_level
# Works out how many days since the user last logged
# and returns a number telling us which reminder to show.
# Returns None if the user has logged recently so no reminder is needed.
# ─────────────────────────────────────────────

def get_reminder_level(last_log):

    # If they have never logged anything we do not show a reminder yet
    if not last_log:
        return None

    # Calculate how many days have passed since their last log entry
    days_since = (date.today() - last_log.date).days

    # Return the right level based on how long they have been away
    if days_since >= 30:
        return 3    # 30 days or more gets the strongest most emotional reminder
    elif days_since >= 14:
        return 2    # 14 days gets a medium reminder
    elif days_since >= 7:
        return 1    # 7 days gets a gentle nudge
    else:
        return None  # user is active so no reminder needed


# ─────────────────────────────────────────────
# HELPER FUNCTION: get_motivational_content
# Generates a personalised motivational message for the dashboard.
# The tone depends on how the user said they felt in question 15.
# The health statistic depends on how many days smoke free they are.
# ─────────────────────────────────────────────

def get_motivational_content(days_smoke_free, profile, craving_level):

    # Get their emotional state from question 15 of the questionnaire
    # This controls whether the message is gentle and soft or energetic and pushy
    feeling = getattr(profile, "starting_feeling", "confident") if profile else "confident"

    # Pick the opening message and subtitle based on emotional state
    if feeling in ["nervous", "worried"]:
        tone_opener = "Take it one day at a time."
        tone_sub    = "Every small step is progress. You do not have to be perfect."
    elif feeling == "excited":
        tone_opener = "You are absolutely ready for this!"
        tone_sub    = "Channel that energy and let us push forward together!"
    else:
        tone_opener = "You are doing brilliantly!"
        tone_sub    = "Stay consistent and the results will follow."

    # Pick the right health statistic based on how many days smoke free they are
    # These are all based on real NHS published recovery timelines
    if days_smoke_free == 0:
        health_stat = "Within 20 minutes of your last cigarette your heart rate starts returning to normal."
    elif days_smoke_free == 1:
        health_stat = "After 24 hours smoke free your risk of heart attack already begins to decrease."
    elif days_smoke_free == 2:
        health_stat = "After 48 hours your sense of smell and taste are already starting to improve."
    elif days_smoke_free < 7:
        health_stat = f"After {days_smoke_free} days your oxygen levels are back to normal and your lungs are beginning to clear."
    elif days_smoke_free < 14:
        health_stat = "After 1 week your lung function has already improved by up to 30 percent."
    elif days_smoke_free < 30:
        health_stat = "After 2 weeks your circulation has improved and exercise is getting easier."
    elif days_smoke_free < 90:
        health_stat = "After 1 month your coughing and wheezing have significantly reduced."
    elif days_smoke_free < 180:
        health_stat = "After 3 months your lung capacity has increased by up to 10 percent."
    elif days_smoke_free < 365:
        health_stat = "After 6 months most people notice dramatically easier breathing."
    else:
        health_stat = "After 1 year your risk of heart disease has halved compared to a smoker."

    # If the user is experiencing a high craving right now add a specific tip
    craving_tip = None
    if craving_level and craving_level >= 7:
        craving_tip = "Cravings only last 3 to 5 minutes. A short walk right now can reduce craving intensity by up to 50 percent."

    # Return everything as a dictionary so the template can access each piece
    return {
        "tone_opener": tone_opener,
        "tone_sub":    tone_sub,
        "health_stat": health_stat,
        "craving_tip": craving_tip,
    }


# ─────────────────────────────────────────────
# HELPER FUNCTION: get_dashboard_stats
# Calculates all the numbers shown on the dashboard stat cards and chart.
# I put this in a separate function to keep the dashboard view clean
# and because the same calculations might be useful elsewhere later.
# ─────────────────────────────────────────────

def get_dashboard_stats(user):

    # Get all progress logs for this user ordered by date oldest first
    all_logs = ProgressLog.objects.filter(user=user).order_by("date")

    # Work out how many consecutive days they have had 0 cigarettes
    # I count backwards from today until I find a day with cigarettes or no log
    days_smoke_free = 0
    check_date = date.today()
    # Put logs in a dictionary keyed by date so I can look them up quickly
    log_dict = {log.date: log for log in all_logs}

    for _ in range(365):   # look back up to a year at most
        if check_date in log_dict:
            if log_dict[check_date].cigarettes_smoked == 0:
                days_smoke_free += 1              # this day had 0 cigarettes so add it
                check_date -= timedelta(days=1)   # go back another day
            else:
                break   # this day had cigarettes so the streak is broken
        else:
            break       # no log for this day so the streak is broken

    # Work out how many cigarettes they have avoided compared to their usual amount
    profile = Profile.objects.filter(user=user).first()
    cigarettes_avoided = 0
    if profile and profile.cigarettes_per_day:
        total_logged      = sum(log.cigarettes_smoked for log in all_logs)
        num_days          = all_logs.count()
        would_have_smoked = profile.cigarettes_per_day * num_days
        # Avoided is what they would have smoked minus what they actually smoked
        cigarettes_avoided = max(0, would_have_smoked - total_logged)

    # Add up all the money saved fields from every log entry
    total_money_saved = sum(float(log.money_saved) for log in all_logs)

    # Calculate a health score between 0 and 10 based on recent logs
    # The formula is: start at 10, subtract for cigarettes and cravings
    health_score = None
    if all_logs.exists():
        recent      = list(all_logs.order_by("-date")[:7])   # use last 7 logs
        avg_cigs    = sum(l.cigarettes_smoked for l in recent) / len(recent)
        avg_craving = sum(l.craving_level     for l in recent) / len(recent)
        raw_score   = 10 - (avg_cigs * 0.3) - (avg_craving * 0.2)
        # Clamp between 0 and 10 and round to 1 decimal place
        health_score = round(max(0, min(10, raw_score)), 1)

    # Get the last 14 logs for the progress chart
    # Django does not support negative indexing so I calculate the skip amount manually
    total      = all_logs.count()
    skip       = max(0, total - 14)
    chart_logs = list(all_logs.order_by("date")[skip:])

    # Convert the chart data to JSON so Chart.js can read it in the template
    chart_labels   = json.dumps([log.date.strftime("%d %b") for log in chart_logs])
    chart_cigs     = json.dumps([log.cigarettes_smoked      for log in chart_logs])
    chart_cravings = json.dumps([log.craving_level          for log in chart_logs])

    # Work out the next milestone and how far through it the user is
    # Milestones are at 3, 7, 14, 30, 60, 90, 180 and 365 days
    milestones     = [3, 7, 14, 30, 60, 90, 180, 365]
    next_milestone = 365   # default to 365 if they have passed all milestones
    for m in milestones:
        if days_smoke_free < m:
            next_milestone = m
            break

    # Find the milestone before the next one so I can calculate the progress percentage
    prev_milestone = 0
    for m in milestones:
        if m < next_milestone:
            prev_milestone = m

    # Calculate what percentage of the way through they are between milestones
    span          = next_milestone - prev_milestone
    progress      = days_smoke_free - prev_milestone
    milestone_pct = min(100, int((progress / span) * 100)) if span > 0 else 100
    days_until    = max(0, next_milestone - days_smoke_free)

    # Pick the right milestone message based on how close they are
    if days_until == 0:
        milestone_message = "You have hit this milestone! Keep going!"
    elif days_until == 1:
        milestone_message = "Just 1 more day to reach your next milestone! You have got this!"
    else:
        milestone_message = f"Just {days_until} more days until you reach {next_milestone} days smoke free! Fantastic work!"

    # Return everything as a dictionary so the views can pass it to the templates
    return {
        "all_logs":             all_logs,
        "days_smoke_free":      days_smoke_free,
        "cigarettes_avoided":   cigarettes_avoided,
        "total_money_saved":    round(total_money_saved, 2),
        "health_score":         health_score,
        "workouts_completed":   0,
        "chart_labels":         chart_labels,
        "chart_cigarettes":     chart_cigs,
        "chart_cravings":       chart_cravings,
        "next_milestone":       next_milestone,
        "milestone_pct":        milestone_pct,
        "days_until_milestone": days_until,
        "milestone_message":    milestone_message,
    }


# ─────────────────────────────────────────────
# VIEW: register_view
# Handles new user registration.
# Uses Django's built in UserCreationForm which enforces:
# - password must be at least 8 characters
# - password cannot be too common
# - password cannot be entirely numeric
# - both passwords must match
# If the email already exists it prompts them to log in instead.
# ─────────────────────────────────────────────

def register_view(request):

    # If they are already logged in send them straight to the dashboard
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        # Check if the email already exists before doing anything else
        email = request.POST.get("email", "").strip()
        if email and User.objects.filter(email=email).exists():
            messages.error(
                request,
                "An account with this email already exists. Please log in instead."
            )
            return render(request, "registration/register.html", {"form": form})

        if form.is_valid():
            user = form.save(commit=False)
            # Save the email they entered into the user account
            user.email = email
            user.save()
            # Log them in straight away so they go directly to the questionnaire
            login(request, user)
            messages.success(request, "Account created! Please complete your profile to get started.")
            return redirect("questionnaire")
        else:
            # Loop through all form errors and show them as messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


# ─────────────────────────────────────────────
# VIEW: questionnaire_view
# This is the first page new users see.
# It shows the 15 question form and saves the answers to the profile.
# Once completed it marks questionnaire_done as True
# so the user is never sent here again.
# ─────────────────────────────────────────────

@login_required
def questionnaire_view(request):

    # Get or create the profile for this user
    profile, created = Profile.objects.get_or_create(user=request.user)

    # If they already completed the questionnaire send them to the dashboard
    if profile.questionnaire_done:
        return redirect("dashboard")

    if request.method == "POST":
        # The user submitted the form so try to save it
        form = QuestionnaireForm(request.POST, instance=profile)
        if form.is_valid():
            questionnaire = form.save(commit=False)   # save without committing yet
            questionnaire.questionnaire_done = True   # mark it as completed
            questionnaire.save()                      # now save to the database
            messages.success(request, "Your personalised plan is ready!")
            return redirect("dashboard")
    else:
        # Just visiting the page so show the empty form
        form = QuestionnaireForm(instance=profile)

    return render(request, "questionnaire.html", {"form": form})


# ─────────────────────────────────────────────
# VIEW: dashboard_view
# This is the main page of the application.
# It pulls together all the stats, badges, exercises
# motivational content and reminder level
# and passes them all to the dashboard template.
# ─────────────────────────────────────────────

@login_required
def dashboard_view(request):

    # Check if the user has completed the questionnaire
    # If not send them there first so the algorithm has data to work with
    profile = Profile.objects.filter(user=request.user).first()
    if not profile or not profile.questionnaire_done:
        return redirect("questionnaire")

    # Get the most recent log entry to show in the quick log form
    last_log = ProgressLog.objects.filter(
        user=request.user
    ).order_by("-date", "-id").first()

    # Get all the calculated stats like days smoke free and money saved
    stats = get_dashboard_stats(request.user)

    # Check if the user has earned any new badges and award them
    check_and_award_badges(
        request.user,
        stats["all_logs"],
        stats["days_smoke_free"],
        stats["total_money_saved"]
    )

    # Get the list of badges this user has already earned
    earned_badges = Achievement.objects.filter(
        user=request.user
    ).values_list("badge", flat=True)

    # Build the complete badge list with earned status for each one
    all_badges = [
        {"key": "first_step",  "label": "First Step",  "desc": "Complete the questionnaire"},
        {"key": "logger",      "label": "Logger",       "desc": "Log 3 days in a row"},
        {"key": "on_fire",     "label": "On Fire",      "desc": "7 days smoke free"},
        {"key": "two_weeks",   "label": "Two Weeks",    "desc": "14 days smoke free"},
        {"key": "one_month",   "label": "One Month",    "desc": "30 days smoke free"},
        {"key": "money_saver", "label": "Money Saver",  "desc": "Save 10 pounds"},
        {"key": "calm_mind",   "label": "Calm Mind",    "desc": "3 days craving under 3"},
        {"key": "dedicated",   "label": "Dedicated",    "desc": "Log every day for a week"},
    ]

    # Mark each badge as earned or not based on the database results
    for badge in all_badges:
        badge["earned"] = badge["key"] in earned_badges

    # Generate today's exercise plan for the dashboard preview
    todays_exercises = []
    trend = "stable"
    if profile and profile.cigarettes_per_day:
        craving = last_log.craving_level     if last_log else 0
        cigs    = last_log.cigarettes_smoked if last_log else profile.cigarettes_per_day

        # Calculate the score and trend using the algorithm
        score, trend = calculate_score(profile, stats["all_logs"])

        # Generate the exercise list using the score
        todays_exercises = generate_exercise_plan(
            int(cigs), int(craving), profile, score
        )

    # Get the personalised motivational message for this user
    craving_now = last_log.craving_level if last_log else 0
    motivation  = get_motivational_content(
        stats["days_smoke_free"], profile, craving_now
    )

    # Check if the user needs a re-engagement reminder
    reminder_level = get_reminder_level(last_log)

    # Calculate money stats for the motivation section
    daily_cost    = (profile.cigarettes_per_day or 0) * 0.50
    yearly_saving = round(daily_cost * 365, 2)

    # Bundle everything into a context dictionary and send it to the template
    context = {
        "profile":          profile,
        "last_log":         last_log,
        "todays_exercises": todays_exercises,
        "all_badges":       all_badges,
        "reminder_level":   reminder_level,
        "motivation":       motivation,
        "daily_cost":       daily_cost,
        "yearly_saving":    yearly_saving,
        "trend":            trend,
        **stats,
    }

    return render(request, "dashboard.html", context)


# ─────────────────────────────────────────────
# VIEW: profile_view
# Lets users update their profile details
# after they have completed the questionnaire.
# ─────────────────────────────────────────────

@login_required
def profile_view(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.questionnaire_done:
        return redirect("questionnaire")

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile.html", {"form": form})


# ─────────────────────────────────────────────
# VIEW: log_progress
# The daily logging page where users record
# how many cigarettes they smoked and their craving level.
# ─────────────────────────────────────────────

@login_required
def log_progress(request):

    if request.method == "POST":
        form = ProgressLogForm(request.POST)
        if form.is_valid():
            log      = form.save(commit=False)
            log.user = request.user

            profile  = Profile.objects.filter(user=request.user).first()
            baseline = profile.cigarettes_per_day if profile and profile.cigarettes_per_day else 20
            avoided  = max(0, baseline - int(log.cigarettes_smoked))
            log.money_saved = round(avoided * 0.50, 2)

            log.save()
            messages.success(request, "Progress logged! Keep it up!")
            return redirect("dashboard")
    else:
        form = ProgressLogForm()

    recent_logs = ProgressLog.objects.filter(
        user=request.user
    ).order_by("-date", "-id")[:10]

    return render(request, "log_progress.html", {
        "form":        form,
        "recent_logs": recent_logs,
    })


# ─────────────────────────────────────────────
# VIEW: plan_view
# The exercise plan page.
# ─────────────────────────────────────────────

@login_required
def plan_view(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.questionnaire_done:
        return redirect("questionnaire")

    if profile.cigarettes_per_day is None:
        return render(request, "plan.html", {
            "exercises":    [],
            "profile":      profile,
            "last_craving": None,
            "score":        None,
            "tier":         None,
            "trend":        None,
        })

    last_log = ProgressLog.objects.filter(
        user=request.user
    ).order_by("-date", "-id").first()

    all_logs = ProgressLog.objects.filter(
        user=request.user
    ).order_by("date")

    cigs    = last_log.cigarettes_smoked if last_log else profile.cigarettes_per_day
    craving = last_log.craving_level     if last_log else 0

    score, trend = calculate_score(profile, all_logs)

    if score >= 70:
        tier = "Active"
    elif score >= 40:
        tier = "Moderate"
    else:
        tier = "Gentle"

    exercises = generate_exercise_plan(int(cigs), int(craving), profile, score)

    return render(request, "plan.html", {
        "exercises":    exercises,
        "profile":      profile,
        "last_craving": craving,
        "score":        score,
        "tier":         tier,
        "trend":        trend,
    })