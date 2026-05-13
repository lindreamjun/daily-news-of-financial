#!/usr/bin/env python3
"""
Premium News Collection & Email Distribution System
"""

import os
import json
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import feedparser
import time

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def strip_html(html_text):
    """Simple HTML tag removal"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text).strip()

def collect_news_from_rss(sources_config):
    """Collect news from RSS feeds"""
    logger.info("=" * 80)
    logger.info("🚀 Starting News Collection")
    logger.info("=" * 80)
    
    articles = {}
    
    # Load config
    with open('config/news_sources.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    categories = config.get('categories', {})
    premium_sources = config.get('premium_sources', {})
    
    for category_key, category_info in categories.items():
        category_name = category_info.get('name', '')
        logger.info(f"\n📂 Processing: {category_name}")
        articles[category_key] = []
        
        sources = category_info.get('sources', [])
        
        for source_name in sources:
            source_info = premium_sources.get(source_name, {})
            if not source_info:
                logger.warning(f"  ⚠️ Source not found: {source_name}")
                continue
            
            rss_feed = source_info.get('rss_feed')
            if not rss_feed:
                logger.debug(f"  ℹ️ No RSS feed for {source_name}")
                continue
            
            try:
                logger.info(f"  🔗 Fetching from {source_name}...")
                feed = feedparser.parse(rss_feed)
                
                count = 0
                for entry in feed.entries[:20]:
                    try:
                        article = {
                            'title': entry.get('title', 'No title'),
                            'summary': strip_html(entry.get('summary', ''))[:300],
                            'link': entry.get('link', ''),
                            'published': entry.get('published', datetime.now().isoformat()),
                            'source': source_name,
                            'credibility': source_info.get('credibility', 'Premium Source')
                        }
                        
                        if article['title'] and article['link'] and article['summary']:
                            articles[category_key].append(article)
                            count += 1
                            
                            if count >= 5:  # Limit to 5 per source
                                break
                    except Exception as e:
                        logger.debug(f"    Error parsing entry: {e}")
                        continue
                
                logger.info(f"  ✅ {source_name}: {count} articles collected")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"  ❌ Error fetching from {source_name}: {str(e)}")
                continue
        
        # Limit to 20 per category
        articles[category_key] = articles[category_key][:20]
        logger.info(f"  📊 Total for this category: {len(articles[category_key])}")
    
    total = sum(len(v) for v in articles.values())
    logger.info(f"\n✅ Collection Complete - Total: {total} articles")
    logger.info("=" * 80)
    
    return articles

def generate_email_html(articles, categories_config):
    """Generate HTML email"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .category {{ background: #f9f9f9; margin: 20px 0; padding: 25px; border-left: 5px solid #667eea; }}
        .category h2 {{ color: #667eea; font-size: 1.5em; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .article {{ background: white; margin: 15px 0; padding: 15px; border: 1px solid #e0e0e0; border-radius: 4px; }}
        .article h3 {{ margin: 10px 0; color: #222; font-size: 1.1em; }}
        .article-meta {{ font-size: 0.9em; color: #666; margin: 10px 0; }}
        .source-badge {{ display: inline-block; background: #4CAF50; color: white; padding: 3px 10px; border-radius: 3px; font-size: 0.85em; margin: 5px 5px 5px 0; }}
        .read-more {{ display: inline-block; margin-top: 10px; padding: 8px 15px; background: #667eea; color: white; text-decoration: none; border-radius: 3px; }}
        .footer {{ background: #f9f9f9; padding: 30px; text-align: center; color: #666; font-size: 0.9em; border-top: 1px solid #e0e0e0; }}
        .empty {{ color: #999; font-style: italic; padding: 20px; text-align: center; }}
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
    
    for category_key, category_info in categories_config.items():
        category_name = category_info.get('name', '')
        articles_list = articles.get(category_key, [])
        
        html += f'<div class="category"><h2>{category_name}</h2>'
        
        if not articles_list:
            html += '<div class="empty">暂无相关新闻 | No relevant news</div>'
        else:
            for idx, article in enumerate(articles_list, 1):
                html += f"""
                <div class="article">
                    <h3>[{idx}] {article.get('title', '')}</h3>
                    <div class="article-meta">📅 {article.get('published', 'N/A')}</div>
                    <div class="source-badge">✓ {article.get('source', '')}</div>
                    <p style="font-size: 0.85em; color: #666;">{article.get('credibility', '')}</p>
                    <div style="color: #555; margin: 10px 0;">
                        {article.get('summary', 'No summary')}
                    </div>
                    <a href="{article.get('link', '#')}" class="read-more" target="_blank">📖 阅读原文 | Read Full Article</a>
                </div>
                """
        
        html += '</div>'
    
    html += """
        <div class="footer">
            <p><strong>信息来源声明</strong></p>
            <p>本日报仅收集来自全球顶级新闻机构的信息：彭博社、金融时报、经济学人、华尔街日报、路透社、BBC 等。</p>
            <p style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
                © 2026 Global News Daily | Powered by GitHub Actions
            </p>
        </div>
    </div>
</body>
</html>
    """
    return html

def send_email(recipient, subject, html_content):
    """Send email via SMTP"""
    try:
        logger.info(f"📧 Sending email to {recipient}")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = os.getenv('SMTP_USERNAME')
        msg['To'] = recipient
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Connect to SMTP server
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        logger.info(f"Connecting to {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        logger.info("✅ Email sent successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Email sending failed: {str(e)}")
        raise

def main():
    """Main execution"""
    try:
        logger.info("🔍 Checking environment variables...")
        
        # Check required secrets
        required_vars = ['EMAIL_RECIPIENT', 'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                logger.error(f"❌ Missing environment variable: {var}")
                raise ValueError(f"Missing {var}")
            logger.info(f"✅ {var} is set")
        
        logger.info("\n🔍 Loading configuration...")
        with open('config/news_sources.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info("✅ Configuration loaded")
        
        logger.info("\n🔍 Collecting news from premium sources...")
        articles = collect_news_from_rss(config)
        
        logger.info("\n📧 Generating email report...")
        html_content = generate_email_html(articles, config['categories'])
        
        recipient = os.getenv('EMAIL_RECIPIENT')
        subject = f"📰 全球新闻日报 | Global News Daily - {datetime.now().strftime('%Y-%m-%d')}"
        
        logger.info("\n📧 Sending email...")
        send_email(recipient, subject, html_content)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Task completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
