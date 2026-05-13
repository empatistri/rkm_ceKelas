import streamlit as st
import sqlite3
import os

# Path database
DB_PATH = "files/datas/cekelas.db"

# Fungsi untuk koneksi DB
def get_conn():
    return sqlite3.connect(DB_PATH)

# Fungsi inisialisasi tabel admin jika belum ada
def init_admin_table():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    # Insert password default jika belum ada
    cursor.execute("INSERT OR IGNORE INTO admin (id, password) VALUES (1, 'masukansandi')")
    conn.commit()
    conn.close()

# Fungsi cek password
def check_password(input_password):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM admin WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == input_password

# Inisialisasi tabel admin
init_admin_table()

# Autentikasi
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("Login Admin")
    password = st.text_input("Masukkan Password", type="password")
    if st.button("Login"):
        if check_password(password):
            st.session_state.admin_logged_in = True
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Password salah!")
    st.stop()  # Hentikan eksekusi jika belum login

# Jika sudah login, lanjutkan ke dashboard

# Fungsi load data kelas dan jadwal
def load_data():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT k.id, k.nama, j.id as jadwal_id, j.prodi_matkul, j.mulai, j.selesai
        FROM kelas k
        LEFT JOIN jadwal j ON k.id = j.kelas_id
        ORDER BY k.nama, j.mulai
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fungsi tambah kelas
def add_kelas(nama):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kelas (nama) VALUES (?)", (nama,))
        conn.commit()
        st.success("Kelas berhasil ditambahkan!")
    except sqlite3.IntegrityError:
        st.error("Nama kelas sudah ada!")
    conn.close()

# Fungsi edit kelas
def edit_kelas(kelas_id, nama_baru):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE kelas SET nama = ? WHERE id = ?", (nama_baru, kelas_id))
    conn.commit()
    conn.close()
    st.success("Kelas berhasil diedit!")

# Fungsi hapus kelas
def delete_kelas(kelas_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jadwal WHERE kelas_id = ?", (kelas_id,))
    cursor.execute("DELETE FROM kelas WHERE id = ?", (kelas_id,))
    conn.commit()
    conn.close()
    st.success("Kelas dan jadwal terkait berhasil dihapus!")

# Fungsi tambah jadwal
def add_jadwal(kelas_id, prodi_matkul, mulai, selesai):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jadwal (kelas_id, prodi_matkul, mulai, selesai) VALUES (?, ?, ?, ?)",
                   (kelas_id, prodi_matkul, mulai, selesai))
    conn.commit()
    conn.close()
    st.success("Jadwal berhasil ditambahkan!")

# Fungsi edit jadwal
def edit_jadwal(jadwal_id, prodi_matkul, mulai, selesai):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE jadwal SET prodi_matkul = ?, mulai = ?, selesai = ? WHERE id = ?",
                   (prodi_matkul, mulai, selesai, jadwal_id))
    conn.commit()
    conn.close()
    st.success("Jadwal berhasil diedit!")

# Fungsi hapus jadwal
def delete_jadwal(jadwal_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jadwal WHERE id = ?", (jadwal_id,))
    conn.commit()
    conn.close()
    st.success("Jadwal berhasil dihapus!")

# UI Streamlit
st.title("Dashboard Admin - Edit Data Kelas")

# Load data
data = load_data()

# Tampilkan data dalam tabel
st.subheader("Data Kelas dan Jadwal")
if data:
    st.dataframe(data, use_container_width=True)
else:
    st.info("Belum ada data kelas.")

# Tabs untuk operasi
tab1, tab2, tab3 = st.tabs(["Tambah Kelas", "Edit/Hapus Kelas", "Edit Jadwal"])

with tab1:
    st.subheader("Tambah Kelas Baru")
    with st.form("add_kelas_form"):
        nama = st.text_input("Nama Kelas")
        submitted = st.form_submit_button("Tambah")
        if submitted and nama:
            add_kelas(nama)
            st.rerun()

with tab2:
    st.subheader("Edit atau Hapus Kelas")
    kelas_list = list(set([row[1] for row in data if row[1]]))  # Nama kelas unik
    if kelas_list:
        selected_kelas = st.selectbox("Pilih Kelas", kelas_list)
        kelas_id = next(row[0] for row in data if row[1] == selected_kelas)
        
        col1, col2 = st.columns(2)
        with col1:
            with st.form("edit_kelas_form"):
                nama_baru = st.text_input("Nama Baru", value=selected_kelas)
                edit_submitted = st.form_submit_button("Edit")
                if edit_submitted and nama_baru:
                    edit_kelas(kelas_id, nama_baru)
                    st.rerun()
        
        with col2:
            if st.button("Hapus Kelas", key="delete_kelas"):
                delete_kelas(kelas_id)
                st.rerun()
    else:
        st.info("Tidak ada kelas untuk diedit.")

with tab3:
    st.subheader("Tambah/Edit/Hapus Jadwal")
    kelas_list = list(set([row[1] for row in data if row[1]]))
    if kelas_list:
        selected_kelas = st.selectbox("Pilih Kelas untuk Jadwal", kelas_list, key="jadwal_kelas")
        kelas_id = next(row[0] for row in data if row[1] == selected_kelas)
        
        # Tampilkan jadwal untuk kelas ini
        jadwal_kelas = [row for row in data if row[0] == kelas_id and row[2]]
        if jadwal_kelas:
            st.write("Jadwal Saat Ini:")
            st.dataframe(jadwal_kelas, use_container_width=True)
        
        # Form tambah jadwal
        st.subheader("Tambah Jadwal Baru")
        with st.form("add_jadwal_form"):
            prodi_matkul = st.text_input("Prodi/Matkul")
            mulai = st.text_input("Jam Mulai (HH:MM)")
            selesai = st.text_input("Jam Selesai (HH:MM)")
            add_submitted = st.form_submit_button("Tambah Jadwal")
            if add_submitted and prodi_matkul and mulai and selesai:
                add_jadwal(kelas_id, prodi_matkul, mulai, selesai)
                st.rerun()
        
        # Edit/Hapus jadwal
        if jadwal_kelas:
            st.subheader("Edit atau Hapus Jadwal")
            jadwal_options = [f"{row[3]} - {row[4]} sampai {row[5]}" for row in jadwal_kelas]
            selected_jadwal = st.selectbox("Pilih Jadwal", jadwal_options)
            jadwal_id = next(row[2] for row in jadwal_kelas if f"{row[3]} - {row[4]} sampai {row[5]}" == selected_jadwal)
            jadwal_data = next(row for row in jadwal_kelas if row[2] == jadwal_id)
            
            with st.form("edit_jadwal_form"):
                prodi_baru = st.text_input("Prodi/Matkul", value=jadwal_data[3])
                mulai_baru = st.text_input("Jam Mulai", value=jadwal_data[4])
                selesai_baru = st.text_input("Jam Selesai", value=jadwal_data[5])
                edit_jadwal_submitted = st.form_submit_button("Edit Jadwal")
                if edit_jadwal_submitted:
                    edit_jadwal(jadwal_id, prodi_baru, mulai_baru, selesai_baru)
                    st.rerun()
            
            if st.button("Hapus Jadwal", key="delete_jadwal"):
                delete_jadwal(jadwal_id)
                st.rerun()
    else:
        st.info("Tidak ada kelas untuk mengelola jadwal.")