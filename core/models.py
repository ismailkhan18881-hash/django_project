# models.py
# This file defines the database structure for the QuitCig application.
# Django uses these classes to create the database tables automatically.
# I have three models: Profile, ProgressLog, and Achievement.
# Profile stores everything about the user from the questionnaire.
# ProgressLog stores each daily entry the user makes.
# Achievement stores which badges the user has earned.

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# MODEL: Profile
# This stores all the personal information about a user.
# It has a one-to-one relationship with Django's built in User model
# meaning every user account gets exactly one profile.
# The questionnaire answers are all stored here as individual fields.

class Profile(models.Model):

    # Link this profile to a Django user account
    # If the user account is deleted the profile gets deleted too
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Section 1: Smoking Behaviour 
    # These fields store the answers from the first four questions
    # of the questionnaire about their smoking habits

    # Q1 - how many cigarettes they smoke per day
    # Stored as a number so I can use it in calculations later
    cigarettes_per_day = models.IntegerField(null=True, blank=True)

    # Q2 - how long they have been smoking
    # I use choices so only valid options can be stored
    SMOKING_DURATION_CHOICES = [
        ("less_1",  "Less than 1 year"),
        ("1_to_5",  "1 to 5 years"),
        ("5_to_10", "5 to 10 years"),
        ("10_plus", "10 or more years"),
    ]
    smoking_duration = models.CharField(
        max_length=20,
        choices=SMOKING_DURATION_CHOICES,
        null=True, blank=True
    )

    # Q3 - when cravings hit them hardest during the day
    # Used to give timing specific advice on the dashboard
    CRAVING_TRIGGER_CHOICES = [
        ("morning", "Morning"),
        ("meals",   "After meals"),
        ("stress",  "During stress"),
        ("social",  "Social situations"),
    ]
    craving_trigger = models.CharField(
        max_length=20,
        choices=CRAVING_TRIGGER_CHOICES,
        null=True, blank=True
    )

    # Q4 - whether they have tried to quit before
    # Helps set realistic expectations in the messaging
    QUIT_ATTEMPTS_CHOICES = [
        ("never",    "Never tried"),
        ("once",     "Tried once"),
        ("multiple", "Tried multiple times"),
        ("reducing", "Currently reducing"),
    ]
    quit_attempts = models.CharField(
        max_length=20,
        choices=QUIT_ATTEMPTS_CHOICES,
        null=True, blank=True
    )

    # Section 2: Medical and Health 
    # These fields are the safety constraints in the algorithm
    # Each one is a separate boolean so I can check them individually
    # They reduce the algorithm score to keep unsafe exercises out of the plan

    # Q5 - medical conditions stored as individual true or false fields
    has_asthma          = models.BooleanField(default=False)  # asthma reduces score by 15
    has_heart_condition = models.BooleanField(default=False)  # heart condition reduces score by 15
    has_joint_problems  = models.BooleanField(default=False)  # joint problems reduces score by 8
    has_diabetes        = models.BooleanField(default=False)  # diabetes reduces score by 5

    # Q6 - whether they get breathless during light activity like stairs
    # This is a direct indicator of how much exertion they can safely handle
    BREATHLESS_CHOICES = [
        ("always",    "Yes always"),
        ("sometimes", "Sometimes"),
        ("rarely",    "Rarely"),
        ("never",     "Never"),
    ]
    breathlessness = models.CharField(
        max_length=20,
        choices=BREATHLESS_CHOICES,
        null=True, blank=True
    )

    # Q7 - whether they have injuries that limit their movement
    has_injuries = models.BooleanField(default=False)

    # Q8 - their overall general health rating
    GENERAL_HEALTH_CHOICES = [
        ("poor",      "Poor"),
        ("fair",      "Fair"),
        ("good",      "Good"),
        ("excellent", "Excellent"),
    ]
    general_health = models.CharField(
        max_length=20,
        choices=GENERAL_HEALTH_CHOICES,
        null=True, blank=True
    )

    # Section 3: Physical Ability 
    # These fields boost the algorithm score and filter which exercises appear
    # I store each activity as a separate boolean so I can check them independently

    # Q9 - which activities they can do comfortably
    can_walk  = models.BooleanField(default=True)   # walking is on by default
    can_run   = models.BooleanField(default=False)  # running is off by default
    can_swim  = models.BooleanField(default=False)  # swimming is off by default
    can_cycle = models.BooleanField(default=False)  # cycling is off by default

    # Q10 - their current fitness level
    FITNESS_CHOICES = [
        ("very_low",  "Very Low"),
        ("low",       "Low"),
        ("moderate",  "Moderate"),
        ("high",      "High"),
    ]
    fitness_level = models.CharField(
        max_length=20,
        choices=FITNESS_CHOICES,
        null=True, blank=True
    )

    # Q11 - how much time they can realistically spend exercising each day
    # This is used to filter out exercises that are too long for them
    TIME_CHOICES = [
        ("less_10",  "Less than 10 minutes"),
        ("10_to_20", "10 to 20 minutes"),
        ("20_to_30", "20 to 30 minutes"),
        ("30_plus",  "30 or more minutes"),
    ]
    time_available = models.CharField(
        max_length=20,
        choices=TIME_CHOICES,
        null=True, blank=True
    )

    # Section 4: Motivation and Lifestyle 
    # These fields affect the score and the tone of messages shown to the user

    # Q12 - open text field asking why they want to quit
    # This cannot be scored because motivation is personal
    # Instead it is stored and shown back to them as a reminder on the dashboard
    quit_reason = models.TextField(null=True, blank=True)

    # Q13 - how motivated they are to quit right now
    MOTIVATION_CHOICES = [
        ("low",       "Not very motivated"),
        ("medium",    "Somewhat motivated"),
        ("high",      "Motivated"),
        ("very_high", "Very motivated"),
    ]
    motivation_level = models.CharField(
        max_length=20,
        choices=MOTIVATION_CHOICES,
        null=True, blank=True
    )

    # Q14 - how active their daily lifestyle is
    LIFESTYLE_CHOICES = [
        ("sitting", "Mostly sitting (desk job or student)"),
        ("mixed",   "Mix of sitting and moving"),
        ("feet",    "Mostly on my feet"),
        ("active",  "Physically active job"),
    ]
    lifestyle = models.CharField(
        max_length=20,
        choices=LIFESTYLE_CHOICES,
        null=True, blank=True
    )

    # Q15 - how they are feeling about starting the journey
    # This controls the tone of motivational messages shown to them
    # Nervous users get softer messages, excited users get more energetic ones
    FEELING_CHOICES = [
        ("nervous",   "Nervous or Unsure"),
        ("worried",   "Ready but worried"),
        ("confident", "Confident"),
        ("excited",   "Very excited"),
    ]
    starting_feeling = models.CharField(
        max_length=20,
        choices=FEELING_CHOICES,
        null=True, blank=True
    )

    # This tracks whether the user has completed the questionnaire
    # Every view checks this and redirects to the questionnaire if it is False
    questionnaire_done = models.BooleanField(default=False)

    # Keep the age field from the original version so no data is lost
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        # This is what shows up in the Django admin panel for this profile
        return f"{self.user.username} profile"


# MODEL: ProgressLog
# Stores each daily entry the user makes.
# One entry per day although technically multiple are allowed.
# I always use the most recent one for calculations.

class ProgressLog(models.Model):

    # Link this log entry to a user account
    # ForeignKey means one user can have many log entries
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The date of this entry defaults to today automatically
    date = models.DateField(default=timezone.now)

    # How many cigarettes they smoked today
    cigarettes_smoked = models.IntegerField(default=0)

    # Their craving level on a scale of 0 to 10
    craving_level = models.IntegerField(default=0)

    # Optional notes they want to add about how they are feeling
    notes = models.TextField(blank=True)

    # How much money they saved today compared to their usual amount
    # This is calculated automatically in the log_progress view when they save
    money_saved = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        # Shows username and date in the Django admin panel
        return f"{self.user.username} - {self.date}"

# MODEL: Achievement
# Stores which badges the user has earned.
# Badges are checked and awarded automatically
# every time the dashboard loads in views.py.
# The unique_together constraint makes sure
# a user can only earn each badge once.

class Achievement(models.Model):

    # All the possible badge names in the system
    BADGE_CHOICES = [
        ("first_step",   "First Step"),    # completed the questionnaire
        ("logger",       "Logger"),        # logged 3 days in a row
        ("on_fire",      "On Fire"),       # 7 days smoke free
        ("two_weeks",    "Two Weeks"),     # 14 days smoke free
        ("one_month",    "One Month"),     # 30 days smoke free
        ("money_saver",  "Money Saver"),   # saved at least 10 pounds
        ("calm_mind",    "Calm Mind"),     # 3 days with craving under 3
        ("dedicated",    "Dedicated"),     # logged every day for a week
    ]

    # Which user earned this badge
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Which badge they earned from the list above
    badge = models.CharField(max_length=30, choices=BADGE_CHOICES)

    # When they earned it - fills in automatically with the current date and time
    earned_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This prevents the same badge being awarded to the same user twice
        # If you try to create a duplicate it just returns the existing one
        unique_together = ("user", "badge")

    def __str__(self):
        # Shows username and badge name in the Django admin panel
        return f"{self.user.username} - {self.badge}"