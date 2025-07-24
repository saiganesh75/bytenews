from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):  # ✅ fixed
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)
    source_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    published_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    author = models.CharField(max_length=255, default="Unknown Source")
    publication_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):  # ✅ fixed
        return self.title

    class Meta:
        ordering = ['-published_date']

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_preference_news')
    preferred_categories = models.ManyToManyField(
    Category,
    blank=True,
    related_name='preferred_by_news_users'  # Different reverse name
)

    def __str__(self):  # ✅ fixed
        return f"{self.user.username}'s preferences"

class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-timestamp']
        unique_together = ('user', 'article')
    def __str__(self):  # ✅ fixed
        return f"{self.user.username} read {self.article.title}"
