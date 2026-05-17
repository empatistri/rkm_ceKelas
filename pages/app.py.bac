import streamlit as st
from datetime import datetime
import pytz
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from files.logic import (
    load_data_from_db,
    str_ke_menit,
    durasi_label,
    cek_status,
    jadwal_berikutnya,
    semua_jadwal_hari_ini,
)

from assets.templates import (
    load_css,
    render_header,
    render_stats,
    render_kelas_card_terpakai,
    render_kelas_card_kosong,
    render_section_label,
    render_pagination_info,
)

# Load data dari DB
data_kelas = load_data_from_db()

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
# CSS STYLING
# =====================
st.markdown(load_css(), unsafe_allow_html=True)


# =====================
# HEADER
# =====================
st.markdown(render_header(jam, hari, tgl), unsafe_allow_html=True)

# =====================
# STATISTIK
# =====================
total    = len(data_olah)
terpakai = sum(1 for k in data_olah if k["status"] == "terpakai")
kosong   = total - terpakai

st.markdown(render_stats(total, terpakai, kosong), unsafe_allow_html=True)

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
st.markdown(render_section_label(), unsafe_allow_html=True)

if total_filtered == 0:
    st.info("Tidak ada kelas yang sesuai filter.")
else:
    cols = st.columns(3)
    for i, kelas in enumerate(data_tampil):
        col = cols[i % 3]
        with col:
            # render kartu HTML
            if kelas["status"] == "terpakai":
                isi = render_kelas_card_terpakai(
                    kelas['nama_kelas'],
                    kelas['prodi_matkul'],
                    kelas['waktu']
                )
            else:
                isi = render_kelas_card_kosong(kelas['nama_kelas'])
            
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
        render_pagination_info(st.session_state.halaman, total_halaman, start, end, total_filtered),
        unsafe_allow_html=True
    )

with col_next:
    if st.button("Selanjutnya →", disabled=(st.session_state.halaman == total_halaman), use_container_width=True):
        st.session_state.halaman += 1
        st.rerun()