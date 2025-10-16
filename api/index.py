"""
Vercel serverless function entry point.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from wsgi import app

# Vercel expects 'app' or 'handler'
handler = app
