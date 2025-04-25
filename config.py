# config.py

import os
from dotenv import load_dotenv

load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
SPACE_KEY = os.getenv("SPACE_KEY")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./smartis")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
ASSISTIANT_ID = os.getenv("ASSISTIANT_ID")
VECTORE_ID = os.getenv("VECTORE_ID")
BOT_TOKEN=os.getenv("BOT_TOKEN")
