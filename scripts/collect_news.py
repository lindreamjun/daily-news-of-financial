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
    email_recipient = os.getenv('EMAIL_RECIPIENT')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    log_write(f"EMAIL_RECIPIENT: {email_recipient}")
    log_write(f"SMTP_SERVER: {smtp_server}")
    log_write(f"SMTP_PORT: {smtp_port}")
    log_write(f"SMTP_USERNAME: {smtp_username}")
    log_write(f"SMTP_PASSWORD: {'SET' if smtp_password else 'NOT SET'}")
    
    if not all([email_recipient, smtp_server, smtp_port, smtp_username, smtp_password]):
        raise ValueError("❌ Missing required environment variables!")
    
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
    
    # Generate simple email
    log_write("\n=== STEP 3: GENERATING EMAIL ===")
    html_content = f"""
    <html>
    <head><meta charset="UTF-8"></head>
    <body>
        <h1>📰 全球新闻日报</h1>
        <p>Global News Daily Digest</p>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
        <h2>✅ 系统测试成功！System Test Successful!</h2>
        <p>配置已加载 | Configuration loaded successfully</p>
        <p>新闻源数量: {sources_count}</p>
        <p>分类数量: {categories_count}</p>
        <p>This is a test email to verify the system is working.</p>
        <hr>
        <p style="font-size: 0.9em; color: #666;">© 2026 Global News Daily | Powered by GitHub Actions</p>
    </body>
    </html>
    """
    log_write("✅ Email HTML generated")
    
    # Send email
    log_write("\n=== STEP 4: SENDING EMAIL ===")
    log_write(f"📧 Connecting to {smtp_server}:{smtp_port}")
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📰 全球新闻日报 测试 | Global News Daily Test - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = smtp_username
    msg['To'] = email_recipient
    
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    log_write(f"📧 Creating SMTP connection...")
    server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
    log_write(f"✅ Connected to SMTP server")
    
    log_write(f"🔒 Starting TLS...")
    server.starttls()
    log_write(f"✅ TLS started")
    
    log_write(f"🔑 Logging in as {smtp_username}...")
    server.login(smtp_username, smtp_password)
    log_write(f"✅ Login successful")
    
    log_write(f"📤 Sending email to {email_recipient}...")
    server.send_message(msg)
    log_write(f"✅ Email sent successfully!")
    
    server.quit()
    log_write(f"✅ Connection closed")
    
    log_write("\n" + "=" * 80)
    log_write("✅ ALL STEPS COMPLETED SUCCESSFULLY")
    log_write("=" * 80)

except Exception as e:
    log_write(f"\n❌ ERROR: {str(e)}")
    log_write(f"Error type: {type(e).__name__}")
    import traceback
    log_write(traceback.format_exc())
    sys.exit(1)
