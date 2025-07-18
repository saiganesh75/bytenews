from django.views.generic import ListView ,DetailView
from .models import Article, Category
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count 
def home(request):
    return HttpResponse("<h1>Welcome to NewsGenie AI</h1>")
class ArticleListView(ListView):
    def get_queryset(self): 
        queryset = super().get_queryset() # Start with all articles 
        category_name = self.request.GET.get('category') 
        query = self.request.GET.get('q')

        if category_name: 
            # Filter articles by category name (case-insensitive) 
            queryset = queryset.filter(categories__name__iexact=category_name)
        if query: 
            # Use Q objects for OR logic: search in title OR content 
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query)) 
            # __icontains means 'case-insensitive contains' 
 
        return queryset 
        
 
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        context['categories'] = Category.objects.all().order_by('name') 
        context['current_category'] = self.request.GET.get('category', 'All') 
        context['search_query'] = self.request.GET.get('q', '') # Pass current search query to 
        context['categories'] = Category.objects.annotate( 
        article_count=Count('article') 
        ).order_by('name')
        return context 
    model = Article # Tell ListView which model to work with 
    template_name = 'news/article_list.html' # The template to render 
    context_object_name = 'articles' # The variable name to use in the template 
    ordering = ['-published_date'] # Order articles by most recent first 
    paginate_by = 10 # For Task 5: Pagination
    queryset = Article.objects.order_by('-published_date')

class ArticleDetailView(DetailView): 
    model = Article 
    template_name = 'news/article_detail.html' 
    context_object_name = 'article' # The variable name to use in the template