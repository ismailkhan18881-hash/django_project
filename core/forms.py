from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['age', 'cigarettes_per_day', 'craving_level']
from .models import ProgressLog

class ProgressLogForm(forms.ModelForm):
    class Meta:
        model = ProgressLog
        fields = ['cigarettes_smoked']
