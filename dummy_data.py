"""
init_db.py
Jalankan sekali untuk membuat dan mengisi database ceKelas.
Usage: python init_db.py
"""

import sqlite3
import os

SCHEDULE_DB_PATH = "files/datas/cekelas.db"
USER_DB_PATH     = "files/datas/users.db"

os.makedirs("files/datas", exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# 1. SCHEDULE DATABASE
# ══════════════════════════════════════════════════════════════════════════════
def init_schedule_db():
    with sqlite3.connect(SCHEDULE_DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS kelas (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT    NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS jadwal (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                kelas_id     INTEGER NOT NULL,
                hari         TEXT    NOT NULL,
                prodi_matkul TEXT    NOT NULL,
                mulai        TEXT    NOT NULL,
                selesai      TEXT    NOT NULL,
                FOREIGN KEY (kelas_id) REFERENCES kelas(id)
            );
        """)
    print("[✓] Tabel schedule DB dibuat.")


# ══════════════════════════════════════════════════════════════════════════════
# 2. USER DATABASE
# ══════════════════════════════════════════════════════════════════════════════
def init_user_db():
    with sqlite3.connect(USER_DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL,
                salt     TEXT    NOT NULL
            );
        """)
    print("[✓] Tabel user DB dibuat.")


# ══════════════════════════════════════════════════════════════════════════════
# 3. SEED DATA
#
# Kelas : 3S.1–3S.8  dan  4S.1–4S.9  (total 17 ruang)
# Hari  : Senin, Selasa, Rabu, Kamis, Sabtu
# Libur : Jumat & Minggu — tidak ada entri jadwal sama sekali
#
# Beberapa kelas sengaja tidak punya jadwal di hari tertentu
# supaya ada simulasi "kelas kosong" yang realistis.
#
# Format: (nama_kelas, hari, prodi_matkul, mulai, selesai)
# ══════════════════════════════════════════════════════════════════════════════
SEED_JADWAL = [

    # ── 3S.1 ── Senin, Rabu, Kamis  |  kosong: Selasa, Sabtu
    ("3S.1", "Senin",   "Informatika - Pemrograman Web",             "07.00", "08.40"),
    ("3S.1", "Senin",   "Informatika - Struktur Data",               "09.00", "10.40"),
    ("3S.1", "Rabu",    "Sistem Informasi - Basis Data",             "10.50", "12.30"),
    ("3S.1", "Rabu",    "Sistem Informasi - Pemrograman Mobile",     "13.00", "14.40"),
    ("3S.1", "Kamis",   "Informatika - Jaringan Komputer",           "08.00", "09.40"),

    # ── 3S.2 ── Senin, Selasa, Sabtu  |  kosong: Rabu, Kamis
    ("3S.2", "Senin",   "Akuntansi - Pengantar Akuntansi",           "08.50", "10.30"),
    ("3S.2", "Selasa",  "Manajemen - Pengantar Manajemen",           "07.00", "08.40"),
    ("3S.2", "Selasa",  "Manajemen - Perilaku Organisasi",           "10.50", "12.30"),
    ("3S.2", "Sabtu",   "Akuntansi - Perpajakan",                    "07.00", "09.30"),
    ("3S.2", "Sabtu",   "Akuntansi - Akuntansi Biaya",               "10.00", "12.30"),

    # ── 3S.3 ── Senin, Selasa, Kamis  |  kosong: Rabu, Sabtu
    ("3S.3", "Senin",   "Matematika - Kalkulus Lanjut",              "10.50", "12.30"),
    ("3S.3", "Selasa",  "Fisika - Fisika Dasar",                     "09.00", "10.40"),
    ("3S.3", "Selasa",  "Fisika - Termodinamika",                    "13.00", "14.40"),
    ("3S.3", "Kamis",   "Matematika - Aljabar Linear",               "07.00", "08.40"),
    ("3S.3", "Kamis",   "Matematika - Statistika Inferensial",       "09.00", "10.40"),

    # ── 3S.4 ── Selasa, Rabu, Sabtu  |  kosong: Senin, Kamis
    ("3S.4", "Selasa",  "Teknik Industri - Sistem Produksi",         "10.50", "12.30"),
    ("3S.4", "Rabu",    "Teknik Industri - Manajemen Kualitas",      "08.50", "10.30"),
    ("3S.4", "Rabu",    "Teknik Industri - Ergonomi",                "13.00", "14.40"),
    ("3S.4", "Sabtu",   "Teknik Industri - Keselamatan Kerja",       "07.00", "09.30"),

    # ── 3S.5 ── Senin, Kamis  |  kosong: Selasa, Rabu, Sabtu
    ("3S.5", "Senin",   "Komunikasi - Pengantar Komunikasi",         "13.00", "14.40"),
    ("3S.5", "Kamis",   "Komunikasi - Komunikasi Massa",             "09.00", "10.40"),
    ("3S.5", "Kamis",   "Komunikasi - Jurnalistik Dasar",            "13.00", "14.40"),

    # ── 3S.6 ── Rabu, Kamis, Sabtu  |  kosong: Senin, Selasa
    ("3S.6", "Rabu",    "Ekonomi - Makroekonomi",                    "07.00", "08.40"),
    ("3S.6", "Rabu",    "Ekonomi - Ekonomi Pembangunan",             "10.50", "12.30"),
    ("3S.6", "Kamis",   "Ekonomi - Mikroekonomi",                    "08.00", "09.40"),
    ("3S.6", "Sabtu",   "Ekonomi - Keuangan Internasional",          "07.00", "09.30"),

    # ── 3S.7 ── Senin, Selasa, Rabu  |  kosong: Kamis, Sabtu
    ("3S.7", "Senin",   "Biologi - Biologi Sel",                     "07.00", "08.40"),
    ("3S.7", "Selasa",  "Biologi - Genetika",                        "13.00", "14.40"),
    ("3S.7", "Rabu",    "Biologi - Ekologi",                         "09.00", "10.40"),
    ("3S.7", "Rabu",    "Biologi - Mikrobiologi",                    "13.00", "14.40"),

    # ── 3S.8 ── Selasa, Kamis, Sabtu  |  kosong: Senin, Rabu
    ("3S.8", "Selasa",  "Kimia - Kimia Organik",                     "07.00", "08.40"),
    ("3S.8", "Selasa",  "Kimia - Kimia Anorganik",                   "10.50", "12.30"),
    ("3S.8", "Kamis",   "Kimia - Kimia Fisika",                      "08.50", "10.30"),
    ("3S.8", "Sabtu",   "Kimia - Analisis Kimia",                    "07.00", "09.30"),

    # ── 4S.1 ── Senin, Selasa, Rabu  |  kosong: Kamis, Sabtu
    ("4S.1", "Senin",   "Manajemen - Manajemen Perpustakaan",        "08.30", "11.55"),
    ("4S.1", "Selasa",  "Manajemen - Manajemen Keuangan",            "09.00", "10.40"),
    ("4S.1", "Rabu",    "Manajemen - Manajemen SDM",                 "07.00", "08.40"),
    ("4S.1", "Rabu",    "Manajemen - Manajemen Pemasaran",           "10.50", "12.30"),

    # ── 4S.2 ── Senin, Kamis, Sabtu  |  kosong: Selasa, Rabu
    ("4S.2", "Senin",   "Hukum - Pengantar Hukum",                   "09.00", "10.40"),
    ("4S.2", "Senin",   "Hukum - Hukum Perdata",                     "13.00", "14.40"),
    ("4S.2", "Kamis",   "Hukum - Hukum Tata Negara",                 "10.50", "12.30"),
    ("4S.2", "Sabtu",   "Hukum - Hukum Internasional",               "09.40", "12.10"),

    # ── 4S.3 ── Selasa, Rabu  |  kosong: Senin, Kamis, Sabtu
    ("4S.3", "Selasa",  "Psikologi - Psikologi Umum",                "10.50", "12.30"),
    ("4S.3", "Selasa",  "Psikologi - Psikologi Perkembangan",        "13.00", "14.40"),
    ("4S.3", "Rabu",    "Psikologi - Psikologi Sosial",              "08.50", "10.30"),

    # ── 4S.4 ── Senin, Selasa, Kamis, Sabtu  |  kosong: Rabu
    ("4S.4", "Senin",   "Akuntansi - Audit Dasar",                   "07.00", "08.40"),
    ("4S.4", "Selasa",  "Akuntansi - Akuntansi Manajemen",           "09.00", "10.40"),
    ("4S.4", "Kamis",   "Akuntansi - Audit Internal",                "10.50", "12.30"),
    ("4S.4", "Kamis",   "Akuntansi - Sistem Informasi Akuntansi",    "13.00", "14.40"),
    ("4S.4", "Sabtu",   "Akuntansi - Perpajakan Lanjut",             "07.00", "09.30"),

    # ── 4S.5 ── Selasa, Rabu, Kamis  |  kosong: Senin, Sabtu
    ("4S.5", "Selasa",  "Teknik Sipil - Struktur Beton",             "07.00", "08.40"),
    ("4S.5", "Selasa",  "Teknik Sipil - Mekanika Tanah",             "10.50", "12.30"),
    ("4S.5", "Rabu",    "Teknik Sipil - Hidrolika",                  "09.00", "10.40"),
    ("4S.5", "Kamis",   "Teknik Sipil - Manajemen Konstruksi",       "07.00", "08.40"),

    # ── 4S.6 ── Senin, Rabu, Sabtu  |  kosong: Selasa, Kamis
    ("4S.6", "Senin",   "Sastra - Linguistik Umum",                  "07.00", "08.40"),
    ("4S.6", "Senin",   "Sastra - Kajian Budaya",                    "10.50", "12.30"),
    ("4S.6", "Rabu",    "Sastra - Sastra Indonesia",                 "13.00", "14.40"),
    ("4S.6", "Sabtu",   "Sastra - Penulisan Kreatif",                "09.40", "12.10"),

    # ── 4S.7 ── Senin, Kamis  |  kosong: Selasa, Rabu, Sabtu
    ("4S.7", "Senin",   "Pendidikan - Teori Belajar",                "08.50", "10.30"),
    ("4S.7", "Senin",   "Pendidikan - Kurikulum",                    "13.00", "14.40"),
    ("4S.7", "Kamis",   "Pendidikan - Teknologi Pendidikan",         "09.00", "10.40"),

    # ── 4S.8 ── Selasa, Rabu, Kamis, Sabtu  |  kosong: Senin
    ("4S.8", "Selasa",  "Pendidikan - Evaluasi Pembelajaran",        "07.00", "08.40"),
    ("4S.8", "Rabu",    "Pendidikan - Manajemen Sekolah",            "10.50", "12.30"),
    ("4S.8", "Kamis",   "Pendidikan - Bimbingan Konseling",          "13.00", "14.40"),
    ("4S.8", "Sabtu",   "Pendidikan - Pengembangan Kurikulum",       "07.00", "09.30"),

    # ── 4S.9 ── Senin, Selasa, Sabtu  |  kosong: Rabu, Kamis
    ("4S.9", "Senin",   "Pendidikan - Psikologi Pendidikan",         "07.00", "08.40"),
    ("4S.9", "Selasa",  "Pendidikan - Pendidikan Inklusif",          "09.00", "10.40"),
    ("4S.9", "Selasa",  "Pendidikan - Desain Pembelajaran",          "13.00", "14.40"),
    ("4S.9", "Sabtu",   "Pendidikan - Supervisi Pendidikan",         "07.00", "09.30"),
]


def seed_data():
    with sqlite3.connect(SCHEDULE_DB_PATH) as conn:
        # Urutkan: lantai dulu (3S vs 4S), lalu nomor
        nama_kelas_list = sorted(
            set(row[0] for row in SEED_JADWAL),
            key=lambda x: (x[0], int(x.split(".")[1]))
        )
        for nama in nama_kelas_list:
            conn.execute("INSERT OR IGNORE INTO kelas (nama) VALUES (?)", (nama,))

        for nama, hari, prodi_matkul, mulai, selesai in SEED_JADWAL:
            kelas_id = conn.execute(
                "SELECT id FROM kelas WHERE nama = ?", (nama,)
            ).fetchone()[0]
            conn.execute(
                "INSERT INTO jadwal (kelas_id, hari, prodi_matkul, mulai, selesai) "
                "VALUES (?, ?, ?, ?, ?)",
                (kelas_id, hari, prodi_matkul, mulai, selesai)
            )

    print(f"[✓] Seed selesai: {len(nama_kelas_list)} kelas, {len(SEED_JADWAL)} entri jadwal.")
    print(f"    Kelas    : {', '.join(nama_kelas_list)}")
    print(f"    Aktif    : Senin, Selasa, Rabu, Kamis, Sabtu")
    print(f"    Libur    : Jumat, Minggu (tidak ada entri jadwal)")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Initializing databases...\n")
    init_schedule_db()
    init_user_db()
    seed_data()
    print(f"\nDone! DB siap dipakai.")
    print(f"  Schedule DB : {SCHEDULE_DB_PATH}")
    print(f"  User DB     : {USER_DB_PATH}")