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

# ─────────────────────────────────────────────────────────────────────────────
# KONSTANTA
# ─────────────────────────────────────────────────────────────────────────────
HARI_ID  = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN_ID = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
TZ = pytz.timezone("Asia/Jakarta")

CARDS_PER_PAGE = 9


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: ambil waktu sekarang
# ─────────────────────────────────────────────────────────────────────────────
def get_waktu_sekarang():
    now = datetime.now(TZ)
    return {
        "now":            now,
        "hari":           HARI_ID[now.weekday()],
        "tgl":            f"{now.day} {BULAN_ID[now.month]} {now.year}",
        "jam":            now.strftime("%H:%M"),
        "sekarang_menit": now.hour * 60 + now.minute,
    }


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: hitung status semua kelas
# ─────────────────────────────────────────────────────────────────────────────
def hitung_status(data_kelas, sekarang_menit):
    hasil = []
    for kelas in data_kelas:
        jadwal_aktif = cek_status(kelas["jadwal"], sekarang_menit)
        if jadwal_aktif:
            hasil.append({
                "nama_kelas":   kelas["nama_kelas"],
                "status":       "terpakai",
                "prodi_matkul": jadwal_aktif["prodi_matkul"],
                "waktu":        f"{jadwal_aktif['mulai']} - {jadwal_aktif['selesai']}",
                "jadwal_aktif": jadwal_aktif,
                "semua_jadwal": kelas["jadwal"],
            })
        else:
            hasil.append({
                "nama_kelas":   kelas["nama_kelas"],
                "status":       "kosong",
                "prodi_matkul": "",
                "waktu":        "",
                "jadwal_aktif": None,
                "semua_jadwal": kelas["jadwal"],
            })
    return hasil


# ─────────────────────────────────────────────────────────────────────────────
# CSS (sekali render, di luar fragment)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(load_css(), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "filter_status" not in st.session_state:
    st.session_state.filter_status = "Semua"
if "halaman" not in st.session_state:
    st.session_state.halaman = 1


# ─────────────────────────────────────────────────────────────────────────────
# FRAGMENT — auto-refresh tiap 60 detik
# Semua yang bergantung pada waktu ada di sini:
#   header jam, stats, kartu kelas
# Filter & pagination di-baca dari session_state supaya tidak reset
# ─────────────────────────────────────────────────────────────────────────────
@st.fragment(run_every=30)
def dashboard():
    # ── Waktu aktual (di-fetch ulang tiap fragment run) ──────────────────────
    w              = get_waktu_sekarang()
    hari           = w["hari"]
    tgl            = w["tgl"]
    jam            = w["jam"]
    sekarang_menit = w["sekarang_menit"]

    # ── Load jadwal sesuai hari ──────────────────────────────────────────────
    data_kelas = load_data_from_db(hari)
    data_olah  = hitung_status(data_kelas, sekarang_menit)

    # Simpan ke session_state supaya dialog bisa akses data terbaru
    st.session_state["data_olah"]       = data_olah
    st.session_state["sekarang_menit"]  = sekarang_menit
    st.session_state["hari"]            = hari

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(render_header(jam, hari, tgl), unsafe_allow_html=True)

    # ── Statistik ────────────────────────────────────────────────────────────
    total    = len(data_olah)
    terpakai = sum(1 for k in data_olah if k["status"] == "terpakai")
    kosong   = total - terpakai
    st.markdown(render_stats(total, terpakai, kosong), unsafe_allow_html=True)

    # ── Filter tombol ────────────────────────────────────────────────────────
    _, col_f1, col_f2, col_f3, _ = st.columns([2, 1, 1, 1, 2])
    with col_f1:
        if st.button("🔘 Semua", use_container_width=True,
                     type="primary" if st.session_state.filter_status == "Semua" else "secondary"):
            st.session_state.filter_status = "Semua"
            st.session_state.halaman = 1
            st.rerun(scope="fragment")
    with col_f2:
        if st.button("🔴 Dipakai", use_container_width=True,
                     type="primary" if st.session_state.filter_status == "terpakai" else "secondary"):
            st.session_state.filter_status = "terpakai"
            st.session_state.halaman = 1
            st.rerun(scope="fragment")
    with col_f3:
        if st.button("🟢 Kosong", use_container_width=True,
                     type="primary" if st.session_state.filter_status == "kosong" else "secondary"):
            st.session_state.filter_status = "kosong"
            st.session_state.halaman = 1
            st.rerun(scope="fragment")

    # ── Filter data ──────────────────────────────────────────────────────────
    if st.session_state.filter_status == "Semua":
        data_filtered = data_olah
    else:
        data_filtered = [k for k in data_olah
                         if k["status"] == st.session_state.filter_status]

    # ── Pagination hitung ────────────────────────────────────────────────────
    total_filtered = len(data_filtered)
    total_halaman  = max(1, -(-total_filtered // CARDS_PER_PAGE))

    if st.session_state.halaman > total_halaman:
        st.session_state.halaman = total_halaman

    start       = (st.session_state.halaman - 1) * CARDS_PER_PAGE
    end         = start + CARDS_PER_PAGE
    data_tampil = data_filtered[start:end]

    # ── Kartu kelas ──────────────────────────────────────────────────────────
    st.markdown(render_section_label(), unsafe_allow_html=True)

    if total_filtered == 0:
        st.info("Tidak ada kelas yang sesuai filter.")
    else:
        cols = st.columns(3)
        for i, kelas in enumerate(data_tampil):
            with cols[i % 3]:
                if kelas["status"] == "terpakai":
                    isi = render_kelas_card_terpakai(
                        kelas["nama_kelas"],
                        kelas["prodi_matkul"],
                        kelas["waktu"],
                    )
                else:
                    isi = render_kelas_card_kosong(kelas["nama_kelas"])

                st.markdown(isi, unsafe_allow_html=True)

                if st.button(f"Cek {kelas['nama_kelas']}",
                             key=f"btn_{kelas['nama_kelas']}_{i}",
                             use_container_width=True):
                    tampilkan_detail(kelas, sekarang_menit, hari)

    # ── Pagination tombol ────────────────────────────────────────────────────
    st.markdown("---")
    col_prev, col_info, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("← Sebelumnya",
                     disabled=(st.session_state.halaman == 1),
                     use_container_width=True):
            st.session_state.halaman -= 1
            st.rerun(scope="fragment")

    with col_info:
        st.markdown(
            render_pagination_info(
                st.session_state.halaman, total_halaman, start, end, total_filtered
            ),
            unsafe_allow_html=True,
        )

    with col_next:
        if st.button("Selanjutnya →",
                     disabled=(st.session_state.halaman == total_halaman),
                     use_container_width=True):
            st.session_state.halaman += 1
            st.rerun(scope="fragment")

    # ── Indikator auto-refresh ───────────────────────────────────────────────
    st.caption(f"🔄 Data diperbarui otomatis setiap 60 detik · Terakhir: {jam}")


# ─────────────────────────────────────────────────────────────────────────────
# DIALOG — di luar fragment supaya tidak terpengaruh auto-refresh
# Akses data_olah terbaru via session_state
# ─────────────────────────────────────────────────────────────────────────────
@st.dialog("Detail Ruangan")
def tampilkan_detail(kelas, sekarang_menit, hari):
    nama       = kelas["nama_kelas"]
    status     = kelas["status"]
    semua      = semua_jadwal_hari_ini(kelas["semua_jadwal"])
    berikutnya = jadwal_berikutnya(kelas["semua_jadwal"], sekarang_menit)

    st.markdown(f"### 🏫 Ruang {nama}")
    st.markdown("---")

    if status == "terpakai":
        aktif = kelas["jadwal_aktif"]
        sisa  = str_ke_menit(aktif["selesai"]) - sekarang_menit

        st.markdown("**Status saat ini:** 🔴 Sedang Dipakai")
        st.markdown(f"**Digunakan oleh:** {aktif['prodi_matkul']}")
        st.markdown(f"**Waktu:** {aktif['mulai']} – {aktif['selesai']}")
        st.info(f"⏳ Sisa waktu pemakaian: **{durasi_label(sisa)}** lagi")

        if berikutnya:
            st.markdown("---")
            st.markdown("**Jadwal setelah ini:**")
            st.markdown(
                f"📚 **{berikutnya['prodi_matkul']}**  \n"
                f"🕐 {berikutnya['mulai']} – {berikutnya['selesai']}"
            )
        else:
            st.markdown("---")
            st.success("✅ Tidak ada jadwal lagi setelah ini hari ini.")

    else:
        if berikutnya:
            kosong_selama = str_ke_menit(berikutnya["mulai"]) - sekarang_menit
            st.markdown("**Status saat ini:** 🟢 Kosong / Tersedia")
            st.success(f"✅ Kelas kosong selama **{durasi_label(kosong_selama)}** lagi")
            st.markdown("---")
            st.markdown("**Jadwal berikutnya:**")
            st.markdown(
                f"📚 **{berikutnya['prodi_matkul']}**  \n"
                f"🕐 {berikutnya['mulai']} – {berikutnya['selesai']}"
            )
        else:
            st.markdown("**Status saat ini:** 🟢 Kosong / Tersedia")
            if kelas["semua_jadwal"]:
                st.success("✅ Bebas digunakan — tidak ada jadwal lagi hari ini.")
            else:
                st.success("✅ Bebas digunakan — tidak ada jadwal sama sekali hari ini.")

    if semua:
        st.markdown("---")
        st.markdown(f"**Semua jadwal hari {hari}:**")
        for j in semua:
            mulai_j   = str_ke_menit(j["mulai"])
            selesai_j = str_ke_menit(j["selesai"])
            if mulai_j <= sekarang_menit < selesai_j:
                icon = "🔴"
            elif mulai_j > sekarang_menit:
                icon = "🕐"
            else:
                icon = "✅"
            st.markdown(
                f"{icon} `{j['mulai']} – {j['selesai']}` &nbsp; {j['prodi_matkul']}"
            )
    else:
        st.markdown("---")
        st.markdown("📭 Tidak ada jadwal sama sekali hari ini.")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
dashboard()