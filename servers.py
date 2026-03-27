from config import conn
from TEXT.cons_txt import fields, record_buttons



def _soft_delete_slot(cursor, user_id, slot_date, slot_time):
    # Preserve history by soft-deleting active slots.
    cursor.execute(
        """
        UPDATE cons_slots
        SET status = 'deleted'
        WHERE user_id = ? AND slot_date = ? AND slot_time = ? AND status = 'active'
        """,
        (user_id, slot_date, slot_time),
    )


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
    meet_time TEXT,
    records_count INTEGER DEFAULT 0
  )""")


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cons_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            slot_date TEXT NOT NULL,
            slot_time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Index for fast date/time lookups.
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_cons_slots_date_time
        ON cons_slots(slot_date, slot_time)
        """
    )

    # Backfill nulls after migrations.
    cursor.execute(
        "UPDATE users_data SET records_count = 0 WHERE records_count IS NULL"
    )

    conn.commit()
    cursor.close()


def get_active_times(slot_date):
    # Active times for a date to filter inline keyboards.
    cur = conn.cursor()
    cur.execute(
        """
        SELECT slot_time FROM cons_slots
        WHERE slot_date = ? AND status = 'active'
        """,
        (slot_date,),
    )
    rows = cur.fetchall()
    cur.close()
    return [row[0] for row in rows]
def add_cons(data, user_id):
    cur = conn.cursor()

    # If user already had an active slot, soft-delete it before replacing.
    cur.execute(
        """
        SELECT data, meet_time FROM users_data
        WHERE user_id = ?
        """,
        (user_id,),
    )
    prev = cur.fetchone()
    if prev and prev[0] and prev[1]:
        _soft_delete_slot(cur, user_id, prev[0], prev[1])

    # Update current user record and increment confirmation counter.
    cur.execute(
        """
        UPDATE users_data
        SET who = ?, name = ?, phone_number = ?, data = ?, meet_time = ?,
            records_count = COALESCE(records_count, 0) + 1
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

    # Write booking history.
    cur.execute(
        """
        INSERT INTO cons_slots (user_id, slot_date, slot_time, status)
        VALUES (?, ?, ?, 'active')
        """,
        (user_id, data.get('date'), data.get('meet_time')),
    )

    conn.commit()
    cur.close()


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
        "SELECT data, meet_time FROM users_data WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    if row is None or row[0] is None or row[1] is None:
        cursor.close()
        return False

    # Soft-delete the active slot to keep history.
    _soft_delete_slot(cursor, user_id, row[0], row[1])

    cursor.execute("""UPDATE users_data
    SET name=?, who=?, phone_number=?, data=?, meet_time=?
    WHERE user_id=?""", (None,None,None,None,None, user_id))
    conn.commit()
    cursor.close()
    return True
