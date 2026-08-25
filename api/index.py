import os
import sys

# Ensure root directory is on Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app
from database import init_db

# Initialize database on serverless cold start
try:
    init_db()
except Exception as e:
    print("Database init:", e)

# Export Flask app for Vercel WSGI
app.debug = False
