import sqlite3
import hashlib
import os

USER_DB_NAME      = "files/datas/users.db"
SCHEDULE_DB_PATH  = "files/datas/cekelas.db"


# ── Password hashing ──────────────────────────────────────────────────────────
def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt


# ── DB init checks ────────────────────────────────────────────────────────────
def init_db() -> bool:
    try:
        with sqlite3.connect(USER_DB_NAME) as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False


def init_schedule_db() -> bool:
    try:
        with sqlite3.connect(SCHEDULE_DB_PATH) as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False


# ── Load jadwal dari DB — sekarang filter by hari ────────────────────────────
def load_data_from_db(hari: str) -> list[dict[str, object]]:
    """
    Ambil semua kelas beserta jadwal yang berlaku pada `hari` tertentu.
    `hari` berformat: "Senin", "Selasa", ..., "Sabtu"
    """
    with sqlite3.connect(SCHEDULE_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT k.nama, j.prodi_matkul, j.mulai, j.selesai "
            "FROM kelas k "
            "LEFT JOIN jadwal j ON k.id = j.kelas_id AND j.hari = ? "
            "ORDER BY k.nama, j.mulai",
            (hari,)
        )
        rows = cursor.fetchall()

    data_kelas: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        nama_kelas, prodi_matkul, mulai, selesai = row
        if nama_kelas not in data_kelas:
            data_kelas[nama_kelas] = []
        if prodi_matkul:   # ada jadwal di hari ini
            data_kelas[nama_kelas].append({
                "prodi_matkul": prodi_matkul,
                "mulai":        mulai,
                "selesai":      selesai,
            })

    return [{"nama_kelas": nama, "jadwal": jadwal}
            for nama, jadwal in data_kelas.items()]


# ── Helper: waktu ─────────────────────────────────────────────────────────────
def str_ke_menit(jam_str: str) -> int:
    """'07.30' → 450"""
    jam, menit = jam_str.split(".")
    return int(jam) * 60 + int(menit)


def menit_ke_jamstr(menit_total: int) -> str:
    """450 → '07.30'"""
    return f"{menit_total // 60:02d}.{menit_total % 60:02d}"


def durasi_label(selisih_menit: int) -> str:
    """450 → '7 jam 30 menit'"""
    jam   = selisih_menit // 60
    menit = selisih_menit % 60
    if jam > 0 and menit > 0:
        return f"{jam} jam {menit} menit"
    elif jam > 0:
        return f"{jam} jam"
    else:
        return f"{menit} menit"


# ── Core logic ────────────────────────────────────────────────────────────────
def cek_status(
    jadwal_list: list[dict[str, str]],
    sekarang_menit: int
) -> dict[str, str] | None:
    """
    Kembalikan jadwal yang sedang aktif sekarang, atau None kalau kosong.
    Jadwal sudah difilter by hari saat load, jadi tidak perlu filter ulang.
    """
    for jadwal in jadwal_list:
        mulai   = str_ke_menit(jadwal["mulai"])
        selesai = str_ke_menit(jadwal["selesai"])
        if mulai <= sekarang_menit < selesai:
            return jadwal
    return None


def jadwal_berikutnya(
    jadwal_list: list[dict[str, str]],
    sekarang_menit: int
) -> dict[str, str] | None:
    """Jadwal pertama yang belum mulai (mulai > sekarang)."""
    jadwal_sorted = sorted(jadwal_list, key=lambda j: str_ke_menit(j["mulai"]))
    for jadwal in jadwal_sorted:
        if str_ke_menit(jadwal["mulai"]) > sekarang_menit:
            return jadwal
    return None


def semua_jadwal_hari_ini(
    jadwal_list: list[dict[str, str]]
) -> list[dict[str, str]]:
    """
    Kembalikan semua jadwal diurutkan dari pagi.
    Sudah otomatis hanya berisi jadwal hari ini karena difilter saat load.
    """
    return sorted(jadwal_list, key=lambda j: str_ke_menit(j["mulai"]))


# ── Auth ──────────────────────────────────────────────────────────────────────
def login(username: str, password: str) -> bool:
    with sqlite3.connect(USER_DB_NAME) as conn:
        row = conn.execute(
            "SELECT password, salt FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    if row is None:
        return False

    stored_hash, salt = row
    attempt_hash, _   = hash_password(password, salt)
    return attempt_hash == stored_hash


if __name__ == "__main__":
    init_db()