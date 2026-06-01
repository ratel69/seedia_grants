"""
Uruchamia jednorazowy scan wszystkich źródeł.
Użycie: python run_scan.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crawlers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scheduler'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from scanner import run_daily_scan
run_daily_scan()
