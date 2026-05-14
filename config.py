import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# --- Environment Management ---
ENV = os.getenv("TEST_ENV", "STAGING").upper()

ENVIRONMENTS = {
    "STAGING": {
        "url": os.getenv("BASE_URL", "https://www.saucedemo.com/"),
        "user": os.getenv("USERNAME", "standard_user"),
        "pass": os.getenv("PASSWORD", "secret_sauce")
    }
}

# --- Core Settings ---
BASE_URL = ENVIRONMENTS[ENV]["url"]
USERNAME = ENVIRONMENTS[ENV]["user"]
PASSWORD = ENVIRONMENTS[ENV]["pass"]

# --- Browser/Performance Settings ---
HEADLESS = os.getenv("HEADLESS", "True").lower() == "true"
IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", 5))
EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", 10))
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", 30))

# --- Industrial Execution ---
PARALLEL_WORKERS = int(os.getenv("PARALLEL_WORKERS", 4))
RETRIES = int(os.getenv("RETRIES", 2))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
