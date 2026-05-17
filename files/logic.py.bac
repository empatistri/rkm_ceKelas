import sqlite3
import hashlib
import os

USER_DB_NAME = "files/datas/users.db"
SCHEDULE_DB_PATH = "files/datas/cekelas.db"

#hash password
def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt

#init user database
def init_db() -> bool:
    try:
        with sqlite3.connect(USER_DB_NAME) as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False

#init schedule database
def init_schedule_db() -> bool:
    try:
        with sqlite3.connect(SCHEDULE_DB_PATH) as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False

#load schedule data
def load_data_from_db() -> list[dict[str, object]]:
    with sqlite3.connect(SCHEDULE_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT k.nama, j.prodi_matkul, j.mulai, j.selesai "
            "FROM kelas k LEFT JOIN jadwal j ON k.id = j.kelas_id "
            "ORDER BY k.nama, j.mulai"
        )
        rows = cursor.fetchall()

    data_kelas: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        nama_kelas, prodi_matkul, mulai, selesai = row
        if nama_kelas not in data_kelas:
            data_kelas[nama_kelas] = []
        if prodi_matkul:  # jika ada jadwal
            data_kelas[nama_kelas].append({
                "prodi_matkul": prodi_matkul,
                "mulai": mulai,
                "selesai": selesai,
            })

    return [{"nama_kelas": nama, "jadwal": jadwal} for nama, jadwal in data_kelas.items()]

# helper time functions
def str_ke_menit(jam_str: str) -> int:
    jam, menit = jam_str.split(".")
    return int(jam) * 60 + int(menit)


def menit_ke_jamstr(menit_total: int) -> str:
    jam = menit_total // 60
    menit = menit_total % 60
    return f"{jam:02d}.{menit:02d}"


def durasi_label(selisih_menit: int) -> str:
    jam = selisih_menit // 60
    menit = selisih_menit % 60
    if jam > 0 and menit > 0:
        return f"{jam} jam {menit} menit"
    elif jam > 0:
        return f"{jam} jam"
    else:
        return f"{menit} menit"


def cek_status(jadwal_list: list[dict[str, str]], sekarang_menit: int) -> dict[str, str] | None:
    for jadwal in jadwal_list:
        mulai = str_ke_menit(jadwal["mulai"])
        selesai = str_ke_menit(jadwal["selesai"])
        if mulai <= sekarang_menit < selesai:
            return jadwal
    return None


def jadwal_berikutnya(jadwal_list: list[dict[str, str]], sekarang_menit: int) -> dict[str, str] | None:
    """Cari jadwal pertama yang mulainya > sekarang"""
    jadwal_sorted = sorted(jadwal_list, key=lambda j: str_ke_menit(j["mulai"]))
    for jadwal in jadwal_sorted:
        if str_ke_menit(jadwal["mulai"]) > sekarang_menit:
            return jadwal
    return None


def semua_jadwal_hari_ini(jadwal_list: list[dict[str, str]]) -> list[dict[str, str]]:
    """Kembalikan semua jadwal diurutkan dari pagi"""
    return sorted(jadwal_list, key=lambda j: str_ke_menit(j["mulai"]))

# #fungsi register - belum fix
# def register(username: str, password: str) -> bool:
#     hashed, salt = hash_password(password)
#     try:
#         with sqlite3.connect(DB_NAME) as conn:
#             conn.execute(
#                 "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
#                 (username, hashed, salt)
#             )
#             conn.commit()
#         print(f"[✓] User '{username}' registered successfully.")
#         return True
#     except sqlite3.IntegrityError:
#         print(f"[✗] Username '{username}' already exists.")
#         return False

#fungsi login
def login(username: str, password: str) -> bool:
    with sqlite3.connect(USER_DB_NAME) as conn:
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

if __name__ == "__main__":
    init_db()