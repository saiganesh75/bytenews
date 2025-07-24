from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .forms import UserRegisterForm, UserPreferenceForm
from .models import UserPreference  # Correct import

# ✅ User Registration
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('login')  # Default auth login
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


# ✅ Logout view
def logout_view(request):
    logout(request)
    return render(request, 'logged_out.html')


# ✅ User Preferences View
@login_required
def preferences(request):
    preference, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences updated successfully!')
            return redirect('users:preferences')  # You can change this if needed
    else:
        form = UserPreferenceForm(instance=preference)

    return render(request, 'users/preferences.html', {'form': form})
