from django.contrib import admin
from .models import Category, Article, UserPreference, ReadingHistory, SummaryFeedback
from django.db.models import Count 
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_date', 'created_at', 'is_approved']
    list_filter = ['category', 'published_date', 'approved']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']
    fields = ('title', 'author', 'published_date', 'categories', 'content', 'image', 'link', 'approved')

    # ✅ Display approved status as a checkmark
    @admin.display(boolean=True, description='Approved')
    def is_approved(self, obj):
        return obj.approved

    # ✅ Bulk action: Approve
    def make_approved(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected articles have been marked as approved.", level='success')
    make_approved.short_description = "Mark selected articles as approved"

    # ✅ Bulk action: Mark as pending
    def make_pending(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, "Selected articles have been marked as pending.", level='warning')
    make_pending.short_description = "Mark selected articles as pending"

    # ✅ Register actions
    actions = [make_approved, make_pending]
    def changelist_view(self, request, extra_context=None): 
        response = super().changelist_view(request, extra_context=extra_context) 
        try: 
            qs = response.context_data['cl'].queryset # Get the current queryset being displayed 
        except (AttributeError, KeyError): 
            qs = Article.objects.all() # Fallback if queryset not available 
 
        approved_count = qs.filter(approved=True).count() 
        pending_count = qs.filter(approved=False).count() 
        total_count = qs.count() 
 
        response.context_data['article_stats'] = { 
            'total': total_count, 
            'approved': approved_count, 
            'pending': pending_count, 
        } 
        return response 

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['preferred_categories']

@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'timestamp']
    list_filter = ['timestamp']
    readonly_fields = ['timestamp']

@admin.register(SummaryFeedback)
class SummaryFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'is_helpful', 'feedback_date']
    list_filter = ['is_helpful', 'feedback_date']