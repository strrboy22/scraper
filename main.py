import feedparser
import html
import requests
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def main():
    rss_feeds = {
        "GMA News": "https://data.gmanetwork.com/gno/rss/news/feed.xml",
        "Inquirer": "https://www.inquirer.net/fullfeed",
        "Philstar": "https://www.philstar.com/rss/headlines",
        "Manila Bulletin": "https://mb.com.ph/rss",
        "ABS-CBN News": "https://news.abs-cbn.com/feed",
        "BusinessWorld": "https://www.bworldonline.com/feed/",
        "Rappler": "https://www.rappler.com/rss",
        "PhilNews": "http://philnews.ph/rss",
        "Manila Times": "https://www.manilatimes.net/news/feed/",
        "TV 5": "https://interaksyon.philstar.com/rss"
    }

    threat_keywords = ["hacker", "data breach", "breach", "data", "cyber", "scam", "arrest", "gcash", "ransomware", "phishing", "defaced", "dict", "npc"]
    WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
    DATABASE_URL = os.getenv("DATABASE_URL")

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:

            for source_name, feed_url in rss_feeds.items():
                try:
                    feed = feedparser.parse(feed_url)

                    if not feed.entries:
                        print(f"[WARNING] No entries found for {feed_url}")
                        continue

                    for article in feed.entries:
                        link = html.unescape(article.link)
                        cur.execute("SELECT 1 FROM news_article WHERE link = %s", (link,))

                        if cur.fetchone() is not None:
                            continue

                        title = html.unescape(article.title)
                        title_lower = html.unescape(article.title).lower()
                        raw_date = article.get("link", article.get("pubDate", article.get("updated", "Unknown Date")))
                        published = html.unescape(raw_date)
                        print(f"[NEW ARTICLE]\ntitle: {title}")
                        is_threat = False

                        for threat in threat_keywords:
                            if threat in title_lower:
                                alert_message = f"""
                                **THREAT DETECTED: {threat.upper()}**
                                **Source**: {source_name}
                                **Title**: {title}
                                **Date**: {published}
                                **Link**: {link}
                                """
                                threat_payload = {
                                    "content": alert_message
                                }
                                requests.post(WEBHOOK_URL, json=threat_payload)
                                is_threat = True
                                break
                        cur.execute("""
                            INSERT INTO news_article (title, link, published_date, is_threat, source) VALUES (%s, %s, %s, %s, %s)""", (title, link, published, is_threat, source_name))
                except Exception as e:
                    print(f"[ERROR] Failed to scrape {source_name}: {e}")
                    continue
        conn.commit()

if __name__ == "__main__":
    main()

