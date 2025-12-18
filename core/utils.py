def generate_exercise_plan(age, cigarettes, craving):
    if cigarettes > 20 or craving >= 8:
        return "High craving detected. Do a 15-minute brisk walk or light jog immediately."
    elif cigarettes > 10:
        return "Moderate smoker. Aim for a 30-minute walk or cycling session today."
    else:
        return "Light smoker. Maintain activity with a 20-minute daily walk or stretching."
