"""
WSGI configuration for PythonAnywhere deployment
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/daily-report-system'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import Flask app
from app import create_app

application = create_app()

# For debugging
if __name__ == "__main__":
    application.run()