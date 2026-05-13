#!/usr/bin/env python3
"""
Minimal test script to verify setup
"""

import os
import sys
from pathlib import Path

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Write test log
log_file = log_dir / "test.log"
with open(log_file, 'w') as f:
    f.write("=== NEWS COLLECTION TEST ===\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Current directory: {os.getcwd()}\n")
    f.write(f"Files in repo:\n")
    for item in Path(".").iterdir():
        f.write(f"  - {item}\n")
    
    f.write("\n=== ENVIRONMENT VARIABLES ===\n")
    f.write(f"EMAIL_RECIPIENT: {os.getenv('EMAIL_RECIPIENT', 'NOT SET')}\n")
    f.write(f"SMTP_SERVER: {os.getenv('SMTP_SERVER', 'NOT SET')}\n")
    f.write(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'NOT SET')}\n")
    f.write(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME', 'NOT SET')}\n")
    f.write(f"SMTP_PASSWORD: {'SET' if os.getenv('SMTP_PASSWORD') else 'NOT SET'}\n")
    
    f.write("\n=== TESTING IMPORTS ===\n")
    
    try:
        import json
        f.write("✅ json imported\n")
    except Exception as e:
        f.write(f"❌ json failed: {e}\n")
    
    try:
        import feedparser
        f.write("✅ feedparser imported\n")
    except Exception as e:
        f.write(f"❌ feedparser failed: {e}\n")
    
    try:
        import smtplib
        f.write("✅ smtplib imported\n")
    except Exception as e:
        f.write(f"❌ smtplib failed: {e}\n")
    
    f.write("\n=== LOADING CONFIG ===\n")
    try:
        with open('config/news_sources.json', 'r') as cf:
            config = json.load(cf)
        f.write("✅ Config loaded successfully\n")
        f.write(f"Sources found: {len(config.get('premium_sources', {}))}\n")
        f.write(f"Categories found: {len(config.get('categories', {}))}\n")
    except Exception as e:
        f.write(f"❌ Config loading failed: {e}\n")
    
    f.write("\n=== TEST COMPLETED ===\n")

print("✅ Test log created at logs/test.log")
print("Script execution successful!")
