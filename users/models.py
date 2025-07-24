from django.db import models
from django.contrib.auth.models import User
from news.models import Category

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_category = models.ManyToManyField(Category)

    def __str__(self):
        return f"{self.user.username}'s Preferences"

    class Meta:
        verbose_name_plural = "User Preferences"
