import streamlit as st
import pandas as pd
import json
import numpy as np
import locale
from datetime import datetime
import re
import requests
import os
from dotenv import load_dotenv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from io import BytesIO

# Load environment variables
load_dotenv()

BPS_API_KEY = os.getenv("BPS_API_KEY", "")

# Set locale for currency formatting (try different options based on platform)
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'id_ID')
    except:
        pass  # Proceed without locale if not available

# Configure page settings
st.set_page_config(
    page_title="Cek Kemiskinan Berdasarkan Pengeluaran",
    page_icon="📊",
    layout="wide"
)

# Custom functions for formatting and parsing
def format_currency(number):
    """Format number to currency string with thousand separator"""
    return f"{number:,.0f}".replace(",", ".")

def parse_currency(currency_string):
    """Parse currency string with thousand separator to float"""
    if not currency_string:
        return 0
    # Remove all non-numeric characters except decimal point
    numeric_string = re.sub(r'[^\d.]', '', currency_string.replace(".", "").replace(",", "."))
    try:
        return float(numeric_string)
    except ValueError:
        return 0

# ---------- Infographic generator ----------
# Colour palette for pie chart slices
PIE_COLORS = [
    "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
    "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AB",
    "#6BAED6", "#FD8D3C", "#74C476", "#9E9AC8", "#D9D9D9",
]

# Status → hex colour mapping (matches the CSS colours used in the app)
STATUS_COLORS = {
    "Miskin":                "#E53935",   # red
    "Rentan Miskin":         "#FB8C00",   # orange
    "Menuju Kelas Menengah": "#1E88E5",   # blue
    "Kelas Menengah":        "#43A047",   # green
    "Kelas Atas":            "#8E24AA",   # purple
}


def generate_infographic(results: dict) -> BytesIO:
    """
    Render a 9×16 portrait infographic and return it as a PNG in a BytesIO buffer.
    """
    # ── palette helpers ──────────────────────────────────────────────
    BG          = "#FFFFFF"
    CARD_BG     = "#F4F6F8"
    HEADER_BG   = "#1B2845"
    TEXT_DARK   = "#1B2845"
    TEXT_LIGHT  = "#FFFFFF"
    ACCENT      = "#4E79A7"
    FOOTER_URL  = "cekkemiskinanbypengeluaran.streamlit.app"

    # ── unpack results ───────────────────────────────────────────────
    wilayah            = results["selected_wilayah"]
    status             = results["status"]
    status_color       = STATUS_COLORS.get(status, "#888888")
    rasio              = results["rasio"]
    total_pengeluaran  = results["total_pengeluaran"]
    pengeluaran_percap = results["pengeluaran_perkapita"]
    garis_kemiskinan   = results["garis_kemiskinan"]
    anggota_data       = results["anggota_data"]
    pengeluaran_data   = results["pengeluaran_data"]

    # ── pre-process pengeluaran → bulanan + persentase ──────────────
    rows_pen = []
    for p in pengeluaran_data:
        if p["nilai"] <= 0:
            continue
        if p["rentang"] == "Mingguan":
            bulanan = p["nilai"] * 30 / 7
        elif p["rentang"] == "Tahunan":
            bulanan = p["nilai"] / 12
        else:
            bulanan = p["nilai"]
        rows_pen.append({"kategori": p["kategori"] or "—", "bulanan": bulanan})

    # sort descending
    rows_pen.sort(key=lambda x: x["bulanan"], reverse=True)

    # group small slices (< 3 %) into "Lainnya"
    labels, values = [], []
    lainnya = 0.0
    for r in rows_pen:
        pct = (r["bulanan"] / total_pengeluaran * 100) if total_pengeluaran > 0 else 0
        if pct < 3:
            lainnya += r["bulanan"]
        else:
            labels.append(r["kategori"])
            values.append(r["bulanan"])
    if lainnya > 0:
        labels.append("Lainnya")
        values.append(lainnya)

    # ── figure setup ─────────────────────────────────────────────────
    fig = plt.figure(figsize=(9, 16), facecolor=BG)
    fig.patch.set_facecolor(BG)

    # GridSpec: 21 rows (was 18; +2 for gauge, +1 extra breathing room)
    gs = fig.add_gridspec(
        nrows=21, ncols=1,
        left=0.06, right=0.94, top=0.96, bottom=0.04,
        hspace=0.06
    )

    # ── 1. HEADER (rows 0-1) ─────────────────────────────────────────
    ax_header = fig.add_subplot(gs[0:2, :])
    ax_header.set_facecolor(HEADER_BG)
    ax_header.set_xlim(0, 1)
    ax_header.set_ylim(0, 1)
    ax_header.axis("off")
    ax_header.text(0.5, 0.62, "Hasil Analisis Status Ekonomi",
                   ha="center", va="center", fontsize=24, fontweight="bold",
                   color=TEXT_LIGHT, fontfamily="sans-serif")
    ax_header.text(0.5, 0.22, wilayah,
                   ha="center", va="center", fontsize=17,
                   color="#A8C4D9", fontfamily="sans-serif")

    # ── 2. STATUS BOX (rows 2-4) ─────────────────────────────────────
    ax_status = fig.add_subplot(gs[2:5, :])
    ax_status.set_facecolor(BG)
    ax_status.set_xlim(0, 1)
    ax_status.set_ylim(0, 1)
    ax_status.axis("off")
    box = FancyBboxPatch((0.05, 0.08), 0.9, 0.84,
                         boxstyle="round,pad=0.02",
                         facecolor=status_color, edgecolor="none")
    ax_status.add_patch(box)
    ax_status.text(0.5, 0.68, "Status Ekonomi",
                   ha="center", va="center", fontsize=16,
                   color="white", alpha=0.85, fontfamily="sans-serif")
    ax_status.text(0.5, 0.42, status,
                   ha="center", va="center", fontsize=32, fontweight="bold",
                   color="white", fontfamily="sans-serif")
    ax_status.text(0.5, 0.18, f"{rasio:.2f}x dari Garis Kemiskinan",
                   ha="center", va="center", fontsize=16,
                   color="white", alpha=0.90, fontfamily="sans-serif")

    # ── 3. KLASIFIKASI GAUGE (rows 5-6) ──────────────────────────────
    # 5 zona: Miskin <1x | Rentan Miskin <1.5x | Menuju KM <3.5x | KM <17x | Kelas Atas ≥17x
    # Representasi visual: bar dibagi proportional berdasarkan lebar zona yang
    # "bermakna" sampai 20x (capped), pointer di posisi rasio saat ini.
    GAUGE_MAX   = 20.0                          # cap visual axis
    gauge_zones = [
        ("Miskin",                1.0,  "#E53935"),
        ("Rentan Miskin",         0.5,  "#FB8C00"),
        ("Menuju Kelas Menengah", 2.0,  "#1E88E5"),
        ("Kelas Menengah",       13.5,  "#43A047"),
        ("Kelas Atas",            3.0,  "#8E24AA"),   # 17→20 = 3
    ]

    ax_gauge = fig.add_subplot(gs[5:7, :])
    ax_gauge.set_facecolor(BG)
    ax_gauge.set_xlim(0, 1)
    ax_gauge.set_ylim(0, 1)
    ax_gauge.axis("off")

    # Section label inside the axes
    ax_gauge.text(0.0, 0.92, "Klasifikasi Status",
                  ha="left", va="center", fontsize=16, fontweight="bold",
                  color=TEXT_DARK, fontfamily="sans-serif")

    bar_left   = 0.02
    bar_right  = 0.98
    bar_width  = bar_right - bar_left
    bar_y      = 0.42          # vertical centre of the bar
    bar_h      = 0.18          # height of the bar

    # Draw coloured segments
    x_cursor = bar_left
    tick_positions = []          # (x_in_axes, label)
    tick_positions.append((bar_left, "0"))
    boundaries_x = {0: bar_left}   # multiplier → x position

    for i, (name, width_units, color) in enumerate(gauge_zones):
        seg_w = (width_units / GAUGE_MAX) * bar_width
        ax_gauge.add_patch(FancyBboxPatch(
            (x_cursor, bar_y - bar_h / 2), seg_w, bar_h,
            boxstyle="square,pad=0",
            facecolor=color, edgecolor="white", linewidth=2
        ))
        x_cursor += seg_w

    # Tick marks at the boundaries: 1x, 1.5x, 3.5x, 17x, 20x
    for mult, label in [(1.0, "1x"), (1.5, "1.5x"), (3.5, "3.5x"), (17.0, "17x")]:
        x_pos = bar_left + (mult / GAUGE_MAX) * bar_width
        ax_gauge.plot([x_pos, x_pos], [bar_y - bar_h / 2 - 0.04,
                                        bar_y - bar_h / 2], color=TEXT_DARK, lw=1.5)
        ax_gauge.text(x_pos, bar_y - bar_h / 2 - 0.10, label,
                      ha="center", va="top", fontsize=11, color=TEXT_DARK,
                      fontfamily="sans-serif")

    # Zone labels inside each segment
    x_cursor = bar_left
    for name, width_units, color in gauge_zones:
        seg_w = (width_units / GAUGE_MAX) * bar_width
        # only label if segment is wide enough
        if seg_w > 0.07:
            ax_gauge.text(x_cursor + seg_w / 2, bar_y, name,
                          ha="center", va="center", fontsize=8.5, fontweight="bold",
                          color="white", fontfamily="sans-serif")
        x_cursor += seg_w

    # Pointer triangle at current rasio (capped at GAUGE_MAX)
    ptr_ratio  = min(rasio, GAUGE_MAX)
    ptr_x      = bar_left + (ptr_ratio / GAUGE_MAX) * bar_width
    tri_top    = bar_y + bar_h / 2 + 0.02
    tri_size   = 0.025
    triangle   = plt.Polygon([
        [ptr_x, tri_top],
        [ptr_x - tri_size, tri_top + tri_size * 1.2],
        [ptr_x + tri_size, tri_top + tri_size * 1.2],
    ], closed=True, facecolor=TEXT_DARK, edgecolor="none",
       transform=ax_gauge.transAxes, clip_on=False)
    ax_gauge.add_patch(triangle)

    # Label above pointer
    ax_gauge.text(ptr_x, tri_top + tri_size * 1.5 + 0.02, f"{rasio:.2f}x",
                  ha="center", va="bottom", fontsize=13, fontweight="bold",
                  color=TEXT_DARK, fontfamily="sans-serif")

    # ── 4. METRIK BOXES (rows 7-9) ───────────────────────────────────
    metrics = [
        ("Total Pengeluaran\nBulanan", f"Rp {format_currency(total_pengeluaran)}"),
        ("Pengeluaran\nPer Kapita",    f"Rp {format_currency(pengeluaran_percap)}"),
        ("Garis Kemiskinan\n" + wilayah, f"Rp {format_currency(garis_kemiskinan)}"),
    ]
    ax_metrics = fig.add_subplot(gs[7:10, :])
    ax_metrics.set_facecolor(BG)
    ax_metrics.set_xlim(0, 1)
    ax_metrics.set_ylim(0, 1)
    ax_metrics.axis("off")

    card_w  = 0.28
    gap     = (1 - card_w * 3) / 4
    for idx, (label, value) in enumerate(metrics):
        x_left = gap + idx * (card_w + gap)
        box = FancyBboxPatch((x_left, 0.1), card_w, 0.8,
                             boxstyle="round,pad=0.015",
                             facecolor=CARD_BG, edgecolor="none")
        ax_metrics.add_patch(box)
        ax_metrics.text(x_left + card_w / 2, 0.72, label,
                        ha="center", va="center", fontsize=12,
                        color=ACCENT, fontweight="bold", fontfamily="sans-serif")
        ax_metrics.text(x_left + card_w / 2, 0.35, value,
                        ha="center", va="center", fontsize=15, fontweight="bold",
                        color=TEXT_DARK, fontfamily="sans-serif")

    # ── 5. SECTION LABEL: Komposisi Pengeluaran ─────────────────────
    ax_lbl1 = fig.add_subplot(gs[10, :])
    ax_lbl1.axis("off")
    ax_lbl1.text(0.0, 0.5, "Komposisi Pengeluaran Bulanan",
                 ha="left", va="center", fontsize=18, fontweight="bold",
                 color=TEXT_DARK, fontfamily="sans-serif")

    # ── 6. PIE CHART (rows 11-15) ────────────────────────────────────
    ax_pie = fig.add_subplot(gs[11:16, :])
    ax_pie.set_facecolor(BG)

    if values:
        colors_slice = PIE_COLORS[: len(values)]
        wedges, texts, autotexts = ax_pie.pie(
            values,
            labels=None,
            autopct=lambda pct: f"{pct:.1f}%" if pct >= 3 else "",
            colors=colors_slice,
            startangle=90,
            pctdistance=0.78,
            wedgeprops=dict(edgecolor="white", linewidth=1.5, width=0.55),
        )
        for at in autotexts:
            at.set_fontsize(12)
            at.set_fontweight("bold")
            at.set_color("white")

        legend_patches = [
            mpatches.Patch(facecolor=colors_slice[i], edgecolor="none", label=labels[i])
            for i in range(len(labels))
        ]
        ax_pie.legend(
            handles=legend_patches,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            fontsize=11,
            frameon=False,
            title="Kategori",
            title_fontsize=12,
        )
    else:
        ax_pie.text(0.5, 0.5, "Tidak ada data pengeluaran",
                    ha="center", va="center", fontsize=15, color="#888888")
        ax_pie.axis("off")

    # ── 7. SECTION LABEL: Anggota Rumah Tangga ──────────────────────
    ax_lbl2 = fig.add_subplot(gs[16, :])
    ax_lbl2.axis("off")
    ax_lbl2.text(0.0, 0.5, "Anggota Rumah Tangga",
                 ha="left", va="center", fontsize=18, fontweight="bold",
                 color=TEXT_DARK, fontfamily="sans-serif")

    # ── 8. TABEL ANGGOTA (rows 17-19) ───────────────────────────────
    ax_tbl = fig.add_subplot(gs[17:20, :])
    ax_tbl.axis("off")
    ax_tbl.set_facecolor(BG)

    col_labels = ["Hubungan", "Umur", "Pendidikan", "Pekerjaan"]
    cell_data  = [
        [a["hubungan"], str(a["umur"]), a["pendidikan"], a["pekerjaan"] or "—"]
        for a in anggota_data
    ]

    table = ax_tbl.table(
        cellText=cell_data,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.8)

    # Style header row
    for col_idx in range(len(col_labels)):
        cell = table[0, col_idx]
        cell.set_facecolor(HEADER_BG)
        cell.set_text_props(color=TEXT_LIGHT, fontweight="bold")

    # Style data rows — alternating
    for row_idx in range(1, len(cell_data) + 1):
        for col_idx in range(len(col_labels)):
            cell = table[row_idx, col_idx]
            cell.set_facecolor(CARD_BG if row_idx % 2 == 0 else BG)
            cell.set_text_props(color=TEXT_DARK)
            cell.set_edgecolor("#E0E0E0")

    # ── 9. FOOTER (row 20) ───────────────────────────────────────────
    ax_footer = fig.add_subplot(gs[20, :])
    ax_footer.axis("off")
    ax_footer.set_facecolor(BG)
    ax_footer.text(0.5, 0.6, FOOTER_URL,
                   ha="center", va="center", fontsize=13,
                   color=ACCENT, fontweight="bold", fontfamily="sans-serif")
    ax_footer.text(0.5, 0.1,
                   f"Dihasilkan pada {datetime.now().strftime('%d %b %Y %H:%M')}",
                   ha="center", va="center", fontsize=11,
                   color="#999999", fontfamily="sans-serif")

    # ── export ───────────────────────────────────────────────────────
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    buf.seek(0)
    return buf


# Application title and description
st.title("Aplikasi Cek Kemiskinan Berdasarkan Pengeluaran")
st.markdown("""
Aplikasi ini membantu Anda mengecek status ekonomi rumah tangga berdasarkan pengeluaran per kapita 
dibandingkan dengan garis kemiskinan resmi.
""")

# ---------- API & data loading ----------
BPS_API_URL = (
    "https://webapi.bps.go.id/v1/api/list/model/data"
    "/lang/ind/domain/0000/var/624/th/125"
)


def _parse_api_response(api_data: dict) -> pd.DataFrame:
    """Parse raw BPS API JSON into DataFrame with nama_wilayah & garis_kemiskinan."""
    # Build suffix from metadata: {var}{turvar}{tahun}{turtahun}
    var_val   = str(api_data["var"][0]["val"])          # "624"
    turvar_val = str(api_data["turvar"][0]["val"])      # "0"
    tahun_val  = str(api_data["tahun"][0]["val"])       # "125"
    turtahun_val = str(api_data["turtahun"][0]["val"]) # "0"
    suffix = var_val + turvar_val + tahun_val + turtahun_val  # "62401250"

    datacontent = api_data["datacontent"]

    rows = []
    for region in api_data["vervar"]:
        label = region["label"]
        # Skip provinsi headers (wrapped in <b>...</b>)
        if label.startswith("<b>"):
            continue
        region_code = str(region["val"])
        key = region_code + suffix
        if key in datacontent:
            rows.append({
                "nama_wilayah": label,
                "garis_kemiskinan": datacontent[key]
            })
    return pd.DataFrame(rows)


def _fetch_from_api() -> tuple[pd.DataFrame | None, str | None]:
    """
    Fetch data from BPS API.
    Returns (DataFrame, last_update_str) on success, or (None, error_msg) on failure.
    """
    if not BPS_API_KEY:
        return None, "API key tidak ditemukan di .env"
    try:
        url = BPS_API_URL + f"/key/{BPS_API_KEY}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        api_data = resp.json()
        if api_data.get("status") != "OK":
            return None, f"API status: {api_data.get('status')}"
        df = _parse_api_response(api_data)
        last_update = api_data.get("last_update", "N/A")
        return df, last_update
    except Exception as e:
        return None, str(e)


def _load_from_local_json() -> pd.DataFrame | None:
    """Load fallback data from local Garis Kemiskinan.json (new API-format or old flat list)."""
    try:
        with open('Garis Kemiskinan.json', 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        # New format (raw API dump with vervar + datacontent)
        if isinstance(data, dict) and "vervar" in data and "datacontent" in data:
            return _parse_api_response(data)

        # Old flat-list format: [{"nama_wilayah": ..., "garis_kemiskinan": ...}, ...]
        if isinstance(data, list):
            return pd.DataFrame(data)

        return None
    except Exception:
        return None


@st.cache_data(ttl=3600)
def load_data() -> tuple[pd.DataFrame, dict]:
    """
    Master loader: try API first, fallback to local JSON.
    Returns (DataFrame, status_info_dict).
    status_info = {
        "source": "API" | "lokal" | "dummy",
        "last_update": str | None,
        "error": str | None
    }
    """
    # --- Try API ---
    df_api, api_info = _fetch_from_api()
    if df_api is not None and not df_api.empty:
        return df_api, {
            "source": "API",
            "last_update": api_info,   # last_update string on success
            "error": None
        }

    # api_info is error message here
    api_error = api_info

    # --- Fallback to local JSON ---
    df_local = _load_from_local_json()
    if df_local is not None and not df_local.empty:
        return df_local, {
            "source": "lokal",
            "last_update": None,
            "error": api_error
        }

    # --- Last resort: dummy data ---
    df_dummy = pd.DataFrame({
        'nama_wilayah': ['JAKARTA', 'BANDUNG', 'SURABAYA', 'MEDAN', 'MAKASSAR'],
        'garis_kemiskinan': [800000, 750000, 720000, 680000, 700000]
    })
    return df_dummy, {
        "source": "dummy",
        "last_update": None,
        "error": api_error
    }


# Load data
wilayah_data, _fetch_status = load_data()

# Initialize session state for storing form data
if 'selected_wilayah' not in st.session_state:
    st.session_state.selected_wilayah = wilayah_data['nama_wilayah'].iloc[0]
    
if 'anggota_count' not in st.session_state:
    st.session_state.anggota_count = 1
    
if 'pengeluaran_count' not in st.session_state:
    st.session_state.pengeluaran_count = 7  # Default set to 7
    
if 'calculation_done' not in st.session_state:
    st.session_state.calculation_done = False
    
if 'results' not in st.session_state:
    st.session_state.results = {}

# Callbacks for input changes (only for widgets outside forms)
def update_anggota_count():
    st.session_state.anggota_count = st.session_state.anggota_count_input

def update_pengeluaran_count():
    st.session_state.pengeluaran_count = st.session_state.pengeluaran_count_input

# ---------- Tampilan status fetch ----------
if _fetch_status["source"] == "API":
    st.success(
        f"Data diambil dari **API BPS** | "
        f"Last update: {_fetch_status['last_update']} | "
        f"Jumlah wilayah: {len(wilayah_data)}"
    )
elif _fetch_status["source"] == "lokal":
    st.warning(
        f"API tidak tersedia ({_fetch_status['error']}). "
        f"Menggunakan data **lokal** dari file JSON. "
        f"Jumlah wilayah: {len(wilayah_data)}"
    )
else:
    st.error(
        f"API dan file lokal tidak tersedia ({_fetch_status['error']}). "
        f"Menggunakan data dummy."
    )

# Input sections outside the form
st.subheader("Pengaturan")

# Use columns to make inputs narrower
col1, col2 = st.columns(2)

# Kabupaten/Kota selection - outside form
with col1:
    st.session_state.selected_wilayah = st.selectbox(
        "Pilih Kabupaten/Kota:",
        options=wilayah_data['nama_wilayah'].tolist(),
        index=wilayah_data['nama_wilayah'].tolist().index(st.session_state.selected_wilayah)
        if st.session_state.selected_wilayah in wilayah_data['nama_wilayah'].tolist() else 0,
        key="wilayah_selectbox"
    )

# Get garis kemiskinan for selected wilayah
garis_kemiskinan = wilayah_data[wilayah_data['nama_wilayah'] == st.session_state.selected_wilayah]['garis_kemiskinan'].values[0]

# Number selector for anggota count - outside form
with col2:
    st.session_state.anggota_count = st.number_input(
        "Jumlah Anggota Rumah Tangga:",
        min_value=1,
        value=st.session_state.anggota_count,
        key="anggota_count_input",
        on_change=update_anggota_count
    )

# Define options for dropdowns
pendidikan_options = [
    "Tidak/Belum Tamat Sekolah Dasar", 
    "SD/Sederajat", 
    "SMP/Sederajat", 
    "SMA/Sederajat", 
    "Diploma/Profesi", 
    "S1", 
    "S2", 
    "S3"
]

hubungan_options = [
    "Istri/Suami", 
    "Anak", 
    "Orang Tua/Kakek/Nenek", 
    "Famili lain", 
    "Pembantu/Sopir"
]

# ---------- Anggota Rumah Tangga (outside form, dynamic count) ----------
st.subheader("Keterangan Anggota Rumah Tangga")

anggota_data = []

for i in range(st.session_state.anggota_count):
    cols = st.columns(4)

    with cols[0]:
        if i == 0:  # First person is always "Saya"
            hubungan = st.text_input(f"**Anggota {i+1}**", value="Saya", disabled=True, key=f"hubungan_{i}")
        else:
            hubungan = st.selectbox(f"**Anggota {i+1}**", options=hubungan_options, key=f"hubungan_{i}")

    with cols[1]:
        umur = st.number_input("Umur", min_value=0, value=25, key=f"umur_{i}")

    with cols[2]:
        pendidikan = st.selectbox("Pendidikan", options=pendidikan_options, key=f"pendidikan_{i}")

    with cols[3]:
        pekerjaan = st.text_input("Pekerjaan", key=f"pekerjaan_{i}")

    anggota_data.append({
        "hubungan": hubungan,
        "umur": umur,
        "pendidikan": pendidikan,
        "pekerjaan": pekerjaan
    })

# ---------- Pengeluaran Rumah Tangga ----------
st.subheader("Pengeluaran Rumah Tangga")

# Jumlah Jenis Pengeluaran — outside form agar on_change berfungsi
st.session_state.pengeluaran_count = st.number_input(
    "Jumlah Jenis Pengeluaran:",
    min_value=1,
    value=st.session_state.pengeluaran_count,
    key="pengeluaran_count_input",
    on_change=update_pengeluaran_count
)

# Pengeluaran rows + submit button dalam form
pengeluaran_data = []
rentang_options = ["Bulanan", "Mingguan", "Tahunan"]

with st.form(key="kemiskinan_form"):
    for i in range(st.session_state.pengeluaran_count):
        cols = st.columns(3)

        with cols[0]:
            rentang = st.selectbox("Rentang", options=rentang_options, key=f"rentang_{i}")

        with cols[1]:
            kategori = st.text_input("Kategori", placeholder="contoh: Makanan", key=f"kategori_{i}")

        with cols[2]:
            nilai = st.number_input(
                "Nilai (Rp)",
                min_value=0,
                value=0,
                step=1000,
                key=f"nilai_{i}"
            )
            # Tampilkan formatted value sebagai helper
            if nilai > 0:
                st.caption(f"Rp {format_currency(nilai)}")

        pengeluaran_data.append({
            "rentang": rentang,
            "kategori": kategori,
            "nilai": nilai
        })

    # Submit button - centered
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submitted = st.form_submit_button("Hitung Status Ekonomi")

# Process submission
if submitted:
    # Calculate total pengeluaran
    total_mingguan = sum([p["nilai"] for p in pengeluaran_data if p["rentang"] == "Mingguan"])
    total_bulanan = sum([p["nilai"] for p in pengeluaran_data if p["rentang"] == "Bulanan"])
    total_tahunan = sum([p["nilai"] for p in pengeluaran_data if p["rentang"] == "Tahunan"])
    
    # Convert all to monthly
    bulanan_dari_mingguan = total_mingguan * 30 / 7
    bulanan_dari_tahunan = total_tahunan / 12
    
    total_pengeluaran = bulanan_dari_mingguan + total_bulanan + bulanan_dari_tahunan
    
    # Calculate per capita
    jumlah_anggota = len(anggota_data)
    pengeluaran_perkapita = total_pengeluaran / jumlah_anggota if jumlah_anggota > 0 else 0
    
    # Determine economic status based on garis kemiskinan
    if pengeluaran_perkapita < garis_kemiskinan:
        status = "Miskin"
        color = "red"
        rasio = pengeluaran_perkapita / garis_kemiskinan if garis_kemiskinan > 0 else 0
    elif pengeluaran_perkapita < 1.5 * garis_kemiskinan:
        status = "Rentan Miskin"
        color = "orange"
        rasio = pengeluaran_perkapita / garis_kemiskinan if garis_kemiskinan > 0 else 0
    elif pengeluaran_perkapita < 3.5 * garis_kemiskinan:
        status = "Menuju Kelas Menengah"
        color = "blue"
        rasio = pengeluaran_perkapita / garis_kemiskinan if garis_kemiskinan > 0 else 0
    elif pengeluaran_perkapita < 17 * garis_kemiskinan:
        status = "Kelas Menengah"
        color = "green"
        rasio = pengeluaran_perkapita / garis_kemiskinan if garis_kemiskinan > 0 else 0
    else:
        status = "Kelas Atas"
        color = "purple"
        rasio = pengeluaran_perkapita / garis_kemiskinan if garis_kemiskinan > 0 else 0
    
    # Store results in session state
    st.session_state.results = {
        'selected_wilayah': st.session_state.selected_wilayah,
        'garis_kemiskinan': garis_kemiskinan,
        'anggota_data': anggota_data,
        'pengeluaran_data': pengeluaran_data,
        'total_mingguan': total_mingguan,
        'total_bulanan': total_bulanan,
        'total_tahunan': total_tahunan,
        'bulanan_dari_mingguan': bulanan_dari_mingguan,
        'bulanan_dari_tahunan': bulanan_dari_tahunan,
        'total_pengeluaran': total_pengeluaran,
        'jumlah_anggota': jumlah_anggota,
        'pengeluaran_perkapita': pengeluaran_perkapita,
        'status': status,
        'color': color,
        'rasio': rasio
    }
    
    # Mark calculation as done
    st.session_state.calculation_done = True

# Display results if calculation has been done
if st.session_state.calculation_done:
    # Get results from session state
    results = st.session_state.results
    
    # Display results
    st.divider()
    
    # Create three columns for displaying results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Pengeluaran Bulanan", f"Rp {format_currency(results['total_pengeluaran'])}")
    
    with col2:
        st.metric("Jumlah Anggota Rumah Tangga", results['jumlah_anggota'])
    
    with col3:
        st.metric("Pengeluaran Per Kapita", f"Rp {format_currency(results['pengeluaran_perkapita'])}")
    
    # Display garis kemiskinan and status
    st.subheader("Hasil Analisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"Garis Kemiskinan {results['selected_wilayah']}: Rp {format_currency(results['garis_kemiskinan'])}")
    
    with col2:
        st.markdown(f"<p style='color:{results['color']}; font-size:20px; font-weight:bold;'>Status Ekonomi: {results['status']}</p>", unsafe_allow_html=True)
    

    st.text(f"Pengeluaran per kapita anda adalah {results['rasio']:.2f}x dari garis kemiskinan di {results['selected_wilayah']}")
    
    # Display detailed breakdown
    st.subheader("Rincian Pengeluaran")
    
    # Create DataFrame from pengeluaran_data
    df_pengeluaran = pd.DataFrame(results['pengeluaran_data'])
    
    # Only show entries with nilai > 0
    df_pengeluaran = df_pengeluaran[df_pengeluaran['nilai'] > 0]
    
    if not df_pengeluaran.empty:
        # Add a column for monthly equivalent
        df_pengeluaran['nilai_bulanan'] = df_pengeluaran.apply(
            lambda row: row['nilai'] * 30 / 7 if row['rentang'] == "Mingguan" else 
                       (row['nilai'] / 12 if row['rentang'] == "Tahunan" else row['nilai']),
            axis=1
        )
        
        # Urutkan dari terbesar ke terkecil berdasarkan nilai bulanan
        df_pengeluaran = df_pengeluaran.sort_values('nilai_bulanan', ascending=False).reset_index(drop=True)

        # Hitung persentase dari total pengeluaran bulanan
        total = results['total_pengeluaran']
        df_pengeluaran['persentase'] = df_pengeluaran['nilai_bulanan'].apply(
            lambda x: f"{(x / total * 100):.1f}%" if total > 0 else "0.0%"
        )

        # Toggle kolom tambahan
        col_toggle1, col_toggle2 = st.columns(2)
        with col_toggle1:
            show_nilai = st.toggle("Tampilkan Nilai", value=False)
        with col_toggle2:
            show_nilai_bulanan = st.toggle("Tampilkan Nilai Bulanan", value=True)

        # Bangun DataFrame display secara dinamis
        df_pengeluaran['nilai_fmt'] = df_pengeluaran['nilai'].apply(lambda x: f"Rp {format_currency(x)}")
        df_pengeluaran['nilai_bulanan_fmt'] = df_pengeluaran['nilai_bulanan'].apply(lambda x: f"Rp {format_currency(x)}")

        cols_select = ['rentang', 'kategori', 'persentase']
        cols_label  = ['Rentang', 'Kategori', 'Persentase']

        if show_nilai:
            cols_select.append('nilai_fmt')
            cols_label.append('Nilai')
        if show_nilai_bulanan:
            cols_select.append('nilai_bulanan_fmt')
            cols_label.append('Nilai Bulanan')

        df_display = df_pengeluaran[cols_select].copy()
        df_display.columns = cols_label

        st.table(df_display)
    else:
        st.info("Tidak ada pengeluaran yang diinput")
    
    # Display household members
    st.subheader("Anggota Rumah Tangga")
    
    # Create DataFrame from anggota_data
    df_anggota = pd.DataFrame(results['anggota_data'])
    df_anggota.columns = ['Hubungan', 'Umur', 'Pendidikan', 'Pekerjaan']
    
    st.table(df_anggota)
    
    st.subheader(f"Klasifikasi untuk {results['selected_wilayah']}")
    st.text(f"Rp {format_currency(17*results['garis_kemiskinan'])} < Pengeluaran per kapita: Kelas Atas")
    st.text(f"Rp {format_currency(3.5*results['garis_kemiskinan'])} < Pengeluaran per kapita < Rp {format_currency(17*results['garis_kemiskinan'])}: Kelas Menengah")
    st.text(f"Rp {format_currency(1.5*results['garis_kemiskinan'])} < Pengeluaran per kapita < Rp {format_currency(3.5*results['garis_kemiskinan'])}: Menuju Kelas Menengah")
    st.text(f"Rp {format_currency(results['garis_kemiskinan'])} < Pengeluaran per kapita < Rp {format_currency(1.5*results['garis_kemiskinan'])}: Rentan Miskin")
    st.text(f"Pengeluaran per kapita < Rp {format_currency(results['garis_kemiskinan'])}: Miskin")
    # Timestamp of calculation
    st.caption(f"Perhitungan dilakukan pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ---------- Download infographic ----------
    st.divider()
    if st.button("Generate Gambar Hasil Analisis", use_container_width=True):
        with st.spinner("Membuat gambar …"):
            img_buf = generate_infographic(results)
        safe_name = re.sub(r'[^\w\-]', '_', results['selected_wilayah'])
        st.download_button(
            label="Unduh Gambar (PNG)",
            data=img_buf,
            file_name=f"hasil_analisis_{safe_name}.png",
            mime="image/png",
            use_container_width=True,
        )

# Add info in sidebar
with st.sidebar:
    st.title("Informasi")
    st.info("""
    **Aplikasi Cek Kemiskinan Berdasarkan Pengeluaran**
    
    Aplikasi ini menghitung status ekonomi rumah tangga berdasarkan perbandingan pengeluaran per kapita dengan garis kemiskinan resmi.
    
    **Cara Penggunaan:**
    1. Pilih Kabupaten/Kota domisili
    2. Atur jumlah anggota rumah tangga
    3. Atur jumlah jenis pengeluaran
    4. Isi data untuk setiap anggota
    5. Isi detail pengeluaran (bisa menggunakan format angka dengan atau tanpa pemisah ribuan)
    6. Klik "Hitung Status Ekonomi"
    
    **Format Pengeluaran:**
    Masukkan nilai pengeluaran dengan atau tanpa pemisah ribuan, contoh: 1000000 atau 1.000.000
    
    **Kategori Status Ekonomi:**
    - **Miskin**: < garis kemiskinan
    - **Rentan Miskin**: < 1,5x garis kemiskinan
    - **Menuju Kelas Menengah**: < 3,5x garis kemiskinan
    - **Kelas Menengah**: < 17x garis kemiskinan
    - **Kelas Atas**: ≥ 17x garis kemiskinan
    """)
