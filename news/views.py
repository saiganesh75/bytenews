from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .utils import generate_summary 
from .models import Article, Category, UserPreference, ReadingHistory
import nltk
from .models import SummaryFeedback

from .models import Article
from nltk.tokenize import sent_tokenize
from django.views.decorators.http import require_POST # To ensure only POST requests 
from django.http import JsonResponse #
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
@login_required 
def generate_summary_view(request, pk): 
    article = get_object_or_404(Article, pk=pk) 
    # Generate and save the summary 
    article.summary = generate_summary(article.content) 
    article.save() 
    messages.success(request, "Summary generated successfully!") 
    return redirect('news:detail', pk=pk) 
@login_required 
@require_POST # Ensure this view only accepts POST requests 
def submit_summary_feedback(request, pk): 
    article = get_object_or_404(Article, pk=pk) 
    is_helpful = request.POST.get('is_helpful') # Get the value from the form 
    if is_helpful is not None: 
            # Convert string 'true'/'false' to boolean 
        is_helpful_bool = (is_helpful.lower() == 'true')  
    
            # Get or update the feedback 
        feedback, created = SummaryFeedback.objects.update_or_create( 
                user=request.user, 
                article=article, 
                defaults={'is_helpful': is_helpful_bool} 
            ) 
        messages.success(request, 'Thank you for your feedback!') 
    
            # If using AJAX, return JSON. Otherwise, redirect. 
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
            return JsonResponse({'status': 'success', 'helpful': is_helpful_bool}) 
        else: 
            return redirect('news:detail', pk=pk) 
    
    messages.error(request, 'Invalid feedback provided.') 
    return redirect('news:detail', pk=pk) 