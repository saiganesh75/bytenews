from django.views.generic import ListView ,DetailView
from .models import Article, Category

from django.shortcuts import render
from django.http import HttpResponse
def home(request):
    return HttpResponse("<h1>Welcome to NewsGenie AI</h1>")
class ArticleListView(ListView):
    def get_queryset(self): 
        queryset = super().get_queryset() # Start with all articles 
        category_name = self.request.GET.get('category') 

        if category_name: 
            # Filter articles by category name (case-insensitive) 
            queryset = queryset.filter(categories__name__iexact=category_name) 
        return queryset 
 
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        context['categories'] = Category.objects.all().order_by('name') 
        context['current_category'] = self.request.GET.get('category', 'All') 
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