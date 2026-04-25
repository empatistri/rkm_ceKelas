import streamlit as st
from datetime import datetime
import pytz
import sqlite3
import os

import streamlit as st
from datetime import datetime
import sqlite3
import os

# =====================
# DATABASE SETUP
# =====================
DB_PATH = "files/datas/cekelas.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    conn.commit()
    conn.close()

def load_data_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT k.nama, j.prodi_matkul, j.mulai, j.selesai FROM kelas k LEFT JOIN jadwal j ON k.id = j.kelas_id ORDER BY k.nama, j.mulai")
    rows = cursor.fetchall()
    conn.close()
    
    data_kelas = {}
    for row in rows:
        nama_kelas, prodi_matkul, mulai, selesai = row
        if nama_kelas not in data_kelas:
            data_kelas[nama_kelas] = []
        if prodi_matkul:  # jika ada jadwal
            data_kelas[nama_kelas].append({
                "prodi_matkul": prodi_matkul,
                "mulai": mulai,
                "selesai": selesai
            })
    
    # Konversi ke list of dict seperti sebelumnya
    return [{"nama_kelas": nama, "jadwal": jadwal} for nama, jadwal in data_kelas.items()]

# Load data dari DB
data_kelas = load_data_from_db()

# =====================
# HELPER FUNCTIONS
# =====================
def str_ke_menit(jam_str):
    jam, menit = jam_str.split(".")
    return int(jam) * 60 + int(menit)

def menit_ke_jamstr(menit_total):
    jam   = menit_total // 60
    menit = menit_total % 60
    return f"{jam:02d}.{menit:02d}"

def durasi_label(selisih_menit):
    jam   = selisih_menit // 60
    menit = selisih_menit % 60
    if jam > 0 and menit > 0:
        return f"{jam} jam {menit} menit"
    elif jam > 0:
        return f"{jam} jam"
    else:
        return f"{menit} menit"

def cek_status(jadwal_list, sekarang_menit):
    for jadwal in jadwal_list:
        mulai   = str_ke_menit(jadwal["mulai"])
        selesai = str_ke_menit(jadwal["selesai"])
        if mulai <= sekarang_menit < selesai:
            return jadwal
    return None

def jadwal_berikutnya(jadwal_list, sekarang_menit):
    """Cari jadwal pertama yang mulainya > sekarang"""
    jadwal_sorted = sorted(jadwal_list, key=lambda j: str_ke_menit(j["mulai"]))
    for jadwal in jadwal_sorted:
        if str_ke_menit(jadwal["mulai"]) > sekarang_menit:
            return jadwal
    return None

def semua_jadwal_hari_ini(jadwal_list):
    """Kembalikan semua jadwal diurutkan dari pagi"""
    return sorted(jadwal_list, key=lambda j: str_ke_menit(j["mulai"]))

# =====================
# WAKTU SEKARANG
# =====================
HARI_ID  = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN_ID = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

tz             = pytz.timezone("Asia/Jakarta")
now            = datetime.now(tz)
hari           = HARI_ID[now.weekday()]
tgl            = f"{now.day} {BULAN_ID[now.month]} {now.year}"
jam            = now.strftime("%H:%M")
sekarang_menit = now.hour * 60 + now.minute

# =====================
# HITUNG STATUS TIAP KELAS
# =====================
data_olah = []
for kelas in data_kelas:
    jadwal_aktif = cek_status(kelas["jadwal"], sekarang_menit)
    if jadwal_aktif:
        data_olah.append({
            "nama_kelas":   kelas["nama_kelas"],
            "status":       "terpakai",
            "prodi_matkul": jadwal_aktif["prodi_matkul"],
            "waktu":        f"{jadwal_aktif['mulai']} - {jadwal_aktif['selesai']}",
            "jadwal_aktif": jadwal_aktif,
            "semua_jadwal": kelas["jadwal"],
        })
    else:
        data_olah.append({
            "nama_kelas":   kelas["nama_kelas"],
            "status":       "kosong",
            "prodi_matkul": "",
            "waktu":        "",
            "jadwal_aktif": None,
            "semua_jadwal": kelas["jadwal"],
        })

# =====================
# DIALOG / POP-UP
# =====================
@st.dialog("Detail Ruangan")
def tampilkan_detail(kelas):
    nama        = kelas["nama_kelas"]
    status      = kelas["status"]
    semua       = semua_jadwal_hari_ini(kelas["semua_jadwal"])
    berikutnya  = jadwal_berikutnya(kelas["semua_jadwal"], sekarang_menit)

    st.markdown(f"### 🏫 Ruang {nama}")
    st.markdown("---")

    if status == "terpakai":
        aktif    = kelas["jadwal_aktif"]
        selesai  = str_ke_menit(aktif["selesai"])
        sisa     = selesai - sekarang_menit

        st.markdown(f"**Status saat ini:** 🔴 Sedang Dipake")
        st.markdown(f"**Digunakan oleh:** {aktif['prodi_matkul']}")
        st.markdown(f"**Waktu:** {aktif['mulai']} – {aktif['selesai']}")
        st.info(f"⏳ Sisa waktu pemakaian: **{durasi_label(sisa)}** lagi")

        if berikutnya:
            st.markdown("---")
            st.markdown("**Jadwal setelah ini:**")
            mulai_berikut = str_ke_menit(berikutnya["mulai"])
            jeda          = mulai_berikut - sekarang_menit - sisa  # jeda antar jadwal
            st.markdown(
                f"📚 **{berikutnya['prodi_matkul']}**  \n"
                f"🕐 {berikutnya['mulai']} – {berikutnya['selesai']}"
            )
        else:
            st.markdown("---")
            st.success("✅ Tidak ada jadwal lagi setelah ini hari ini.")

    else:
        # kelas kosong
        if berikutnya:
            mulai_berikut = str_ke_menit(berikutnya["mulai"])
            kosong_selama = mulai_berikut - sekarang_menit

            st.markdown(f"**Status saat ini:** 🟢 Kosong / Tersedia")
            st.success(f"✅ Kelas kosong selama **{durasi_label(kosong_selama)}** lagi")
            st.markdown("---")
            st.markdown("**Jadwal berikutnya:**")
            st.markdown(
                f"📚 **{berikutnya['prodi_matkul']}**  \n"
                f"🕐 {berikutnya['mulai']} – {berikutnya['selesai']}"
            )
        else:
            st.markdown(f"**Status saat ini:** 🟢 Kosong / Tersedia")
            st.success("✅ Bebas digunakan — tidak ada jadwal lagi hari ini.")

    # tampilkan semua jadwal hari ini
    if semua:
        st.markdown("---")
        st.markdown("**Semua jadwal hari ini:**")
        for j in semua:
            mulai_j   = str_ke_menit(j["mulai"])
            selesai_j = str_ke_menit(j["selesai"])
            if mulai_j <= sekarang_menit < selesai_j:
                icon = "🔴"  # sedang berlangsung
            elif mulai_j > sekarang_menit:
                icon = "🕐"  # akan datang
            else:
                icon = "✅"  # sudah selesai
            st.markdown(f"{icon} `{j['mulai']} – {j['selesai']}` &nbsp; {j['prodi_matkul']}")
    else:
        st.markdown("---")
        st.markdown("📭 Tidak ada jadwal sama sekali hari ini.")

# =====================
# CSS
# =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    .header-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 55%, #0f3460 100%);
        border-radius: 16px; padding: 22px 32px; margin-bottom: 22px;
        color: white; display: flex; justify-content: space-between; align-items: center;
    }
    .header-brand { display: flex; align-items: center; gap: 16px; }
    .logo-circle {
        width: 54px; height: 54px; border-radius: 14px;
        background: linear-gradient(135deg, #4f8ef7, #a259f7);
        display: flex; align-items: center; justify-content: center;
        font-size: 26px; flex-shrink: 0; box-shadow: 0 4px 14px rgba(79,142,247,0.4);
    }
    .brand-name { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; line-height: 1; margin-bottom: 6px; }
    .brand-name span { color: #4f8ef7; }
    .brand-sub  { font-size: 12px; opacity: 0.55; line-height: 1.5; }
    .header-right { text-align: right; }
    .header-jam   { font-size: 30px; font-weight: 700; line-height: 1; letter-spacing: -1px; }
    .header-tgl   { font-size: 12px; opacity: 0.6; margin-top: 5px; }

    .stat-row { display: flex; gap: 14px; margin-bottom: 20px; }
    .stat-card { flex: 1; border-radius: 12px; padding: 18px 22px; color: white; }
    .stat-card.total  { background: #2d3561; }
    .stat-card.pakai  { background: #c0392b; }
    .stat-card.kosong { background: #1e8449; }
    .stat-number { font-size: 32px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
    .stat-label  { font-size: 12px; opacity: 0.8; }

    .section-label {
        font-size: 12px; font-weight: 600; letter-spacing: 1.5px;
        text-transform: uppercase; color: #999; margin-bottom: 12px;
    }

    /* wrapper kartu — posisi relative agar tombol bisa overlap */
    .card-wrapper {
        position: relative;
        margin-bottom: 14px;
    }
    .kelas-card {
        border-radius: 14px; padding: 18px 20px;
        height: 140px; display: flex; flex-direction: column;
        justify-content: space-between; overflow: hidden;
        cursor: pointer;
        transition: box-shadow 0.15s ease, transform 0.15s ease;
    }
    .kelas-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.10);
    }
    .kelas-card.terpakai { background: #fff5f5; border: 1.5px solid #f5c6c6; }
    .kelas-card.kosong   { background: #f0fff4; border: 1.5px solid #b7e4c7; }

    .card-top { display: flex; align-items: center; justify-content: space-between; }
    .room-name { font-size: 22px; font-weight: 700; color: #1a1a2e; line-height: 1; }

    .badge { font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; white-space: nowrap; }
    .badge.terpakai { background: #fde8e8; color: #c0392b; }
    .badge.kosong   { background: #d5f5e3; color: #1e8449; }

    .info-row {
        display: flex; align-items: flex-start; gap: 6px;
        font-size: 12px; color: #555; line-height: 1.4; margin-bottom: 3px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .info-icon { flex-shrink: 0; }
    .info-text  { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .available-text { font-size: 13px; color: #27ae60; font-weight: 500; }

    .tap-hint {
        font-size: 11px; color: #aaa; text-align: right;
        margin-top: -10px; margin-bottom: 4px;
    }

    /* sembunyikan border default tombol Streamlit agar tombol invisible */
    div[data-testid="stButton"] button[kind="tertiary"] {
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        cursor: pointer;
        z-index: 10;
    }
</style>
""", unsafe_allow_html=True)

# =====================
# HEADER
# =====================
st.markdown(f"""
<div class="header-box">
    <div class="header-brand">
        <div class="logo-circle">🎓</div>
        <div>
            <div class="brand-name">ce<span>Kelas</span> <span style="font-size:13px; opacity:0.5; font-weight:500;">v.1</span></div>
            <div class="brand-sub">
                non-Official Kampus!
            </div>
        </div>
    </div>
    <div class="header-right">
        <div class="header-jam">{jam}</div>
        <div class="header-tgl">{hari}, {tgl}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================
# STATISTIK
# =====================
total    = len(data_olah)
terpakai = sum(1 for k in data_olah if k["status"] == "terpakai")
kosong   = total - terpakai

st.markdown(f"""
<div class="stat-row">
    <div class="stat-card total">
        <div class="stat-number">{total}</div>
        <div class="stat-label">Total Kelas</div>
    </div>
    <div class="stat-card pakai">
        <div class="stat-number">{terpakai}</div>
        <div class="stat-label">Sedang Dipake</div>
    </div>
    <div class="stat-card kosong">
        <div class="stat-number">{kosong}</div>
        <div class="stat-label">Kelas Kosong</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================
# FILTER
# =====================
if "filter_status" not in st.session_state:
    st.session_state.filter_status = "Semua"

_, col_f1, col_f2, col_f3, _ = st.columns([2, 1, 1, 1, 2])

with col_f1:
    if st.button("🔘 Semua", use_container_width=True,
                 type="primary" if st.session_state.filter_status == "Semua" else "secondary"):
        st.session_state.filter_status = "Semua"
        st.session_state.halaman = 1
        st.rerun()
with col_f2:
    if st.button("🔴 Dipake", use_container_width=True,
                 type="primary" if st.session_state.filter_status == "terpakai" else "secondary"):
        st.session_state.filter_status = "terpakai"
        st.session_state.halaman = 1
        st.rerun()
with col_f3:
    if st.button("🟢 Kosong", use_container_width=True,
                 type="primary" if st.session_state.filter_status == "kosong" else "secondary"):
        st.session_state.filter_status = "kosong"
        st.session_state.halaman = 1
        st.rerun()

# =====================
# FILTER DATA
# =====================
if st.session_state.filter_status == "Semua":
    data_filtered = data_olah
else:
    data_filtered = [k for k in data_olah if k["status"] == st.session_state.filter_status]

# =====================
# PAGINATION
# =====================
CARDS_PER_PAGE = 9

if "halaman" not in st.session_state:
    st.session_state.halaman = 1

total_filtered = len(data_filtered)
total_halaman  = max(1, -(-total_filtered // CARDS_PER_PAGE))

if st.session_state.halaman > total_halaman:
    st.session_state.halaman = total_halaman

start       = (st.session_state.halaman - 1) * CARDS_PER_PAGE
end         = start + CARDS_PER_PAGE
data_tampil = data_filtered[start:end]

# =====================
# KARTU KELAS (klikable)
# =====================
st.markdown('<div class="section-label">Daftar Ruangan &nbsp;·&nbsp; <span style="font-weight:400; font-size:11px;">klik kartu untuk detail</span></div>', unsafe_allow_html=True)

if total_filtered == 0:
    st.info("Tidak ada kelas yang sesuai filter.")
else:
    cols = st.columns(3)
    for i, kelas in enumerate(data_tampil):
        col = cols[i % 3]
        with col:
            # render kartu HTML
            if kelas["status"] == "terpakai":
                isi = f"""
                <div class="kelas-card terpakai">
                    <div class="card-top">
                        <div class="room-name">{kelas['nama_kelas']}</div>
                        <div class="badge terpakai">🔴 Dipake</div>
                    </div>
                    <div class="card-bottom">
                        <div class="info-row">
                            <span class="info-icon">📚</span>
                            <span class="info-text">{kelas['prodi_matkul']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-icon">🕐</span>
                            <span class="info-text">{kelas['waktu']}</span>
                        </div>
                    </div>
                </div>
                """
            else:
                isi = f"""
                <div class="kelas-card kosong">
                    <div class="card-top">
                        <div class="room-name">{kelas['nama_kelas']}</div>
                        <div class="badge kosong">🟢 Kosong</div>
                    </div>
                    <div class="card-bottom">
                        <div class="available-text">✓ Ruangan tersedia</div>
                    </div>
                </div>
                """
            st.markdown(isi, unsafe_allow_html=True)

            # tombol invisible di atas kartu
            if st.button(f"Cek {kelas['nama_kelas']}", key=f"btn_{kelas['nama_kelas']}_{i}",
                         use_container_width=True):
                tampilkan_detail(kelas)

# =====================
# PAGINATION TOMBOL
# =====================
st.markdown("---")

col_prev, col_info, col_next = st.columns([1, 2, 1])

with col_prev:
    if st.button("← Sebelumnya", disabled=(st.session_state.halaman == 1), use_container_width=True):
        st.session_state.halaman -= 1
        st.rerun()

with col_info:
    st.markdown(
        f"<div style='text-align:center; padding-top:8px; font-size:14px; color:#666;'>"
        f"Halaman <b>{st.session_state.halaman}</b> dari <b>{total_halaman}</b>"
        f" &nbsp;·&nbsp; Menampilkan {start+1}–{min(end, total_filtered)} dari {total_filtered} kelas"
        f"</div>",
        unsafe_allow_html=True
    )

with col_next:
    if st.button("Selanjutnya →", disabled=(st.session_state.halaman == total_halaman), use_container_width=True):
        st.session_state.halaman += 1
        st.rerun()