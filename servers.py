from config import conn
from TEXT.cons_txt import fields, record_buttons


def create_important_events_table():
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS important_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            description TEXT,
            link TEXT,
            button_text TEXT,
            is_active INTEGER DEFAULT 1
        )
        """
    )
    conn.commit()
    cursor.close()


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


def _is_slot_busy(cursor, slot_date, slot_time, excluded_cons_id=None):
    if excluded_cons_id is None:
        cursor.execute(
            """
            SELECT 1 FROM cons_slots
            WHERE slot_date = ? AND slot_time = ? AND status = 'active'
            LIMIT 1
            """,
            (slot_date, slot_time),
        )
    else:
        cursor.execute(
            """
            SELECT 1 FROM cons_slots
            WHERE slot_date = ? AND slot_time = ? AND status = 'active' AND id != ?
            LIMIT 1
            """,
            (slot_date, slot_time, excluded_cons_id),
        )
    return cursor.fetchone() is not None


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
    create_important_events_table()


def get_active_times(slot_date, excluded_cons_id=None):
    # Active times for a date to filter inline keyboards.
    cur = conn.cursor()
    if excluded_cons_id is None:
        cur.execute(
            """
            SELECT slot_time FROM cons_slots
            WHERE slot_date = ? AND status = 'active'
            """,
            (slot_date,),
        )
    else:
        cur.execute(
            """
            SELECT slot_time FROM cons_slots
            WHERE slot_date = ? AND status = 'active' AND id != ?
            """,
            (slot_date, excluded_cons_id),
        )
    rows = cur.fetchall()
    cur.close()
    return [row[0] for row in rows]


def get_user_active_booking(user_id):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT cs.id,
               COALESCE(ud.name, ''),
               COALESCE(ud.who, ''),
               COALESCE(ud.phone_number, ''),
               cs.slot_date,
               cs.slot_time
        FROM cons_slots cs
        LEFT JOIN users_data ud ON ud.user_id = cs.user_id
        WHERE cs.user_id = ? AND cs.status = 'active'
        ORDER BY cs.id DESC
        LIMIT 1
        """,
        (user_id,),
    )
    row = cur.fetchone()
    cur.close()
    return row


def add_cons(data, user_id, replaced_cons_id=None):
    cur = conn.cursor()
    slot_date = data.get('date')
    slot_time = data.get('meet_time')
    active_booking = get_user_active_booking(user_id)

    if replaced_cons_id is None and active_booking is not None:
        cur.close()
        return 'has_active'

    if replaced_cons_id is not None:
        if active_booking is None or active_booking[0] != replaced_cons_id:
            cur.close()
            return 'missing_old'

    if _is_slot_busy(cur, slot_date, slot_time, replaced_cons_id):
        cur.close()
        return 'slot_taken'

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

    if replaced_cons_id is not None:
        cur.execute(
            """
            UPDATE cons_slots
            SET status = 'deleted'
            WHERE id = ? AND status = 'active'
            """,
            (replaced_cons_id,),
        )

    cur.execute(
        """
        INSERT INTO cons_slots (user_id, slot_date, slot_time, status)
        VALUES (?, ?, ?, 'active')
        """,
        (user_id, data.get('date'), data.get('meet_time')),
    )

    conn.commit()
    cur.close()
    return 'ok'


def get_user_cons(lang, user_id):
    row = get_user_active_booking(user_id)
    if row is None:
        return record_buttons[lang]['view_records']['no_record']
    _, name, who, phone_number, data, meet_time = row
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
    active_booking = get_user_active_booking(user_id)
    if active_booking is None:
        cursor.close()
        return False

    _soft_delete_slot(cursor, user_id, active_booking[4], active_booking[5])

    cursor.execute("""UPDATE users_data
    SET name=?, who=?, phone_number=?, data=?, meet_time=?
    WHERE user_id=?""", (None,None,None,None,None, user_id))
    conn.commit()
    cursor.close()
    return True


def get_active_consultations_count():
    # Считаем все активные записи для пагинации в админском списке.
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM cons_slots
        WHERE status = 'active'
        """
    )
    count = cursor.fetchone()[0]
    cursor.close()
    return count


def get_active_consultations_page(page, page_size=5):
    # Получаем одну страницу активных записей с именем пользователя из users_data.
    offset = max(page - 1, 0) * page_size
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT cs.id,
               cs.slot_date,
               cs.slot_time,
               cs.user_id,
               COALESCE(ud.name, '')
        FROM cons_slots cs
        LEFT JOIN users_data ud ON ud.user_id = cs.user_id
        WHERE cs.status = 'active'
        ORDER BY cs.slot_date ASC, cs.slot_time ASC
        LIMIT ? OFFSET ?
        """,
        (page_size, offset),
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_consultation_by_id(cons_id):
    # Получаем полную карточку одной записи для админского просмотра.
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT cs.id,
               COALESCE(ud.name, ''),
               COALESCE(ud.phone_number, ''),
               cs.user_id,
               cs.slot_date,
               cs.slot_time,
               cs.status
        FROM cons_slots cs
        LEFT JOIN users_data ud ON ud.user_id = cs.user_id
        WHERE cs.id = ?
        LIMIT 1
        """,
        (cons_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row


def update_consultation_status(cons_id, status):
    # Меняем статус только у активной записи, чтобы не трогать уже обработанные записи.
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE cons_slots
        SET status = ?
        WHERE id = ? AND status = 'active'
        """,
        (status, cons_id),
    )
    updated = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    return updated


def add_important_event(title, event_date, description, link=None, button_text=None):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO important_events (title, event_date, description, link, button_text)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, event_date, description, link, button_text),
    )
    conn.commit()
    cursor.close()


def get_unique_user_ids():
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT DISTINCT user_id
        FROM users_data
        WHERE user_id IS NOT NULL
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    return [row[0] for row in rows]


def get_active_important_events():
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, event_date, description, link, button_text, is_active
        FROM important_events
        WHERE is_active = 1
        ORDER BY event_date ASC, id ASC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_important_event_by_id(event_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, event_date, description, link, button_text, is_active
        FROM important_events
        WHERE id = ?
        LIMIT 1
        """,
        (event_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row


def deactivate_important_event(event_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE important_events
        SET is_active = 0
        WHERE id = ? AND is_active = 1
        """,
        (event_id,),
    )
    updated = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    return updated
