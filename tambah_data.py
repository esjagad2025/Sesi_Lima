import sqlite3
import random
from faker import Faker
import os

# Nama file database harus sama dengan yang digunakan di aplikasi Streamlit
DB_FILE = "klinik_praktek.db"
JUMLAH_DATA_TAMBAHAN = 900

# Inisialisasi Faker untuk data Indonesia
fake = Faker('id_ID')

def tambah_data_baru():
    """Menambahkan data baru ke dalam tabel jadwal_praktek."""
    
    if not os.path.exists(DB_FILE):
        print(f"Error: File database '{DB_FILE}' tidak ditemukan.")
        print("Harap jalankan aplikasi Streamlit 'sesi_lima.py' terlebih dahulu untuk membuat database awal.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Cek jumlah data saat ini
    cursor.execute("SELECT COUNT(*) FROM jadwal_praktek")
    jumlah_awal = cursor.fetchone()[0]
    print(f"Jumlah data saat ini: {jumlah_awal} baris.")

    # Data master untuk pembuatan data acak
    spesialisasi_list = [
        "Dokter Umum", "Spesialis Anak (Sp.A)", "Spesialis Kandungan (Sp.OG)",
        "Spesialis Penyakit Dalam (Sp.PD)", "Spesialis Jantung (Sp.JP)",
        "Spesialis THT (Sp.THT-KL)", "Spesialis Kulit & Kelamin (Sp.KK)",
        "Dokter Gigi (drg.)", "Psikiater (Sp.KJ)", "Spesialis Mata (Sp.M)"
    ]
    hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    jam_list = ["08:00 - 12:00", "13:00 - 16:00", "17:00 - 20:00"]
    ruang_list = [f"Poli {chr(65+i)}{j}" for i in range(5) for j in range(1, 4)]

    print(f"Menambahkan {JUMLAH_DATA_TAMBAHAN} data baru...")

    # Loop untuk menambahkan data baru
    for i in range(JUMLAH_DATA_TAMBAHAN):
        # Membuat nama dokter yang panjang dan realistis
        gelar_depan = "Dr."
        nama_lengkap = f"{fake.first_name()} {fake.last_name()}"
        gelar_belakang_akademis = random.choice([", S.Ked", ", M.Kes", ""])
        spesialisasi = random.choice(spesialisasi_list)
        gelar_spesialis = f", {spesialisasi.split('(')[1].replace(')', '')}" if '(' in spesialisasi else ""
        
        nama_dokter_final = f"{gelar_depan} {nama_lengkap}{gelar_belakang_akademis}{gelar_spesialis}"
        
        hari = random.choice(hari_list)
        jam = random.choice(jam_list)
        ruang = random.choice(ruang_list)
        estimasi_pasien = random.randint(5, 45)

        cursor.execute('''
            INSERT INTO jadwal_praktek (nama_dokter, spesialisasi, hari_praktek, jam_praktek, ruang_praktek, estimasi_pasien)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nama_dokter_final, spesialisasi, hari, jam, ruang, estimasi_pasien))
        
        # Memberi feedback di terminal agar terlihat prosesnya
        if (i + 1) % 100 == 0:
            print(f"  -> {i + 1}/{JUMLAH_DATA_TAMBAHAN} data telah ditambahkan...")

    conn.commit()
    
    # Cek jumlah data setelah penambahan
    cursor.execute("SELECT COUNT(*) FROM jadwal_praktek")
    jumlah_akhir = cursor.fetchone()[0]
    
    conn.close()
    
    print("\nProses selesai!")
    print(f"Jumlah data akhir: {jumlah_akhir} baris.")

if __name__ == "__main__":
    tambah_data_baru()
