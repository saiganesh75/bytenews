import requests
import feedparser
import time
from datetime import datetime
from datetime import timezone as dt_timezone
from django.utils import timezone


def fetch_bbc_news_rss():
    BBC_RSS_FEED_URL = "https://feeds.bbci.co.uk/news/rss.xml"
    articles_data = []
    
    try:
        response = requests.get(
            BBC_RSS_FEED_URL,
            headers={'User-Agent': 'ByteNewsScraper/1.0'},
            timeout=10
        )
        response.raise_for_status()
        feed = feedparser.parse(response.content)

        for entry in feed.entries:
            title = entry.title
            link = entry.link
            content = entry.get('summary', entry.get('description', 'No content available.'))

            # Get proper published date
            published_date = None
            if hasattr(entry, 'published_parsed'):
                published_date = datetime.fromtimestamp(
                    time.mktime(entry.published_parsed),
                    tz=dt_timezone.utc
                )
            else:
                published_date = timezone.now()

            articles_data.append({
                'title': title,
                'link': link,
                'content': content,
                'publication_date': published_date,
                'source': 'BBC News'
            })

        return articles_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed from BBC News: {e}")
        return []
    except Exception as e:
        print(f"An error occurred during RSS parsing: {e}")
        return []
