import sqlite3
import hashlib
from paths import get_db_path


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, password, role="staff"):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        "SELECT role FROM users WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    )

    user = cur.fetchone()
    conn.close()
    return user  # ('admin',) or None

