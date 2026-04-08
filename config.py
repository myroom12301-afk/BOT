import sqlite3
TOKEN = ''
# Telegram user_id администраторов, которым доступна команда /admin_cons.
ADMIN_IDS = (6650088790,)

conn = sqlite3.connect('users_data.db')
