import requests
import feedparser
import time
import nltk
from datetime import datetime
from datetime import timezone as dt_timezone
from django.utils import timezone
from bs4 import BeautifulSoup
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, sent_tokenize 
from collections import Counter
from newspaper import Article as NewsArticle
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
# Download required NLTK data if not present
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def fetch_news_from_rss(feed_url, source_name):
    articles_data = []

    try:
        response = requests.get(feed_url, headers={'User-Agent': 'ByteNewsScraper/1.0'}, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)

        for entry in feed.entries:
            title = entry.title
            link = entry.link

            if hasattr(entry, 'published_parsed'):
                published_date = datetime.fromtimestamp(
                    time.mktime(entry.published_parsed),
                    tz=dt_timezone.utc
                )
            else:
                published_date = timezone.now()

            # ✅ Try to get full content via newspaper3k
            try:
                article = NewsArticle(link)
                article.download()
                article.parse()
                full_content = article.text.strip()
            except Exception:
                # fallback to RSS summary if scraping fails
                full_content = clean_html(entry.get('summary') or entry.get('description', ''))

            if not full_content:
                full_content = "Content unavailable."

            articles_data.append({
                'title': title,
                'link': link,
                'content': full_content,
                'publication_date': published_date,
                'source': source_name
            })

        return articles_data

    except Exception as e:
        print(f"Error scraping {source_name}: {e}")
        return []
def generate_summary(text,article_title="", num_sentences=5):
    if not text or not isinstance(text, str):
        return "No content available to summarize."

    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text

    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    word_frequencies = Counter(filtered_words)
    if article_title: 
        title_words = word_tokenize(article_title.lower()) 
        for word in title_words: 
            if word in word_frequencies: 
                word_frequencies[word] += 0.5 

    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if i not in sentence_scores: 
                    sentence_scores[i] = sentence_scores.get(i, 0) + word_frequencies[word]
            if i == 0: # First sentence 
                if i in sentence_scores: sentence_scores[i] += 1.0 
                else: sentence_scores[i] = 1.0 # Or assign initial score if not yet scored 
            elif i == 1 and len(sentences) > 1: # Second sentence 
                if i in sentence_scores: sentence_scores[i] += 0.5 
                else: sentence_scores[i] = 0.5
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    top_indices = sorted([i for i, _ in top_sentences])
    return " ".join([sentences[i] for i in top_indices])