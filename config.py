import sqlite3
TOKEN = '7710896707:AAGqrnNU1qHpUhB3YtN-acJ7n2shCHB21jk'
# Telegram user_id администраторов, которым доступна команда /admin_cons.
ADMIN_IDS = (6650088790,)

conn = sqlite3.connect('users_data.db')
