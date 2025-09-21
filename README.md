Fungsi web :
- mencari jadwal praktek dokter
- dengan filter
- dilengkapi AI sederhana

data sqlite3 : data dummy

selain memakai requirements.txt
semua lokal instalasi berbasis streamlit 
juga memerlukan instalasi python Faker
database sqlite3

steps :
jalankan dahulu file : sesi_lima_app_versi2.py
tambahkan data dengan file : tambah_data.py sehingga data jadi 1000.

hal penting : web ini dimulai degan pertanyaan bantu AI sebagai saran/sugestion utk pengalihan hasil search karena kepadatan pasien diatas 10 ( saya anggap padat )
mulailah dengan filter : dokter umum pada hari senin ( menghasilkan saran , jika disetujui karenapasien padat ) , memunculkan nama dokter lain dan hari jumat ( oleh AI ). 

pengembangan belum selesai . meski dibantu koding dengan AI.
Karena waktu tidak mencukupi : problem instalasi Conda pada OS microsoft gagal hingga waktu akhir , terpaksa pakai linux dalam Virtualisasi .
