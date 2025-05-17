import streamlit as st
import pandas as pd
import json
import numpy as np
import locale
from datetime import datetime
import re

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

# Application title and description
st.title("Aplikasi Cek Kemiskinan Berdasarkan Pengeluaran")
st.markdown("""
Aplikasi ini membantu Anda mengecek status ekonomi rumah tangga berdasarkan pengeluaran per kapita 
dibandingkan dengan garis kemiskinan resmi.
""")

# Function to load data from local JSON file
@st.cache_data(ttl=3600)
def load_data():
    try:
        # Load data from JSON file
        with open('Garis Kemiskinan.json', 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return dummy data for testing
        st.info("Menggunakan data dummy untuk demo...")
        wilayah_data = pd.DataFrame({
            'nama_wilayah': ['JAKARTA', 'BANDUNG', 'SURABAYA', 'MEDAN', 'MAKASSAR'],
            'garis_kemiskinan': [800000, 750000, 720000, 680000, 700000]
        })
        return wilayah_data

# Load data
wilayah_data = load_data()

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

# Input sections outside the form
st.subheader("Pengaturan")

# Use columns to make inputs narrower (1/4 width)
col1, col2, col3, col4 = st.columns(4)

# Kabupaten/Kota selection - outside form, 1/4 width
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

# Number selector for anggota count - outside form, 1/4 width
with col2:
    st.session_state.anggota_count = st.number_input(
        "Jumlah Anggota Rumah Tangga:", 
        min_value=1, 
        value=st.session_state.anggota_count,
        key="anggota_count_input",
        on_change=update_anggota_count
    )

# Number selector for pengeluaran count - outside form, 1/4 width
with col3:
    st.session_state.pengeluaran_count = st.number_input(
        "Jumlah Jenis Pengeluaran:", 
        min_value=1, 
        value=st.session_state.pengeluaran_count,
        key="pengeluaran_count_input",
        on_change=update_pengeluaran_count
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

# Main form for data input
with st.form(key="kemiskinan_form"):
    # Anggota Rumah Tangga section
    st.subheader("Keterangan Anggota Rumah Tangga")
    
    # Create anggota fields
    anggota_data = []
    
    for i in range(st.session_state.anggota_count):
        cols = st.columns(4)
        
        with cols[0]:
            if i == 0:  # First person is always "Saya"
                hubungan = st.text_input(f"**Anggota {i+1}**", value="Saya", disabled=True, key=f"hubungan_{i}")
            else:
                hubungan = st.selectbox(f"**Anggota {i+1}**", options=hubungan_options, key=f"hubungan_{i}")
                
        with cols[1]:
            umur = st.number_input("Umur", min_value=1, value=25, key=f"umur_{i}")
            
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
    
    # Pengeluaran Rumah Tangga section
    st.subheader("Pengeluaran Rumah Tangga")
    
    # Create pengeluaran fields
    pengeluaran_data = []
    rentang_options = ["Bulanan", "Mingguan", "Tahunan"]
    
    for i in range(st.session_state.pengeluaran_count):
        cols = st.columns(3)
        
        with cols[0]:
            rentang = st.selectbox("Rentang", options=rentang_options, key=f"rentang_{i}")
            
        with cols[1]:
            kategori = st.text_input("Kategori", placeholder="contoh: Makanan", key=f"kategori_{i}")
        
        with cols[2]:
            # Text input for currency without callback (to avoid form error)
            nilai_text = st.text_input(
                "Nilai (Rp)", 
                placeholder="contoh: 1.000.000", 
                key=f"nilai_text_{i}"
            )
            
            # Parse the text input to get the numeric value
            try:
                nilai = parse_currency(nilai_text)
            except:
                nilai = 0
        
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
        
        # Format for display
        df_display = df_pengeluaran.copy()
        df_display['nilai'] = df_display['nilai'].apply(lambda x: f"Rp {format_currency(x)}")
        df_display['nilai_bulanan'] = df_display['nilai_bulanan'].apply(lambda x: f"Rp {format_currency(x)}")
        df_display.columns = ['Rentang', 'Kategori', 'Nilai', 'Nilai Bulanan']
        
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
