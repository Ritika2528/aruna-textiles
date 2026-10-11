# Configuration Template
# ========================
# This file shows how to customize the application
# Un-comment and modify values as needed

# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================
DATABASE_NAME = "production_system.db"  # Name of SQLite database
DATABASE_PATH = "./"  # Path where database is stored


# ==========================================================
# FLASK CONFIGURATION
# ==========================================================
FLASK_DEBUG = True  # Enable debug mode (False for production)
FLASK_PORT = 5000  # Server port
FLASK_HOST = "0.0.0.0"  # Server host (0.0.0.0 = accessible from network)
FLASK_SECRET_KEY = "your-secret-key-textile-production"  # Session secret


# ==========================================================
# LOGIN CREDENTIALS (CHANGE THESE!)
# ==========================================================
# Default username for login
DEFAULT_USERNAME = "admin"

# Default password for login
DEFAULT_PASSWORD = "admin123"


# ==========================================================
# APPLICATION SETTINGS
# ==========================================================
# Application name
APP_NAME = "Production Monitoring System"

# Company name
COMPANY_NAME = "Aruna Textiles"

# Application version
APP_VERSION = "1.0"


# ==========================================================
# PRODUCT TYPES (Customize these)
# ==========================================================
PRODUCT_TYPES = [
    "Cotton Yarn",
    "Polyester Blend",
    "Silk Blend",
    "Nylon",
    "Wool Blend"
]


# ==========================================================
# MACHINE TYPES (Customize these)
# ==========================================================
MACHINE_TYPES = [
    "Ring Frame",
    "Carding Machine",
    "Spinning Frame",
    "Winding Machine",
    "Roving Frame",
    "Twisting Machine"
]


# ==========================================================
# ORDER STATUS OPTIONS
# ==========================================================
ORDER_STATUS = ["Pending", "Processing", "Completed"]


# ==========================================================
# PRODUCTION STATUS OPTIONS
# ==========================================================
PRODUCTION_STATUS = ["Completed", "Processing", "Incomplete"]


# ==========================================================
# PAGINATION SETTINGS
# ==========================================================
RECORDS_PER_PAGE = 10  # How many records per page
MAX_SEARCH_RESULTS = 100  # Maximum search results


# ==========================================================
# UI/COLOR CONFIGURATION
# ==========================================================
# You can modify these colors in static/css/style.css
PRIMARY_COLOR = "#1a1a2e"  # Primary background
ACCENT_CYAN = "#00d4ff"  # Cyan accent
ACCENT_GREEN = "#00ff88"  # Green accent (success)
ACCENT_PINK = "#ff6b9d"  # Pink accent (alert)


# ==========================================================
# SAMPLE DATA CONFIGURATION
# ==========================================================
# Set to False if you don't want sample data on first run
INCLUDE_SAMPLE_DATA = True


# ==========================================================
# SESSION CONFIGURATION
# ==========================================================
SESSION_TIMEOUT = 3600  # Session timeout in seconds (1 hour)
PERMANENT_SESSION_LIFETIME = 86400  # 24 hours


# ==========================================================
# API RATE LIMITING (Future Enhancement)
# ==========================================================
# RATE_LIMIT_ENABLED = True
# RATE_LIMIT_REQUESTS = 100  # Max requests
# RATE_LIMIT_WINDOW = 3600   # Per 1 hour


# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================
# LOG_FILE = "app.log"
# LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL


# ==========================================================
# HOW TO USE THIS FILE
# ==========================================================
# 1. Go to app.py
# 2. Uncomment the configuration you want to use
# 3. Restart the application
# 4. Changes will take effect


# ==========================================================
# CUSTOMIZATION EXAMPLES
# ==========================================================

# Example 1: Change Server Port
# ==============================
# In app.py, find the last line:
#   app.run(debug=True, port=5000)
# Change 5000 to your desired port:
#   app.run(debug=True, port=8000)

# Example 2: Disable Debug Mode (Production)
# ===========================================
# In app.py, find:
#   app.run(debug=True, port=5000)
# Change to:
#   app.run(debug=False, port=5000)

# Example 3: Change Login Credentials
# ====================================
# In app.py, find the login route:
#   if username == 'admin' and password == 'admin123':
# Change to:
#   if username == 'yourname' and password == 'yourpass':

# Example 4: Add New Product Type
# ================================
# In customer_form.html, find:
#   <option value="Wool Blend">Wool Blend</option>
# Add new option before closing tag:
#   <option value="Your Product">Your Product</option>

# Example 5: Change Application Name
# ===================================
# In each template, find:
#   ARUNA TEXTILES
# Replace with:
#   YOUR COMPANY NAME
