import requests
from bs4 import BeautifulSoup
import feedparser
from newspaper import Article
from datetime import datetime, timedelta
import time
from backend.config import Config
import anthropic
import json
import logging

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.config = Config()
        
        # Validate API key
        if not self.config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        try:
            self.anthropic_client = anthropic.Anthropic(
                api_key=self.config.ANTHROPIC_API_KEY
            )
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def fetch_rss_feeds(self):
        """Fetch news from RSS feeds"""
        articles = []
        
        for feed_url in self.config.RSS_FEEDS:
            try:
                logger.info(f"Fetching RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Get top 10 from each feed
                    try:
                        published = entry.get('published_parsed', None)
                        if published:
                            published_date = datetime(*published[:6])
                        else:
                            published_date = datetime.now()
                        
                        # Only include articles from last 48 hours
                        if datetime.now() - published_date <= timedelta(hours=48):
                            articles.append({
                                'title': entry.get('title', ''),
                                'url': entry.get('link', ''),
                                'source': feed_url.split('/')[2],
                                'published_date': published_date,
                                'summary': entry.get('summary', '')
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing RSS entry: {e}")
                        continue
                
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {e}")
                continue
        
        logger.info(f"Fetched {len(articles)} articles from RSS feeds")
        return articles
    
    def fetch_article_content(self, url):
        """Fetch full article content"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            logger.warning(f"Error fetching article {url}: {e}")
            return ""
    
    def search_with_claude(self, query):
        """Use Claude AI to search for recent news"""
        try:
            logger.info(f"Searching with Claude: {query}")
            
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search"
                }],
                messages=[{
                    "role": "user",
                    "content": f"""Search for: {query}
                    
Focus on news from the last 48 hours about global financial institutions 
(banks and asset managers) that could impact Indian stock markets.

Return credible sources like Reuters, Bloomberg, Financial Times, 
Economic Times, Moneycontrol, etc.

Include information about:
- Institution names
- Impact on Indian markets
- Sentiment (positive/negative/neutral)
- Key developments

Provide a concise summary of the most important findings."""
                }]
            )
            
            return message.content
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error with Claude search: {e}")
            return []
    
    def comprehensive_search(self):
        """Perform comprehensive news search"""
        all_articles = []
        
        # Search queries for Claude (reduced from 8 to 5 to save API costs)
        search_queries = [
            "global banks India news today financial institutions",
            "JPMorgan Goldman Sachs HSBC India latest developments",
            "BlackRock Vanguard India investments emerging markets",
            "RBI policy foreign banks India",
            "Indian stock market international banks news"
        ]
        
        logger.info("Fetching news with AI search...")
        for idx, query in enumerate(search_queries, 1):
            try:
                logger.info(f"Query {idx}/{len(search_queries)}: {query}")
                results = self.search_with_claude(query)
                
                # Parse Claude's response
                for block in results:
                    if hasattr(block, 'text') and block.text:
                        # Store the search results
                        all_articles.append({
                            'title': f"AI Analysis: {query[:50]}...",
                            'content': block.text,
                            'source': 'AI Search',
                            'published_date': datetime.now(),
                            'url': f"ai_search_{len(all_articles)}"
                        })
                
                time.sleep(2)  # Rate limiting between API calls
            except Exception as e:
                logger.error(f"Error in AI search for '{query}': {e}")
                continue
        
        # Also fetch RSS feeds
        logger.info("Fetching RSS feeds...")
        rss_articles = self.fetch_rss_feeds()
        
        # Combine and enrich articles
        for article in rss_articles:
            try:
                if article['url'] and article['url'].startswith('http'):
                    content = self.fetch_article_content(article['url'])
                    article['content'] = content if content else article.get('summary', '')
                    all_articles.append(article)
            except Exception as e:
                logger.warning(f"Error enriching article: {e}")
                continue
        
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles