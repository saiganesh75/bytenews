from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Article, Category, UserPreference, ReadingHistory


def home(request):
    return HttpResponse("<h1>Welcome to NewsGenie AI</h1>")


class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    ordering = ['-published_date']
    paginate_by = 10
    queryset = Article.objects.order_by('-published_date')

    def get_queryset(self):
        queryset = super().get_queryset()
        category_name = self.request.GET.get('category')
        query = self.request.GET.get('q')

        # Filter by category
        if category_name and category_name.lower() != 'all':
            queryset = queryset.filter(category__name__iexact=category_name)

        # Search by title or content
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        # Personalized feed
        if self.request.user.is_authenticated:
            try:
                user_preferences = (
                    self.request.user.userpreference.preferred_category.all()
                    if hasattr(self.request.user, 'userpreference')
                    else Category.objects.none()
                )

                if user_preferences.exists():
                    queryset = queryset.filter(category__in=user_preferences)
                    messages.info(self.request, "Showing articles based on your preferences.")
                else:
                    messages.info(self.request, "No preferences set. Showing all articles.")
            except UserPreference.DoesNotExist:
                messages.info(self.request, "No preferences found. Showing all articles.")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(article_count=Count('article')).order_by('name')
        context['current_category'] = self.request.GET.get('category', 'All')
        context['search_query'] = self.request.GET.get('q', '')
        context['recommendations'] = []

        # Recommendation system
        if self.request.user.is_authenticated:
            try:
                user_preferences = (
                    self.request.user.userpreference.preferred_category.all()
                    if hasattr(self.request.user, 'userpreference')
                    else Category.objects.none()
                )

                if user_preferences.exists():
                    preferred_articles = Article.objects.filter(category__in=user_preferences)
                    read_article_ids = ReadingHistory.objects.filter(
                        user=self.request.user
                    ).values_list('article__id', flat=True)
                    recommendations = preferred_articles.exclude(
                        id__in=read_article_ids
                    ).order_by('-published_date')[:5]
                    context['recommendations'] = recommendations
            except UserPreference.DoesNotExist:
                pass

        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # Track reading history
        if self.request.user.is_authenticated:
            ReadingHistory.objects.update_or_create(
    user=self.request.user,
    article=obj,
    defaults={'timestamp': timezone.now()}
)


        return obj


@login_required
def reading_history_view(request):
    history = ReadingHistory.objects.filter(user=request.user).select_related('article').order_by('-timestamp')

    return render(request, 'news/reading_history.html', {'history': history})
