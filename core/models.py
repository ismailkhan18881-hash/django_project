from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    ACTIVITY_CHOICES = [
        ("sedentary", "Sedentary"),
        ("light", "Light"),
        ("moderate", "Moderate"),
        ("active", "Active"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # onboarding essentials
    age = models.IntegerField(null=True, blank=True)
    cigarettes_per_day = models.IntegerField(null=True, blank=True)

    # safety + ability questions (supervisor-relevant)
    has_asthma = models.BooleanField(default=False)
    can_run = models.BooleanField(default=True)
    can_swim = models.BooleanField(default=False)
    activity_level = models.CharField(
        max_length=10,
        choices=ACTIVITY_CHOICES,
        default="light"
    )

    
    craving_level = models.IntegerField(null=True, blank=True, help_text="0–10 scale")

    def __str__(self):
        return self.user.username


class ProgressLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    cigarettes_smoked = models.IntegerField(default=0)

   
    craving_level = models.IntegerField(default=0, help_text="0–10 scale")

   
    notes = models.TextField(blank=True)

    money_saved = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
