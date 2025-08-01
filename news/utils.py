import requests
import feedparser
import time
import nltk
import os 
from gtts import gTTS 
from django.conf import settings 
import logging
from datetime import datetime
from datetime import timezone as dt_timezone
from django.utils import timezone
from bs4 import BeautifulSoup
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, sent_tokenize 
from collections import Counter
from newspaper import Article as NewsArticle

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

            # ✅ Check for valid URL before downloading
            if not link or not link.startswith("http"):
                print(f"Invalid link: {link}")
                full_content = clean_html(entry.get('summary') or entry.get('description', ''))
            else:
                try:
                    article = NewsArticle(link)
                    article.download()
                    article.parse()
                    full_content = article.text.strip()
                except Exception:
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

def generate_summary(text, article_title="", num_sentences=5):
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
        if i == 0: 
            sentence_scores[i] = sentence_scores.get(i, 0) + 1.0
        elif i == 1 and len(sentences) > 1: 
            sentence_scores[i] = sentence_scores.get(i, 0) + 0.5

    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    top_indices = sorted([i for i, _ in top_sentences])
    return " ".join([sentences[i] for i in top_indices])
logger = logging.getLogger(__name__) 
 
def generate_audio_summary(text, article_id): 
    if not text: 
        logger.warning(f"No text provided for audio summary for article_id: {article_id}") 
        return None 
 
    # Create a unique filename for the audio 
    filename = f"summary_{article_id}.mp3" 
 
    # Construct the full path where the audio file will be saved 
    # This will be MEDIA_ROOT/news_audio/summary_<article_id>.mp3 
    audio_dir = os.path.join(settings.MEDIA_ROOT, 'news_audio') 
    os.makedirs(audio_dir, exist_ok=True) # Ensure the directory exists 
 
    filepath = os.path.join(audio_dir, filename) 
 
    try: 
        tts = gTTS(text=text, lang='en') 
        tts.save(filepath) 
        logger.info(f"Generated audio summary for article {article_id} at {filepath}") 
        # Return the URL relative to MEDIA_URL 
        return os.path.join(settings.MEDIA_URL, 'news_audio', filename) 
    except Exception as e: 
        logger.error(f"Error generating audio for article {article_id}: {e}") 
        return None