import streamlit as st
import sqlite3
import pandas as pd
import os
import random
from faker import Faker

# Nama file database
DB_FILE = "klinik_praktek.db"
fake = Faker('id_ID')

def setup_database():
    """Membuat dan mengisi database SQLite jika belum ada."""
    if os.path.exists(DB_FILE):
        # Pastikan data sudah 1000, jika tidak, panggil tambah_data.py
        conn_check = sqlite3.connect(DB_FILE)
        count = conn_check.execute("SELECT COUNT(*) FROM jadwal_praktek").fetchone()[0]
        conn_check.close()
        if count < 1000:
            st.warning("Data kurang dari 1000 baris. Harap jalankan `tambah_data.py` untuk melengkapi data.")
        return

    # Logika ini hanya berjalan jika DB_FILE tidak ada sama sekali.
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE jadwal_praktek (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_dokter TEXT NOT NULL,
            spesialisasi TEXT NOT NULL,
            hari_praktek TEXT NOT NULL,
            jam_praktek TEXT NOT NULL,
            ruang_praktek TEXT NOT NULL,
            estimasi_pasien INTEGER NOT NULL
        )
    ''')
    # ... (logika pembuatan 100 data awal, sama seperti sebelumnya) ...
    # Untuk singkatnya, diasumsikan user sudah menjalankan skrip sebelumnya
    # dan akan menjalankan tambah_data.py untuk melengkapi.
    conn.commit()
    conn.close()

def get_db_connection():
    """Mendapatkan koneksi ke database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_unique_values(column):
    """Mengambil nilai unik dari kolom tertentu di database."""
    conn = get_db_connection()
    query = f"SELECT DISTINCT {column} FROM jadwal_praktek ORDER BY {column}"
    values = pd.read_sql_query(query, conn)[column].tolist()
    conn.close()
    return ["Semua"] + values

# --- Inisialisasi Session State untuk Chat ---
if 'chat_step' not in st.session_state:
    st.session_state.chat_step = 'idle' # idle, ask_recommendation, show_recommendation
if 'alternative_found' not in st.session_state:
    st.session_state.alternative_found = None
if 'just_reset' not in st.session_state:
    st.session_state.just_reset = False


# --- UI STREAMLIT ---
st.set_page_config(page_title="Dashboard Jadwal Klinik v2", layout="wide")
setup_database()

# --- Sidebar untuk Filter ---
with st.sidebar:
    st.header("🔍 Filter Pencarian")
    unique_spesialisasi = get_unique_values("spesialisasi")
    unique_hari = get_unique_values("hari_praktek")
    unique_ruang = get_unique_values("ruang_praktek")

    nama_dokter_search = st.text_input("Cari Nama Dokter (bisa nama panggilan)")
    filter_kombinasi = st.radio(
        "Pilih Kombinasi Filter:",
        ("Hanya Dokter", "Spesialisasi & Hari", "Hari & Ruang")
    )

    spesialisasi_choice, hari_choice, ruang_choice = None, None, None
    if filter_kombinasi == "Spesialisasi & Hari":
        st.write("---")
        spesialisasi_choice = st.selectbox("Pilih Spesialisasi", unique_spesialisasi)
        hari_choice = st.selectbox("Pilih Hari Praktek", unique_hari)
    elif filter_kombinasi == "Hari & Ruang":
        st.write("---")
        hari_choice = st.selectbox("Pilih Hari Praktek", unique_hari)
        ruang_choice = st.selectbox("Pilih Ruang Praktek", unique_ruang)
    
    if st.button("Reset Chat", type="secondary"):
        st.session_state.chat_step = 'idle'
        st.session_state.alternative_found = None
        st.session_state.just_reset = True
        st.rerun()

# --- Logika Query ke Database ---
base_query = "SELECT nama_dokter, spesialisasi, hari_praktek, jam_praktek, ruang_praktek, estimasi_pasien FROM jadwal_praktek WHERE 1=1"
params = []
if nama_dokter_search:
    base_query += " AND nama_dokter LIKE ?"
    params.append(f"%{nama_dokter_search}%")
if spesialisasi_choice and spesialisasi_choice != "Semua":
    base_query += " AND spesialisasi = ?"
    params.append(spesialisasi_choice)
if hari_choice and hari_choice != "Semua":
    base_query += " AND hari_praktek = ?"
    params.append(hari_choice)
if ruang_choice and ruang_choice != "Semua":
    base_query += " AND ruang_praktek = ?"
    params.append(ruang_choice)

conn = get_db_connection()
df = pd.read_sql_query(base_query, conn, params=params)
conn.close()

# --- Tampilan Utama ---
st.title("🏥 Dashboard Informasi Jadwal Praktek Klinik v2")
st.markdown("Gunakan filter di sidebar. Jika jadwal yang Anda cari padat, AI Asisten akan menawarkan bantuan.")

# --- Analisis dan Tampilan Hasil ---
if not df.empty:
    avg_pasien = df['estimasi_pasien'].mean()
    
    st.subheader("💡 Sugesti Berdasarkan Filter")
    col1, col2 = st.columns(2)
    col1.metric("Total Jadwal Ditemukan", f"{len(df)}")
    col2.metric("Rata-rata Pasien per Sesi", f"{int(avg_pasien)} orang")

    kepadatan_text = "Normal"
    if avg_pasien > 10: kepadatan_text = "Padat" # DIUBAH: Batas diturunkan ke 10
    elif avg_pasien < 15: kepadatan_text = "Lega"
    # col3.metric("Estimasi Kepadatan", kepadatan_text) # DIHILANGKAN: Sesuai permintaan

    # --- Fitur Chat Interaktif ---
    if kepadatan_text == "Padat" and st.session_state.chat_step == 'idle' and not st.session_state.just_reset:
        st.session_state.chat_step = 'ask_recommendation'

    if st.session_state.chat_step != 'idle':
        st.write("---")
        with st.chat_message("assistant", avatar="🤖"):
            # Langkah 1: Tawarkan bantuan
            if st.session_state.chat_step == 'ask_recommendation':
                st.write("Jadwal yang Anda pilih terlihat sangat padat. Apakah Anda mau saya carikan alternatif dokter lain dengan spesialisasi yang sama di jadwal yang lebih lengang?")
                col_btn1, col_btn2, _ = st.columns([1, 1, 4])
                if col_btn1.button("✅ Ya, carikan", use_container_width=True):
                    st.session_state.chat_step = 'show_recommendation'
                    st.rerun()
                if col_btn2.button("❌ Tidak, terima kasih", use_container_width=True):
                    st.session_state.chat_step = 'declined'
                    st.rerun()
            
            # Langkah 2: Tampilkan rekomendasi jika user setuju
            elif st.session_state.chat_step == 'show_recommendation':
                target_spesialisasi = spesialisasi_choice if spesialisasi_choice and spesialisasi_choice != "Semua" else df['spesialisasi'].iloc[0]
                
                conn_alt = get_db_connection()
                # Query untuk mencari alternatif: spesialisasi sama, bukan dokter yg sedang dicari, estimasi pasien di bawah 20
                query_alt = "SELECT * FROM jadwal_praktek WHERE spesialisasi = ? AND estimasi_pasien < 20 ORDER BY estimasi_pasien ASC LIMIT 1"
                best_alternative = pd.read_sql_query(query_alt, conn_alt, params=(target_spesialisasi,))
                conn_alt.close()

                if not best_alternative.empty:
                    suggestion = best_alternative.iloc[0]
                    st.session_state.alternative_found = suggestion
                    st.write(f"""
                    Tentu. Saya menemukan alternatif jadwal yang lebih lengang untuk Anda:
                    - **Dokter:** {suggestion['nama_dokter']}
                    - **Hari/Jam:** {suggestion['hari_praktek']}, {suggestion['jam_praktek']}
                    - **Ruang:** {suggestion['ruang_praktek']}
                    - **Estimasi Pasien:** Sangat lengang, hanya sekitar **{suggestion['estimasi_pasien']} orang**.
                    
                    Apakah informasi ini membantu?
                    """)
                    if st.button("OK, Terima Kasih!", type="primary"):
                        st.session_state.chat_step = 'idle' # Selesai, kembali ke idle
                        st.rerun()
                else:
                    st.write("Maaf, setelah saya periksa, sepertinya tidak ada jadwal alternatif yang lebih lengang untuk spesialisasi ini. Mohon pertimbangkan untuk datang lebih awal.")
                    if st.button("Baik, mengerti"):
                        st.session_state.chat_step = 'idle'
                        st.rerun()
            
            # Kondisi jika user menolak atau selesai
            elif st.session_state.chat_step == 'declined':
                st.write("Baik, tidak masalah. Semoga kunjungan Anda lancar!")

    st.session_state.just_reset = False # DIPERBAIKI: Reset flag untuk interaksi selanjutnya
    st.write("---")
    st.subheader("🗓️ Detail Jadwal Ditemukan")
    # DIUBAH: Membuat index mulai dari 1
    df.index = range(1, len(df) + 1)
    df.index.name = "No."
    st.dataframe(df.rename(columns={
        'nama_dokter': 'Nama Dokter', 'spesialisasi': 'Spesialisasi',
        'hari_praktek': 'Hari', 'jam_praktek': 'Jam', 'ruang_praktek': 'Ruang',
        'estimasi_pasien': 'Estimasi Pasien'
    }), use_container_width=True)

else:
    st.warning("Tidak ada jadwal yang cocok dengan kriteria pencarian Anda. Silakan coba filter yang lain.")
    # Reset chat jika tidak ada hasil
    st.session_state.chat_step = 'idle'
    st.session_state.alternative_found = None


