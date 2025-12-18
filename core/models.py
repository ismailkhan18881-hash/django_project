from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    cigarettes_per_day = models.IntegerField()
    craving_level = models.IntegerField(help_text="1–10 scale")

    def __str__(self):
        return self.user.username
from django.utils import timezone

class ProgressLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    cigarettes_smoked = models.IntegerField()
    money_saved = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
