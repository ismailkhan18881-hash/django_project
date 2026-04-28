# forms.py
# This file contains all the forms used in QuitCig.
# Django forms handle taking user input and validating it
# before it gets saved to the database.
# I have three forms:
# QuestionnaireForm - the big 15 question onboarding form
# ProfileForm - the shorter update form on the profile page
# ProgressLogForm - the daily logging form

from django import forms
from .models import Profile, ProgressLog



# FORM: QuestionnaireForm
# This is the main 15 question form that new users
# fill in when they first sign up.
# It maps directly to the fields on the Profile model.
# I use ModelForm so Django handles the saving automatically.

class QuestionnaireForm(forms.ModelForm):

    # Question 5 has multiple conditions in one question
    # I define them separately here as individual checkbox fields
    # so the user can tick all that apply
    has_asthma = forms.BooleanField(
        required=False,    # required=False means it is okay to leave unticked
        label="Asthma"
    )
    has_heart_condition = forms.BooleanField(
        required=False,
        label="Heart condition"
    )
    has_joint_problems = forms.BooleanField(
        required=False,
        label="Joint problems (knees or hips)"
    )
    has_diabetes = forms.BooleanField(
        required=False,
        label="Diabetes"
    )

    # Question 9 also uses checkboxes so the user can tick multiple activities
    can_walk = forms.BooleanField(
        required=False,
        label="Walking"
    )
    can_run = forms.BooleanField(
        required=False,
        label="Jogging or Running"
    )
    can_swim = forms.BooleanField(
        required=False,
        label="Swimming"
    )
    can_cycle = forms.BooleanField(
        required=False,
        label="Cycling"
    )

    class Meta:
        # Tell Django which model this form is for
        model = Profile

        # List every field that should appear in the questionnaire
        # The order here matches the order they appear on the page
        fields = [
            # Section 1 - smoking behaviour questions
            "cigarettes_per_day",
            "smoking_duration",
            "craving_trigger",
            "quit_attempts",

            # Section 2 - medical and health questions
            "has_asthma",
            "has_heart_condition",
            "has_joint_problems",
            "has_diabetes",
            "breathlessness",
            "has_injuries",
            "general_health",

            # Section 3 - physical ability questions
            "can_walk",
            "can_run",
            "can_swim",
            "can_cycle",
            "fitness_level",
            "time_available",

            # Section 4 - motivation and lifestyle questions
            "quit_reason",
            "motivation_level",
            "lifestyle",
            "starting_feeling",

            # Keep the age field from the original profile
            "age",
        ]

        # Widgets let me customise how each field looks in the HTML
        widgets = {
            # The quit reason question is open text so I use a textarea
            # I make it 3 rows tall and add a helpful placeholder
            "quit_reason": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "For example: I want to be healthier for my family..."
            }),

            # Number inputs get a minimum value of 0 so negative numbers are blocked
            "cigarettes_per_day": forms.NumberInput(attrs={"min": 0}),
            "age":                forms.NumberInput(attrs={"min": 0}),
        }


# 
# FORM: ProfileForm
# This is the shorter update form shown on the profile page.
# Users come here after completing the questionnaire
# if they want to update their details.
# It only shows the most important fields rather than all 15 questions.
# 

class ProfileForm(forms.ModelForm):

    class Meta:
        # Same model as the questionnaire form
        model = Profile

        # Only include the fields that make sense to update later
        # I leave out things like quit_reason and starting_feeling
        # because those are one time onboarding questions
        fields = [
            "age",
            "cigarettes_per_day",
            "has_asthma",
            "has_heart_condition",
            "has_joint_problems",
            "has_diabetes",
            "breathlessness",
            "has_injuries",
            "general_health",
            "can_walk",
            "can_run",
            "can_swim",
            "can_cycle",
            "fitness_level",
            "time_available",
            "motivation_level",
            "lifestyle",
        ]

        # Same widget settings as the questionnaire form
        widgets = {
            "cigarettes_per_day": forms.NumberInput(attrs={"min": 0}),
            "age":                forms.NumberInput(attrs={"min": 0}),
        }


# 
# FORM: ProgressLogForm
# This is the daily logging form used on the log progress page
# and also in the quick log section on the dashboard.
# Users fill this in every day to record how they are doing.
# 

class ProgressLogForm(forms.ModelForm):

    class Meta:
        # This form saves to the ProgressLog model
        model = ProgressLog

        # Only show these three fields to the user
        # The date and money_saved fields are filled in automatically
        fields = [
            "cigarettes_smoked",
            "craving_level",
            "notes",
        ]

        widgets = {
            # Number input for cigarettes with a minimum of 0
            "cigarettes_smoked": forms.NumberInput(attrs={"min": 0}),

            # Range input turns the craving field into a slider
            # min 0 and max 10 matches the 0 to 10 craving scale
            "craving_level": forms.NumberInput(attrs={
                "type":  "range",
                "min":   "0",
                "max":   "10",
                "step":  "1",
            }),

            # Textarea for the notes field with a helpful placeholder
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "How are you feeling today? Any triggers or things that helped?"
            }),
        }