import sqlite3
db_name = "sessions.db"
def init_db():
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            target_ip TEXT NOT NULL,
            target_port INTEGER NOT NULL,
            status TEXT DEFAULT 'active'
            )''')
        cur.execute("UPDATE sessions SET status = 'closed' WHERE status = 'active'")
        conn.commit()
def register_session(session_type: str,ip: str,port: int) -> int:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO sessions (type,target_ip,target_port) VALUES (?,?,?)",(session_type,ip,port))
        conn.commit()
        return cur.lastrowid
def close_session_in_db(session_id: int):
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE sessions SET status = 'closed' WHERE session_id = ?",(session_id,))
        conn.commit()
def get_active_sessions():
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("SELECT session_id,type,target_ip,target_port FROM sessions WHERE status = 'active'")
        return cur.fetchall()