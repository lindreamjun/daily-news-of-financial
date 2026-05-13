#!/usr/bin/env python3
"""
Premium News Collection & Email Distribution System
Collects news from trusted global sources only
"""

import os
import json
import logging
import smtplib
import feedparser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict
import time
import re
from html.parser import HTMLParser

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"news_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MLStripper(HTMLParser):
    """Remove HTML tags"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_data(self):
        return ''.join(self.text)

def strip_html(html):
    """Strip HTML tags from text"""
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class PremiumNewsCollector:
    """Collects news from verified premium sources only"""
    
    def __init__(self, config_path: str = "config/news_sources.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.articles = {}
        logger.info("✅ Configuration loaded")
    
    def collect_news(self) -> Dict[str, List[Dict]]:
        """Collect news from premium sources"""
        logger.info("=" * 80)
        logger.info("🚀 Starting Premium News Collection")
        logger.info("=" * 80)
        
        categories = self.config.get('categories', {})
        
        for category_key, category_info in categories.items():
            logger.info(f"\n📂 Category: {category_info['name']}")
            self.articles[category_key] = []
            
            sources = category_info.get('sources', [])
            
            for source_name in sources:
                source_info = self.config['premium_sources'].get(source_name)
                if not source_info:
                    logger.warning(f"  ⚠️ Source not found: {source_name}")
                    continue
                
                try:
                    articles = self._fetch_from_source(source_name, source_info)
                    self.articles[category_key].extend(articles)
                    logger.info(f"  ✅ {source_name}: {len(articles)} articles found")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"  ❌ Error fetching from {source_name}: {e}")
            
            # Limit to max articles
            max_articles = self.config.get('max_articles_per_category', 20)
            self.articles[category_key] = self.articles[category_key][:max_articles]
            logger.info(f"  📊 Final count: {len(self.articles[category_key])}")
        
        total = sum(len(v) for v in self.articles.values())
        logger.info(f"\n✅ Collection Complete - Total: {total} articles")
        logger.info("=" * 80)
        return self.articles
    
    def _fetch_from_source(self, source_name: str, source_info: Dict) -> List[Dict]:
        """Fetch articles from RSS feed"""
        articles = []
        rss_feed = source_info.get('rss_feed')
        
        if not rss_feed:
            logger.debug(f"  ℹ️ No RSS feed for {source_name}")
            return articles
        
        try:
            feed = feedparser.parse(rss_feed)
            
            for entry in feed.entries[:25]:
                try:
                    article = {
                        'title': entry.get('title', 'No title'),
                        'summary': strip_html(entry.get('summary', '')[:400]),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', datetime.now().isoformat()),
                        'source': source_name,
                        'credibility': source_info.get('credibility', 'Premium Source')
                    }
                    
                    # Validate article
                    if article['title'] and article['link']:
                        articles.append(article)
                except Exception as e:
                    logger.debug(f"    Error parsing entry: {e}")
                    continue
            
            return articles[:20]
        
        except Exception as e:
            logger.error(f"Error parsing RSS {rss_feed}: {e}")
            return []

class NewsEmailFormatter:
    """Format and send news digest"""
    
    def generate_html_report(self, articles: Dict, categories: Dict) -> str:
        """Generate HTML email"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{ 
            max-width: 900px;
            margin: 0 auto;
            background: white;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .category {{
            background: #f9f9f9;
            margin: 20px 0;
            padding: 25px;
            border-left: 5px solid #667eea;
            border-radius: 0 4px 4px 0;
        }}
        .category h2 {{
            color: #667eea;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .article {{
            background: white;
            margin: 15px 0;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            transition: box-shadow 0.2s;
        }}
        .article:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .article-number {{
            display: inline-block;
            background: #667eea;
            color: white;
            width: 28px;
            height: 28px;
            line-height: 28px;
            text-align: center;
            border-radius: 50%;
            font-weight: bold;
            margin-right: 10px;
            font-size: 0.9em;
        }}
        .article h3 {{
            margin: 10px 0;
            color: #222;
            font-size: 1.1em;
        }}
        .article-meta {{
            font-size: 0.9em;
            color: #666;
            margin: 10px 0;
        }}
        .article-summary {{
            color: #555;
            line-height: 1.6;
            margin: 10px 0;
        }}
        .source-badge {{
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 0.85em;
            margin: 5px 5px 5px 0;
        }}
        .credibility {{
            font-size: 0.85em;
            color: #666;
        }}
        .read-more {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 15px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 3px;
            font-size: 0.9em;
            transition: background 0.2s;
        }}
        .read-more:hover {{
            background: #764ba2;
        }}
        .footer {{
            background: #f9f9f9;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #e0e0e0;
        }}
        .empty {{
            color: #999;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 全球新闻日报</h1>
            <p>Global News Daily Digest</p>
            <p>{datetime.now().strftime('%Y年%m月%d日 | %B %d, %Y')}</p>
        </div>
"""
        
        for category_key, category_info in categories.items():
            category_name = category_info.get('name', '')
            articles_list = articles.get(category_key, [])
            
            html += f'<div class="category"><h2>{category_name}</h2>'
            
            if not articles_list:
                html += '<div class="empty">暂无相关新闻 | No relevant news available</div>'
            else:
                for idx, article in enumerate(articles_list, 1):
                    html += f"""
                    <div class="article">
                        <h3><span class="article-number">{idx}</span>{article.get('title', '')}</h3>
                        <div class="article-meta">
                            📅 {article.get('published', 'N/A')}
                        </div>
                        <div class="source-badge">✓ {article.get('source', '')}</div>
                        <p class="credibility">{article.get('credibility', '')}</p>
                        <div class="article-summary">
                            {article.get('summary', 'No summary')}
                        </div>
                        <a href="{article.get('link', '#')}" class="read-more" target="_blank">📖 阅读原文 | Read Full Article</a>
                    </div>
                    """
            
            html += '</div>'
        
        html += """
        <div class="footer">
            <p><strong>信息来源声明 | Source Disclaimer:</strong></p>
            <p>本日报仅收集来自全球顶级新闻机构的信息，包括彭博社、金融时报、经济学人、华尔街日报、路透社、BBC等。</p>
            <p>This digest only collects news from premium global media including Bloomberg, Financial Times, The Economist, Wall Street Journal, Reuters, BBC, etc.</p>
            <p style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
                信息仅供参考，不构成投资建议 | Information for reference only, not investment advice<br>
                © 2026 Global News Daily | Powered by GitHub Actions
            </p>
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def send_email(self, recipient: str, subject: str, html_content: str) -> bool:
        """Send email via SMTP"""
        try:
            logger.info(f"📧 Sending email to {recipient}")
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = os.getenv('SMTP_USERNAME')
            msg['To'] = recipient
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
            server.starttls()
            server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email sent successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}")
            raise

def main():
    """Main execution"""
    try:
        # Collect news
        logger.info("🔍 Starting news collection...")
        collector = PremiumNewsCollector()
        articles = collector.collect_news()
        
        # Load config
        with open('config/news_sources.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Format and send email
        logger.info("📧 Generating email report...")
        formatter = NewsEmailFormatter()
        html_content = formatter.generate_html_report(articles, config['categories'])
        
        recipient = os.getenv('EMAIL_RECIPIENT')
        if not recipient:
            raise ValueError("❌ EMAIL_RECIPIENT not set!")
        
        subject = f"📰 全球新闻日报 | Global News Daily - {datetime.now().strftime('%Y-%m-%d')}"
        formatter.send_email(recipient, subject, html_content)
        
        logger.info("✅ Task completed successfully!")
        
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
