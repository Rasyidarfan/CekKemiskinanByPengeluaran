# Aplikasi Cek Kemiskinan Berdasarkan Pengeluaran

Aplikasi web interaktif untuk mengevaluasi status ekonomi rumah tangga berdasarkan perbandingan pengeluaran per kapita dengan garis kemiskinan resmi di berbagai wilayah Indonesia.

## Deskripsi

Aplikasi ini membantu pengguna untuk menentukan status ekonomi rumah tangga dengan cara membandingkan total pengeluaran per kapita bulanan dengan garis kemiskinan resmi. Status ekonomi dikategorikan menjadi 5 tingkatan:

- **Miskin**: Pengeluaran per kapita < garis kemiskinan
- **Rentan Miskin**: Pengeluaran per kapita < 1,5x garis kemiskinan
- **Menuju Kelas Menengah**: Pengeluaran per kapita < 3,5x garis kemiskinan
- **Kelas Menengah**: Pengeluaran per kapita < 17x garis kemiskinan
- **Kelas Atas**: Pengeluaran per kapita ≥ 17x garis kemiskinan

## Fitur Utama

- Pemilihan Kabupaten/Kota domisili dengan data garis kemiskinan terbaru
- Input data anggota rumah tangga beserta informasi demografis
- Input rincian pengeluaran berdasarkan rentang waktu (mingguan, bulanan, tahunan)
- Kalkulasi otomatis pengeluaran per kapita dan perbandingan dengan garis kemiskinan
- Visualisasi status ekonomi dengan indikator warna dan progress bar
- Tampilan rincian perhitungan dan breakdown pengeluaran dengan toggle kolom
- Pengambilan data garis kemiskinan secara otomatis dari API BPS, dengan fallback ke file lokal
- Generate & unduh gambar infographic hasil analisis (9×16 portrait) berisi status ekonomi, gauge klasifikasi, pie chart komposisi pengeluaran, dan tabel anggota rumah tangga

## Persyaratan Sistem

- Python 3.8 atau lebih baru
- Streamlit 1.34.0 atau lebih baru
- Pandas 2.0.0 atau lebih baru
- Matplotlib 3.7.0 atau lebih baru
- Requests, python-dotenv (tertera dalam `requirements.txt`)

## Cara Instalasi

1. Kloning repositori atau salin semua file ke direktori lokal

2. Buat dan aktifkan lingkungan virtual Python:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instal dependensi yang diperlukan:
   ```
   pip install -r requirements.txt
   ```

4. Dapatkan API key dari [BPS Web API](https://webapi.bps.go.id/developer/) dengan mendaftar dan melakukan login. Buat file `.env` di direktori aplikasi dan isi dengan:
   ```
   BPS_API_KEY=your_api_key_here
   ```
   > Aplikasi akan mengambil data garis kemiskinan secara otomatis dari API BPS. Jika API tidak tersedia atau key tidak diisi, aplikasi akan fallback menggunakan data dari file lokal `Garis Kemiskinan.json`.

## Cara Penggunaan

1. Jalankan aplikasi dengan perintah:
   ```
   streamlit run app.py
   ```

2. Buka browser dan akses aplikasi melalui URL yang ditampilkan (biasanya http://localhost:8501)

3. Isi formulir sesuai petunjuk:
   - Pilih Kabupaten/Kota domisili
   - Atur jumlah anggota rumah tangga (secara default 1)
   - Isi data untuk setiap anggota (hubungan, umur, pendidikan, pekerjaan)
   - Atur jumlah jenis pengeluaran dan isi detail pengeluaran per kategori
   - Klik "Hitung Status Ekonomi"

4. Lihat hasil analisis yang menampilkan status ekonomi rumah tangga, termasuk gauge klasifikasi dan breakdown pengeluaran

5. Klik "Generate Gambar Hasil Analisis" untuk membuat infographic, kemudian unduh gambar PNG yang berisi ringkasan lengkap hasil analisis

## Struktur Aplikasi

- `app.py` - File utama aplikasi Streamlit
- `Garis Kemiskinan.json` - Data garis kemiskinan fallback (format raw API BPS)
- `requirements.txt` - Daftar dependensi Python
- `.env` - Berisi `BPS_API_KEY` (tidak di-commit ke repository)
- `.gitignore` - Mengecualikan `.env`, `venv/`, dan `__pycache__/`
- `README.md` - Dokumentasi aplikasi

## Format Input Nilai

Aplikasi mendukung berbagai format input nilai, antara lain:
- Tanpa pemisah ribuan: `1000000`
- Dengan pemisah titik: `1.000.000`
- Dengan pemisah koma: `1,000,000`

Semua format akan diproses dengan benar dan ditampilkan dengan format "Rp 1.000.000" pada hasil perhitungan.
