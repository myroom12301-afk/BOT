from config import conn
from TEXT.cons_txt import fields,record_buttons
def init_db():
    cursor = conn.cursor()
    cursor.execute("""create table IF NOT EXISTS users_data
                      (
    id           INTEGER
        primary key autoincrement,
    user_id      INTEGER,
    language     TEXT   DEFAULT NULL,
    who          TEXT DEFAULT NULL,
    name         TEXT,
    phone_number integer,
    data TEXT,
    meet_time TEXT
  )""")

    conn.commit()
    cursor.close()
def add_cons(data, user_id):
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users_data
        SET who = ?, name = ?, phone_number = ?, data = ?, meet_time = ?
        WHERE user_id = ?
        """,
        (
            data.get('who'),
            data.get('name'),
            data.get('number'),
            data.get('date'),
            data.get('meet_time'),
            user_id
        )
    )

    conn.commit()


def get_user_cons(lang, user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT name, who, phone_number, data, meet_time
        FROM users_data
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    if row is None or row[3] is None:
        return record_buttons[lang]['view_records']['no_record']
    name, who, phone_number, data, meet_time = row
    text = (
        f"{fields[lang]['name']}: {name}\n"
        f"{fields[lang]['who']}: {who}\n"
        f"{fields[lang]['phone']}: {'0'+str(phone_number)}\n"
        f"{fields[lang]['date']}: {data}\n"
        f"{fields[lang]['time']}: {meet_time}"
    )
    return text

def add_user(user_id, language):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users_data WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute(
            "INSERT INTO users_data (user_id, language) VALUES (?, ?)",
            (user_id, language))
    else:
        cursor.execute(
            "UPDATE users_data SET language = ? WHERE user_id = ?",
            (language, user_id))
    conn.commit()
    cursor.close()

def get_user_language(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users_data WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def del_cons(user_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT data FROM users_data WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    if row is None or row[0] is None:
        cursor.close()
        return False
    cursor.execute("""UPDATE users_data
    SET name=?, who=?, phone_number=?, data=?, meet_time=?
    WHERE user_id=?""", (None,None,None,None,None, user_id))
    conn.commit()
    cursor.close()
    return True
