#!/usr/bin/env python3
"""
Minimal test script to verify setup
"""

import os
import sys
import json
from pathlib import Path

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Write test log
log_file = log_dir / "test.log"
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=== NEWS COLLECTION TEST ===\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Current directory: {os.getcwd()}\n")
    
    f.write("\nFiles in repo:\n")
    for item in Path(".").iterdir():
        f.write(f"  - {item}\n")
    
    f.write("\n=== CHECKING CONFIG FILE ===\n")
    config_path = Path('config/news_sources.json')
    if config_path.exists():
        f.write("✅ Config file exists\n")
        try:
            with open(config_path, 'r', encoding='utf-8') as cf:
                config = json.load(cf)
            f.write(f"✅ Config loaded: {len(config.get('premium_sources', {}))} sources, {len(config.get('categories', {}))} categories\n")
        except Exception as e:
            f.write(f"❌ Config load error: {str(e)}\n")
    else:
        f.write("❌ Config file NOT found\n")
    
    f.write("\n=== CHECKING ENVIRONMENT ===\n")
    vars_to_check = ['EMAIL_RECIPIENT', 'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']
    for var in vars_to_check:
        value = os.getenv(var)
        status = "✅ SET" if value else "❌ NOT SET"
        f.write(f"{var}: {status}\n")
    
    f.write("\n✅ TEST COMPLETE\n")

print("✅ Test completed! Check logs/test.log")
