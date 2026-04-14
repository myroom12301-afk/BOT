import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TELEGRAM_TOKEN')
# Telegram user_id администраторов, которым доступна команда /admin_cons.
ADMIN_IDS = (6650088790,)

conn = sqlite3.connect('users_data.db')
