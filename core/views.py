from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, ProgressLogForm
from .utils import generate_exercise_plan
from .models import Profile

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()

            plan = generate_exercise_plan(
                profile.age,
                profile.cigarettes_per_day,
                profile.craving_level
            )

            return render(request, 'plan.html', {'plan': plan})
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form})
from .models import ProgressLog
from django.utils import timezone

@login_required
def log_progress(request):
    if request.method == 'POST':
        form = ProgressLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user

            # simple money saved logic (£0.50 per cigarette avoided, example)
            log.money_saved = max(0, (20 - log.cigarettes_smoked) * 0.5)

            log.save()
            return render(request, 'progress_success.html', {'log': log})
    else:
        form = ProgressLogForm()

    return render(request, 'log_progress.html', {'form': form})
