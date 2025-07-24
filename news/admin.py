from django.contrib import admin

# Register your models here.
#news/admin.py:

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Article, UserPreference, ReadingHistory

admin.site.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_date', 'created_at']
    list_filter = ['category', 'published_date']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']
    fields = ('title', 'author', 'published_date', 'categories', 'content', 'image', 'source_url')

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['preferred_categories']

@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'timestamp']
    list_filter = ['timestamp']
    readonly_fields = ['timestamp']