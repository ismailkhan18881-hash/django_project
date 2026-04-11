# utils.py
# This file contains the two main functions that power the exercise plan.
# calculate_score works out a number between 0 and 100 based on the user's profile and history.
# generate_exercise_plan uses that number to pick the right exercises for the user.
# I kept these separate from views.py so the logic is easy to find and test on its own.

from datetime import date, timedelta


def calculate_score(profile, all_logs):
    # This function takes the user's profile answers and their log history
    # and returns two things: a score out of 100 and a trend direction string
    # The score decides which exercise tier the user gets placed in
    # The trend tells us if their cravings are getting better or worse over time

    # Step 1 - start everyone at 50
    # I picked 50 as the baseline because it sits right in the middle
    # This means medical conditions have room to push the score down
    # and positive factors like fitness have room to push it up
    score = 50

    # Step 2 - reduce the score for medical conditions
    # These act as safety constraints - I never want to recommend
    # exercise that could be dangerous for someone with these conditions
    # The reductions are deliberately large so they actually change the tier

    # Asthma makes high intensity exercise risky so this gets a big reduction
    if getattr(profile, "has_asthma", False):
        score -= 15

    # Heart conditions need very careful exercise so this also gets a large reduction
    if getattr(profile, "has_heart_condition", False):
        score -= 15

    # Joint problems mean we need to avoid high impact exercise
    if getattr(profile, "has_joint_problems", False):
        score -= 8

    # Diabetes needs monitoring during exercise so gets a smaller reduction
    if getattr(profile, "has_diabetes", False):
        score -= 5

    # Check how breathless they get during light activity like walking upstairs
    breathlessness = getattr(profile, "breathlessness", "never")
    if breathlessness == "always":
        score -= 10  # always breathless means we keep intensity very low
    elif breathlessness == "sometimes":
        score -= 5   # sometimes breathless gets a smaller reduction

    # Injuries limit what movements are safe to do
    if getattr(profile, "has_injuries", False):
        score -= 8

    # General health gives us an overall picture of how the user is doing
    general_health = getattr(profile, "general_health", "good")
    if general_health == "poor":
        score -= 10    # poor health means we go very gentle
    elif general_health == "fair":
        score -= 5     # fair health gets a smaller reduction
    elif general_health == "excellent":
        score += 5     # excellent health gets a small boost

    # Step 3 - increase the score for positive factors
    # These show the user is capable of handling more intense exercise

    # Fitness level tells us how much exertion they can handle
    fitness = getattr(profile, "fitness_level", "low")
    if fitness == "high":
        score += 10    # high fitness gets the biggest boost
    elif fitness == "moderate":
        score += 5     # moderate fitness gets a medium boost
    elif fitness == "very_low":
        score -= 5     # very low fitness means we ease off

    # Physical abilities - each activity they can do shows more capability
    if getattr(profile, "can_run", False):
        score += 8     # running ability is a strong positive signal
    if getattr(profile, "can_swim", False):
        score += 5     # swimming is good but less common so smaller boost
    if getattr(profile, "can_cycle", False):
        score += 5     # cycling gets the same as swimming

    # How much time they have available affects how long the exercises can be
    time_available = getattr(profile, "time_available", "10_to_20")
    if time_available == "30_plus":
        score += 8     # lots of time available means we can push harder
    elif time_available == "20_to_30":
        score += 4     # decent amount of time gets a medium boost
    elif time_available == "less_10":
        score -= 5     # less than 10 minutes means we keep things short

    # Lifestyle tells us how active they already are day to day
    lifestyle = getattr(profile, "lifestyle", "mixed")
    if lifestyle == "active":
        score += 8     # physically active job means they are used to moving
    elif lifestyle == "feet":
        score += 4     # mostly on feet gets a smaller boost
    elif lifestyle == "sitting":
        score -= 3     # mostly sitting means we start gentle to build the habit

    # Motivation level affects how hard we push them
    motivation = getattr(profile, "motivation_level", "medium")
    if motivation == "very_high":
        score += 10    # very motivated users can handle a harder plan
    elif motivation == "high":
        score += 6     # high motivation gets a good boost
    elif motivation == "low":
        score -= 5     # low motivation means easier plan to build the habit slowly

    # Emotional state from question 15 affects tone and intensity
    feeling = getattr(profile, "starting_feeling", "confident")
    if feeling == "excited":
        score += 5     # excited users are ready to push hard
    elif feeling == "nervous":
        score -= 3     # nervous users need a gentler start
    elif feeling == "worried":
        score -= 2     # worried users get a small reduction

    # Step 4 - adjust the score based on the user's log history
    # This is the adaptive part of the algorithm
    # Instead of just looking at where the user is right now
    # I compare the last 3 days against the 3 days before that
    # This tells me whether things are getting better or worse over time

    if all_logs and all_logs.count() >= 1:

        # Convert the queryset to a list ordered by newest first
        all_logs_list = list(all_logs.order_by("-date"))

        # I need at least 6 logs to compare two 3-day windows
        # If there are fewer I fall back to a simpler check
        if len(all_logs_list) >= 6:

            # Get the 3 most recent log entries
            recent_3 = all_logs_list[:3]

            # Get the 3 entries before those
            previous_3 = all_logs_list[3:6]

            # Work out the average craving for each group
            recent_avg = sum(log.craving_level for log in recent_3) / 3
            previous_avg = sum(log.craving_level for log in previous_3) / 3

            # Compare the two averages to find out which direction things are going
            # I use a threshold of 1 point to avoid reacting to tiny fluctuations
            if recent_avg > previous_avg + 1:
                # Cravings are getting noticeably worse so ease off the plan
                trend = "worsening"
                score -= 8
            elif recent_avg < previous_avg - 1:
                # Cravings are getting noticeably better so push a bit harder
                trend = "improving"
                score += 8
            else:
                # Cravings are roughly the same so make a small adjustment
                trend = "stable"
                if recent_avg >= 7:
                    score -= 3   # still high but stable so ease off slightly
                elif recent_avg <= 3:
                    score += 3   # low and stable so push slightly harder

        else:
            # Not enough logs for full trend detection yet
            # Fall back to a simple check of the most recent entries
            trend = "stable"
            recent_logs = all_logs_list[:3]
            avg_craving = sum(
                log.craving_level for log in recent_logs
            ) / len(recent_logs)

            if avg_craving >= 7:
                score -= 5   # high craving so ease off
            elif avg_craving <= 3:
                score += 5   # low craving so push harder

        # Give bonus points for a smoke free streak
        # The longer the streak the bigger the reward
        days_smoke_free = 0
        check_date = date.today()
        log_dict = {log.date: log for log in all_logs_list}

        for _ in range(365):
            if check_date in log_dict:
                if log_dict[check_date].cigarettes_smoked == 0:
                    days_smoke_free += 1          # add a day to the streak
                    check_date -= timedelta(days=1)  # go back one day
                else:
                    break   # streak broken so stop counting
            else:
                break       # no log for that day so streak ended

        # Bigger streaks get bigger bonuses to reward long term progress
        if days_smoke_free >= 30:
            score += 15    # one month smoke free gets the biggest reward
        elif days_smoke_free >= 14:
            score += 10    # two weeks gets a good reward
        elif days_smoke_free >= 7:
            score += 5     # one week gets a smaller reward

        # Give a small bonus for logging consistently every day for a week
        # This rewards engagement with the app
        if len(all_logs_list) >= 7:
            recent_7 = all_logs_list[:7]
            dates = [log.date for log in recent_7]
            expected = [date.today() - timedelta(days=i) for i in range(7)]
            if sorted(dates, reverse=True) == expected:
                score += 5   # logged every day for 7 days

    else:
        # No logs at all yet so set trend to stable as a default
        trend = "stable"

    # Step 5 - make sure the score never goes below 0 or above 100
    score = max(0, min(100, score))

    # Return both the score and the trend direction
    # The trend is used on the plan page to show the user which way things are going
    return score, trend


def generate_exercise_plan(cigarettes, craving, profile, score):
    # This function takes the score from calculate_score and the user's profile
    # and returns a list of exercises that are safe and appropriate for them
    # Each exercise in the list is a dictionary with all the info needed to display it

    # Step 1 - decide which tier the score puts the user in
    # I split into three tiers based on the score ranges
    if score >= 70:
        tier = "active"      # high score means they can handle harder exercise
    elif score >= 40:
        tier = "moderate"    # middle score means a balanced plan
    else:
        tier = "gentle"      # low score means we keep it safe and easy

    # Step 2 - work out the maximum exercise duration they have time for
    # This makes sure we never recommend a 30 minute exercise to someone
    # who only has 10 minutes available
    time_available = getattr(profile, "time_available", "10_to_20")
    if time_available == "less_10":
        max_minutes = 10     # only show exercises under 10 minutes
    elif time_available == "10_to_20":
        max_minutes = 20     # only show exercises under 20 minutes
    elif time_available == "20_to_30":
        max_minutes = 30     # only show exercises under 30 minutes
    else:
        max_minutes = 999    # 30 plus means no time limit

    # Step 3 - the full library of exercises the system knows about
    # Each exercise has all the information needed to display it
    # and flags that tell the filter which users it is safe for
    all_exercises = {

        "morning_walk": {
            "name":            "Gentle Morning Walk",
            "duration":        "15 minutes",
            "duration_mins":   15,
            "intensity":       "Low",
            "intensity_class": "low",           # used for the badge colour in CSS
            "icon":            "🚶",
            "reason":          "Low impact and gentle on joints, suitable for all fitness levels.",
            "tiers":           ["gentle", "moderate", "active"],  # available in all tiers
            "requires_run":    False,
            "requires_swim":   False,
            "requires_cycle":  False,
            "asthma_safe":     True,
            "heart_safe":      True,
            "joint_safe":      True,
        },

        "breathing": {
            "name":            "Deep Breathing Exercise",
            "duration":        "5 minutes",
            "duration_mins":   5,
            "intensity":       "Very Low",
            "intensity_class": "verylow",
            "icon":            "🧘",
            "reason":          "Controlled breathing reduces cravings and is completely safe for asthma.",
            "tiers":           ["gentle", "moderate", "active"],
            "requires_run":    False,
            "requires_swim":   False,
            "requires_cycle":  False,
            "asthma_safe":     True,
            "heart_safe":      True,
            "joint_safe":      True,
        },

        "stretching": {
            "name":            "Light Stretching Routine",
            "duration":        "10 minutes",
            "duration_mins":   10,
            "intensity":       "Low",
            "intensity_class": "low",
            "icon":            "🤸",
            "reason":          "Improves flexibility and reduces stress, safe for all fitness levels.",
            "tiers":           ["gentle", "moderate", "active"],
            "requires_run":    False,
            "requires_swim":   False,
            "requires_cycle":  False,
            "asthma_safe":     True,
            "heart_safe":      True,
            "joint_safe":      True,
        },

        "seated_arms": {
            "name":            "Seated Arm Exercises",
            "duration":        "8 minutes",
            "duration_mins":   8,
            "intensity":       "Low",
            "intensity_class": "low",
            "icon":            "💪",
            "reason":          "Low impact upper body activity with no strain on joints or breathing.",
            "tiers":           ["gentle"],       # only shown in gentle tier
            "requires_run":    False,
            "requires_swim":   False,
            "requires_cycle":  False,
            "asthma_safe":     True,
            "heart_safe":      True,
            "joint_safe":      True,
        },

        "brisk_walk": {
            "name":            "Brisk Walk",
            "duration":        "30 minutes",
            "duration_mins":   30,
            "intensity":       "Moderate",
            "intensity_class": "moderate",
            "icon":            "🚶‍♂️",
            "reason":          "Boosts cardiovascular health and is a proven craving distraction.",
            "tiers":           ["moderate", "active"],
            "requires_run":    False,
            "requires_swim":   False,
            "requires_cycle":  False,
            "asthma_safe":     True,
            "heart_safe":      True,
            "joint_safe":      False,   # long walks can aggravate joint problems
        },

        "cycling": {
            "name":            "Cycling or Static Bike",
            "duration":        "20 minutes",
            "duration_mins":   20,
            "intensity":       "Moderate",
            "intensity_class": "moderate",
            "icon":            "🚴",
            "reason":          "Great cardio that supports lung recovery without high impact stress.",
            "tiers":           ["moderate", "active"],
            "requires_run":    False,
            "requires_swim":   False,
            "requires_cycle":  True,    # only shown if the user said they can cycle
            "asthma_safe":     False,   # outdoor cycling can trigger asthma
            "heart_safe":      True,
            "joint_safe":      True,
        },

        "yoga": {
            "name":            "Yoga Session",
            "duration":        "20 minutes",
            "duration_mins":   20,
            "intensity":       "Low",
            "intensity_class": "low",
            "icon":            "🧘‍♀️",
            "reason":          "Combines breathing and movement, shown to reduce nicotine cravings.",
            "tiers":           ["moderate", "active"],
            "requires_run":    False,
            "requires_swim":   False,
            "requires_cycle":  False,
            "asthma_safe":     True,
            "heart_safe":      True,
            "joint_safe":      True,
        },

        "jogging": {
            "name":            "Jogging",
            "duration":        "25 minutes",
            "duration_mins":   25,
            "intensity":       "High",
            "intensity_class": "high",
            "icon":            "🏃",
            "reason":          "High intensity cardio that accelerates lung recovery and releases endorphins.",
            "tiers":           ["active"],       # only in active tier
            "requires_run":    True,             # only if they said they can run
            "requires_swim":   False,
            "requires_cycle":  False,
            "asthma_safe":     False,   # jogging is not safe for asthma
            "heart_safe":      False,   # jogging is not safe for heart conditions
            "joint_safe":      False,   # jogging is hard on joints
        },

        "swimming": {
            "name":            "Swimming",
            "duration":        "30 minutes",
            "duration_mins":   30,
            "intensity":       "Moderate",
            "intensity_class": "moderate",
            "icon":            "🏊",
            "reason":          "Full body workout that is easy on joints and great for lung capacity.",
            "tiers":           ["moderate", "active"],
            "requires_run":    False,
            "requires_swim":   True,    # only if they said they can swim
            "requires_cycle":  False,
            "asthma_safe":     True,
            "heart_safe":      True,
            "joint_safe":      True,
        },
    }

    # Step 4 - filter the exercise library
    # Go through each exercise and remove ones the user cannot do
    # or that are not safe for their health conditions

    # Get the user's abilities and conditions from their profile
    can_run    = getattr(profile, "can_run",             False)
    can_swim   = getattr(profile, "can_swim",            False)
    can_cycle  = getattr(profile, "can_cycle",           False)
    has_asthma = getattr(profile, "has_asthma",          False)
    has_heart  = getattr(profile, "has_heart_condition", False)
    has_joints = getattr(profile, "has_joint_problems",  False)

    selected = []   # this will hold the exercises we keep

    for key, ex in all_exercises.items():

        # Skip this exercise if it is not in the user's tier
        if tier not in ex["tiers"]:
            continue

        # Skip if the exercise needs running and they said they cannot run
        if ex["requires_run"] and not can_run:
            continue

        # Skip if the exercise needs swimming and they said they cannot swim
        if ex["requires_swim"] and not can_swim:
            continue

        # Skip if the exercise needs cycling and they said they cannot cycle
        if ex["requires_cycle"] and not can_cycle:
            continue

        # Skip if the user has asthma and this exercise is not asthma safe
        if has_asthma and not ex["asthma_safe"]:
            continue

        # Skip if the user has a heart condition and this exercise is not heart safe
        if has_heart and not ex["heart_safe"]:
            continue

        # Skip if the user has joint problems and this exercise is hard on joints
        if has_joints and not ex["joint_safe"]:
            continue

        # Skip if the exercise takes longer than the user has available
        if ex["duration_mins"] > max_minutes:
            continue

        # If we get here the exercise passed all the checks so add it to the list
        # done is set to False as a placeholder for a future tick off feature
        selected.append({**ex, "done": False})

    # Step 5 - add a craving buster exercise if the user's craving is high
    # Research shows a short walk can reduce cravings within minutes
    # so if craving is 7 or above we always add this at the top of the list
    if craving >= 7:
        craving_buster = {
            "name":            "5-Minute Craving Buster Walk",
            "duration":        "5 minutes",
            "duration_mins":   5,
            "intensity":       "Low",
            "intensity_class": "low",
            "icon":            "🔥",
            "reason":          "Studies show a short brisk walk reduces cigarette cravings within minutes.",
            "done":            False,
        }
        selected.insert(0, craving_buster)   # add it at the top of the list

    # Step 6 - return a maximum of 5 exercises
    # This keeps the plan manageable and not overwhelming
    return selected[:5]