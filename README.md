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
- Tampilan rincian perhitungan dan breakdown pengeluaran

## Persyaratan Sistem

- Python 3.8 atau lebih baru
- Streamlit 1.34.0 atau lebih baru
- Pandas 2.0.0 atau lebih baru
- Library pendukung lainnya (tertera dalam `requirements.txt`)

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

4. Pastikan file `Garis Kemiskinan.json` berada di direktori aplikasi

## Cara Penggunaan

1. Jalankan aplikasi dengan perintah:
   ```
   streamlit run app.py
   ```
   Atau gunakan file batch `run_app.bat` dengan klik dua kali

2. Buka browser dan akses aplikasi melalui URL yang ditampilkan (biasanya http://localhost:8501)

3. Isi formulir sesuai petunjuk:
   - Pilih Kabupaten/Kota domisili
   - Atur jumlah anggota rumah tangga (secara default 1)
   - Atur jumlah jenis pengeluaran (secara default 7)
   - Isi data untuk setiap anggota
   - Isi detail pengeluaran (nilai dapat dimasukkan dengan atau tanpa pemisah ribuan)
   - Klik "Hitung Status Ekonomi"

4. Lihat hasil analisis yang menampilkan status ekonomi rumah tangga

## Struktur Aplikasi

- `app.py` - File utama aplikasi Streamlit
- `Garis Kemiskinan.json` - Data garis kemiskinan untuk berbagai kabupaten/kota
- `requirements.txt` - Daftar dependensi Python
- `run_app.bat` - Script batch untuk menjalankan aplikasi (Windows)
- `README.md` - Dokumentasi aplikasi

## Format Input Nilai

Aplikasi mendukung berbagai format input nilai, antara lain:
- Tanpa pemisah ribuan: `1000000`
- Dengan pemisah titik: `1.000.000`
- Dengan pemisah koma: `1,000,000`

Semua format akan diproses dengan benar dan ditampilkan dengan format "Rp 1.000.000" pada hasil perhitungan.

## Kontribusi dan Pengembangan

Untuk melaporkan bug, memberikan saran, atau berkontribusi pada pengembangan aplikasi, silakan hubungi pengembang atau buat pull request.

## Lisensi

[Sesuaikan dengan lisensi yang digunakan, misalnya MIT License, GPL, dll]
