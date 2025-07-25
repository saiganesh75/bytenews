from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model 
User = get_user_model()
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
    link = models.URLField(max_length=500, unique=True, null=True, blank=True) 
    source = models.CharField(max_length=100, default='Unknown') 
    categories = models.ManyToManyField('Category', related_name='multi_articles') 
    summary = models.TextField(blank=True, null=True) 
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

class SummaryFeedback(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    article = models.ForeignKey(Article, on_delete=models.CASCADE) 
    is_helpful = models.BooleanField() # True for helpful, False for not helpful 
    feedback_date = models.DateTimeField(auto_now_add=True) 
    class Meta: 
    # Ensures a user can only leave one feedback per article 
        unique_together = ('user', 'article')  
        verbose_name_plural = "Summary Feedback" 
    def __str__(self): 
        return f"{self.user.username} - {self.article.title[:30]} - Helpful: {self.is_helpful}"