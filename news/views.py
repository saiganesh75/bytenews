from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import Article, Category, UserPreference, ReadingHistory, SummaryFeedback
from newspaper import Article as NewsArticle  # for scraping and NLP

# Home View
def home(request):
    return HttpResponse("<h1>Welcome to NewsGenie AI</h1>")

# ListView for displaying articles (only approved ones)
class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.filter(approved=True).order_by('-published_date')
        category_name = self.request.GET.get('category')
        query = self.request.GET.get('q')

        if category_name and category_name.lower() != 'all':
            queryset = queryset.filter(category__name__iexact=category_name)

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if self.request.user.is_authenticated:
            try:
                user_preferences = (
                    self.request.user.user_preference_news.preferred_categories.all()

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

        if self.request.user.is_authenticated:
            try:
                user_preferences = (
                    self.request.user.user_preference_news.preferred_categories.all()

                    if hasattr(self.request.user, 'userpreference')
                    else Category.objects.none()
                )
                if user_preferences.exists():
                    preferred_articles = Article.objects.filter(
                        category__in=user_preferences, approved=True
                    )
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

# Detail view with approval check
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(approved=True)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.approved and not self.request.user.is_staff:
            raise Http404("Article not found or not yet approved.")
        if self.request.user.is_authenticated:
            ReadingHistory.objects.update_or_create(
                user=self.request.user,
                article=obj,
                defaults={'timestamp': timezone.now()}
            )
        return obj

# For handling summary toggle on article detail
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if not article.approved and not request.user.is_staff:
        raise Http404("This article is not yet approved.")
    show_summary = request.GET.get('show_summary') == '1'
    return render(request, 'news/article_detail.html', {
        'article': article,
        'show_summary': show_summary,
    })

# View for generating summary using newspaper3k
@login_required
def generate_summary_view(request, pk):
    article = get_object_or_404(Article, pk=pk)

    try:
        news_article = NewsArticle(article.source_url, keep_article_html=False)
        news_article.download()
        news_article.parse()
        news_article.nlp()

        article.summary = news_article.summary
        article.is_summary_generated = True
        article.save()

        messages.success(request, "New summary generated successfully!")

    except Exception as e:
        print(f"Error while generating summary: {e}")
        messages.error(request, "Failed to generate summary.")

    return redirect(f'{reverse("news:article_detail", args=[pk])}?show_summary=1')

# Reading history view
@login_required
def reading_history_view(request):
    history = ReadingHistory.objects.filter(user=request.user).select_related('article').order_by('-timestamp')
    return render(request, 'news/reading_history.html', {'history': history})

# Submit feedback on summaries
@login_required
@require_POST
def submit_summary_feedback(request, pk):
    article = get_object_or_404(Article, pk=pk)
    is_helpful = request.POST.get('is_helpful')
    if is_helpful is not None:
        is_helpful_bool = (is_helpful.lower() == 'true')
        SummaryFeedback.objects.update_or_create(
            user=request.user,
            article=article,
            defaults={'is_helpful': is_helpful_bool}
        )
        messages.success(request, 'Thank you for your feedback!')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'helpful': is_helpful_bool})
        else:
            return redirect('news:article_detail', pk=pk)

    messages.error(request, 'Invalid feedback provided.')
    return redirect('news:article_detail', pk=pk)

# Fallback list view (also show only approved)
def article_list(request):
    articles = Article.objects.filter(approved=True).order_by('-published_date')
    return render(request, 'news/article_list.html', {'articles': articles})
