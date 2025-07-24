from django.core.management.base import BaseCommand
from news.utils import fetch_bbc_news_rss
from news.models import Article, Category

class Command(BaseCommand):
    help = 'Scrapes news articles from BBC RSS feed and saves them to the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting news scraping...")

        articles_data = fetch_bbc_news_rss()

        if not articles_data:
            self.stdout.write(self.style.WARNING("No articles fetched. Check for errors during scraping."))
            return

        articles_added = 0
        for article_data in articles_data:
            if not Article.objects.filter(title=article_data['title']).exists():
                general_category, _ = Category.objects.get_or_create(name='General')

                article = Article.objects.create(
                    title=article_data['title'],
                    content=article_data['content'],
                    publication_date=article_data['publication_date'],
                    author=article_data.get('source', 'Unknown Source'),
                    category=general_category
                )
                articles_added += 1

        self.stdout.write(self.style.SUCCESS(f"Finished scraping. Added {articles_added} new articles."))
