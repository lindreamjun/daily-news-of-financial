#!/usr/bin/env python3
"""
Premium News Collection & Email Distribution System
"""

import os
import sys
import json
import smtplib
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Write detailed log
log_file = log_dir / f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log_write(message):
    """Write to both console and file"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + "\n")

try:
    log_write("=" * 80)
    log_write("🚀 NEWS COLLECTION AND EMAIL SENDING")
    log_write("=" * 80)
    
    # Check environment variables
    log_write("\n=== STEP 1: CHECKING ENVIRONMENT VARIABLES ===")
    email_recipient = os.getenv('EMAIL_RECIPIENT', '').strip()
    smtp_server = os.getenv('SMTP_SERVER', '').strip()
    smtp_port = os.getenv('SMTP_PORT', '').strip()
    smtp_username = os.getenv('SMTP_USERNAME', '').strip()
    smtp_password = os.getenv('SMTP_PASSWORD', '').strip()
    
    log_write(f"EMAIL_RECIPIENT: {email_recipient if email_recipient else 'NOT SET'}")
    log_write(f"SMTP_SERVER: {smtp_server if smtp_server else 'NOT SET'}")
    log_write(f"SMTP_PORT: {smtp_port if smtp_port else 'NOT SET'}")
    log_write(f"SMTP_USERNAME: {smtp_username if smtp_username else 'NOT SET'}")
    log_write(f"SMTP_PASSWORD: {'SET' if smtp_password else 'NOT SET'}")
    
    # Validate
    if not email_recipient:
        raise ValueError("❌ EMAIL_RECIPIENT not set")
    if not smtp_username:
        raise ValueError("❌ SMTP_USERNAME not set")
    if not smtp_password:
        raise ValueError("❌ SMTP_PASSWORD not set")
    
    log_write(f"\n✅ All required variables are set")
    
    # Load config
    log_write("\n=== STEP 2: LOADING CONFIGURATION ===")
    config_path = Path('config/news_sources.json')
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    sources_count = len(config.get('premium_sources', {}))
    categories_count = len(config.get('categories', {}))
    log_write(f"✅ Config loaded: {sources_count} sources, {categories_count} categories")
    
    # Import feedparser
    log_write("\n=== STEP 3: COLLECTING NEWS ===")
    try:
        import feedparser
        log_write("✅ feedparser module loaded")
        
        all_articles = {}
        total_articles = 0
        
        for category_key, category_info in config.get('categories', {}).items():
            category_name = category_info.get('name', '')
            log_write(f"\n  📂 {category_name}")
            all_articles[category_key] = []
            
            sources = category_info.get('sources', [])
            for source_name in sources:
                source_info = config['premium_sources'].get(source_name, {})
                rss_feed = source_info.get('rss_feed')
                
                if not rss_feed:
                    continue
                
                try:
                    feed = feedparser.parse(rss_feed)
                    count = 0
                    for entry in feed.entries[:10]:
                        if count >= 3:
                            break
                        article = {
                            'title': entry.get('title', 'No title'),
                            'link': entry.get('link', ''),
                            'source': source_name
                        }
                        if article['title'] and article['link']:
                            all_articles[category_key].append(article)
                            count += 1
                            total_articles += 1
                    
                    if count > 0:
                        log_write(f"    ✅ {source_name}: {count} articles")
                except Exception as e:
                    log_write(f"    ⚠️ {source_name}: {str(e)[:50]}")
        
        log_write(f"\n✅ Total articles collected: {total_articles}")
        
    except ImportError as e:
        log_write(f"⚠️ feedparser import failed: {e}")
        all_articles = {}
    
    # Generate email
    log_write("\n=== STEP 4: GENERATING EMAIL ===")
    
    html_content = f"""
    <html>
    <head><meta charset="UTF-8"><style>
    body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; }}
    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 2em; }}
    .category {{ background: #f9f9f9; margin: 20px 0; padding: 15px; border-left: 4px solid #667eea; }}
    .article {{ background: white; margin: 10px 0; padding: 10px; border: 1px solid #e0e0e0; }}
    .article a {{ color: #667eea; text-decoration: none; }}
    .footer {{ text-align: center; color: #666; font-size: 0.9em; margin-top: 30px; }}
    </style></head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📰 全球新闻日报</h1>
                <p>Global News Daily Digest</p>
                <p>{datetime.now().strftime('%Y年%m月%d日 | %B %d, %Y')}</p>
            </div>
    """
    
    if all_articles:
        for category_key, category_info in config.get('categories', {}).items():
            category_name = category_info.get('name', '')
            articles = all_articles.get(category_key, [])
            
            html_content += f'<div class="category"><h2>{category_name}</h2>'
            
            if not articles:
                html_content += '<p style="color: #999;">暂无新闻 | No news</p>'
            else:
                for idx, article in enumerate(articles, 1):
                    html_content += f"""
                    <div class="article">
                        <strong>[{idx}] {article.get('title', '')}</strong><br>
                        <small>Source: {article.get('source', '')}</small><br>
                        <a href="{article.get('link', '#')}" target="_blank">📖 阅读原文 | Read More</a>
                    </div>
                    """
            
            html_content += '</div>'
    else:
        html_content += '<p style="color: #999; padding: 20px;">暂无新闻 | No news available</p>'
    
    html_content += """
            <div class="footer">
                <p>本日报仅供参考 | This digest is for reference only</p>
                <p>© 2026 Global News Daily | Powered by GitHub Actions</p>
            </div>
        </div>
    </body>
    </html>
    """
    log_write("✅ Email HTML generated")
    
    # Send email
    log_write("\n=== STEP 5: SENDING EMAIL ===")
    log_write(f"📧 Target email: {email_recipient}")
    log_write(f"📧 From account: {smtp_username}")
    log_write(f"📧 Server: {smtp_server}:{smtp_port}")
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📰 全球新闻日报 | Global News Daily - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = smtp_username
    msg['To'] = email_recipient
    
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    log_write(f"🔗 Connecting to SMTP server...")
    server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
    log_write(f"✅ Connected")
    
    log_write(f"🔒 Starting TLS...")
    server.starttls()
    log_write(f"✅ TLS started")
    
    log_write(f"🔑 Authenticating...")
    # IMPORTANT: Ensure credentials are ASCII-safe
    # For Gmail, use 16-character app password (not account password)
    server.login(smtp_username.encode('utf-8').decode('ascii'), smtp_password.encode('utf-8').decode('ascii'))
    log_write(f"✅ Authentication successful")
    
    log_write(f"📤 Sending email...")
    result = server.send_message(msg)
    log_write(f"✅ Email sent")
    
    server.quit()
    log_write(f"✅ Connection closed")
    
    log_write("\n" + "=" * 80)
    log_write("✅ SUCCESS! Email sent to " + email_recipient)
    log_write("=" * 80)

except Exception as e:
    log_write(f"\n❌ ERROR: {str(e)}")
    log_write(f"Error type: {type(e).__name__}")
    import traceback
    log_write(traceback.format_exc())
    
    log_write("\n💡 TROUBLESHOOTING:")
    log_write("   1. For Gmail: Use 16-character APP PASSWORD (not account password)")
    log_write("   2. Generate new password at: https://myaccount.google.com/apppasswords")
    log_write("   3. Update SMTP_PASSWORD secret with the new password")
    log_write("   4. Ensure SMTP_USERNAME and EMAIL_RECIPIENT use same Gmail account")
    
    sys.exit(1)
