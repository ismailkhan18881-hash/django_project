from django import forms
from .models import Profile, ProgressLog


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "age",
            "cigarettes_per_day",

            # onboarding/safety questions (supervisor-relevant)
            "has_asthma",
            "can_run",
            "can_swim",
            "activity_level",
        ]
        widgets = {
            "age": forms.NumberInput(attrs={"min": 0}),
            "cigarettes_per_day": forms.NumberInput(attrs={"min": 0}),
        }


class ProgressLogForm(forms.ModelForm):
    class Meta:
        model = ProgressLog
        fields = [
            "cigarettes_smoked",
            "craving_level",
            "notes",
        ]
        widgets = {
            "cigarettes_smoked": forms.NumberInput(attrs={"min": 0}),
            "craving_level": forms.NumberInput(attrs={
                "type": "range",
                "min": "0",
                "max": "10",
                "step": "1",
            }),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional notes (triggers, mood, etc.)"}),
        }
