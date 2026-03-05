import sqlite3
import hashlib
import os
import streamlit as st

#folder db.users
DB_NAME = "files/users.db"

#hash password
def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt

#init database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    UNIQUE NOT NULL,
                password TEXT    NOT NULL,
                salt     TEXT    NOT NULL
            )
        """)
        conn.commit()

#fungsi register - belum fix
def register(username: str, password: str) -> bool:
    hashed, salt = hash_password(password)
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
                (username, hashed, salt)
            )
            conn.commit()
        print(f"[✓] User '{username}' registered successfully.")
        return True
    except sqlite3.IntegrityError:
        print(f"[✗] Username '{username}' already exists.")
        return False

#fungsi login
def login(username: str, password: str) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute(
            "SELECT password, salt FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    if row is None:
        print("[✗] User not found.")
        return False

    stored_hash, salt = row
    attempt_hash, _ = hash_password(password, salt)

    if attempt_hash == stored_hash:
        print(f"[✓] Login successful! Welcome, {username}.")
        return True
    else:
        print("[✗] Incorrect password.")
        return False

#sekalian konfigurasi
st.set_page_config(
    page_title="ceKelas.1",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if __name__ == "__main__":
    init_db()