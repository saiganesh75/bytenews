from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserPreference
from news.models import Category


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserPreferenceForm(forms.ModelForm):
    preferred_category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2 form-control',
            'data-placeholder': 'Select your preferred categories'
        }),
        required=False,
        label="Preferred Categories"
    )

    class Meta:
        model = UserPreference
        fields = ['preferred_category']
