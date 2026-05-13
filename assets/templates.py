"""HTML templates untuk ceKelas"""

def load_css() -> str:
    """Load CSS styling"""
    with open("assets/styles.css", "r", encoding="utf-8") as f:
        return f"<style>\n{f.read()}\n</style>"


def render_header(jam: str, hari: str, tgl: str) -> str:
    """Render header section"""
    return f"""
<div class="header-box">
    <div class="header-brand">
        <div class="logo-circle">🎓</div>
        <div>
            <div class="brand-name">ce<span>Kelas</span></div>
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
"""


def render_stats(total: int, terpakai: int, kosong: int) -> str:
    """Render statistics cards"""
    return f"""
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
"""


def render_kelas_card_terpakai(nama_kelas: str, prodi_matkul: str, waktu: str) -> str:
    """Render classroom card (in use)"""
    return f"""
<div class="kelas-card terpakai">
    <div class="card-top">
        <div class="room-name">{nama_kelas}</div>
        <div class="badge terpakai">🔴 Dipake</div>
    </div>
    <div class="card-bottom">
        <div class="info-row">
            <span class="info-icon">📚</span>
            <span class="info-text">{prodi_matkul}</span>
        </div>
        <div class="info-row">
            <span class="info-icon">🕐</span>
            <span class="info-text">{waktu}</span>
        </div>
    </div>
</div>
"""


def render_kelas_card_kosong(nama_kelas: str) -> str:
    """Render classroom card (available)"""
    return f"""
<div class="kelas-card kosong">
    <div class="card-top">
        <div class="room-name">{nama_kelas}</div>
        <div class="badge kosong">🟢 Kosong</div>
    </div>
    <div class="card-bottom">
        <div class="available-text">✓ Ruangan tersedia</div>
    </div>
</div>
"""


def render_section_label() -> str:
    """Render section label for classroom list"""
    return '<div class="section-label">Daftar Ruangan &nbsp;·&nbsp; <span style="font-weight:400; font-size:11px;">klik kartu untuk detail</span></div>'


def render_pagination_info(halaman: int, total_halaman: int, start: int, end: int, total_filtered: int) -> str:
    """Render pagination info"""
    return (
        f"<div style='text-align:center; padding-top:8px; font-size:14px; color:#666;'>"
        f"Halaman <b>{halaman}</b> dari <b>{total_halaman}</b>"
        f" &nbsp;·&nbsp; Menampilkan {start+1}–{min(end, total_filtered)} dari {total_filtered} kelas"
        f"</div>"
    )
