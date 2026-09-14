import feedparser
from flask import Flask, render_template, request
import psycopg2

import calendar
from datetime import datetime, timezone


app = Flask(__name__)

RSS_FEEDS = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/cnn_topstories.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'reddit_canada_news': 'https://www.reddit.com/r/canadanews/.rss',
}
INSERT_QUERY = """
            INSERT INTO articles (source, title, link, published_at, summary)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (link) DO NOTHING;
            """



def to_datetime(struct_time):
    """Convert feedparser's published_parsed (a time.struct_time in UTC) to a datetime."""
    if not struct_time:
        return None
    return datetime.fromtimestamp(calendar.timegm(struct_time), tz=timezone.utc)

def get_conn():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="rss_aggregator",
        user="postgres",
        password="postgres"
    )
    return conn

def fetch_all_feeds():
    conn = get_conn()
    cursor = conn.cursor()
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            link = getattr(entry, 'link', None)
            title = getattr(entry, 'title', None)
            published_at = to_datetime(getattr(entry, 'published_parsed', None))
            summary = None if source == 'reddit_canada_news' else getattr(entry, 'summary', None)
            if link and title:
                cursor.execute(INSERT_QUERY, (source, title, link, published_at, summary))
    conn.commit()
    cursor.close()
    conn.close()


@app.route('/')
def index():
    articles = []
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT source, title, link, published_at, summary FROM articles ORDER BY COALESCE(published_at, fetched_at) DESC")
    rows = cursor.fetchall()
    for row in rows:
        source, title, link, published_at, summary = row
        articles.append((source, type('Entry', (object,), {'title': title, 'link': link, 'published': published_at, 'summary': summary})()))

    cursor.close()
    conn.close()
    #articles = sorted(articles, key=lambda x: getattr(x[1], 'published_parsed', ()) or (), reverse=True)

    page = request.args.get('page', 1, type=int)
    per_page = 15

    total_articles = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]
    return render_template('index.html', articles=paginated_articles, total_pages=total_articles // per_page + (1 if total_articles % per_page else 0), page=page)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = get_conn()
    cursor = conn.cursor()

    results = []
    cursor.execute("SELECT source, title, link, published_at, summary FROM articles WHERE title ILIKE %s OR summary ILIKE %s ORDER BY published_at DESC", (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    for row in rows:
        source, title, link, published_at, summary = row
        results.append((source, type('Entry', (object,), {'title': title, 'link': link, 'published': published_at, 'summary': summary})()))

    return render_template('search_results.html', articles=results, query=query)

if __name__ == '__main__':
    fetch_all_feeds()
    app.run(debug=True)


# from bs4 import BeautifulSoup

# import requests
# import lxml

# url_1 = "https://www.reddit.com/r/AmItheAsshole/comments/1vqfb03/aitah_for_banning_my_friends_kids_from_our_lake.rss"
# url_2 = "https://www.bbc.com/audio/play/p0p38lpy?at_medium=RSS&at_campaign=rss"
# url_3 = "https://realpython.com/atom.xml"
# headers = {
#     "User-Agent": "Mozilla/5.0 (compatible; MyRSSAggregator/1.0)"
# }

# response_1 = requests.get(url_1, headers=headers)
# response_2 = requests.get(url_2, headers=headers)
# response_3 = requests.get(url_3, headers=headers)

# print(response_1.status_code)
# print(response_2.status_code)
# print(response_3.status_code)


# soup = BeautifulSoup(response_3.content, 'xml')

# entries = soup.find_all('entry')

# for entry in entries:
#     title = entry.title.text
#     summary = entry.summary.text
#     link = entry.link['href']
#     print(f"Title: {title}, \nSummary: {summary} \nlink: {link}\n\n----------------------------")