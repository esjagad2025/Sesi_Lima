Fungsi web :
- mencari jadwal praktek dokter
- dengan filter
- dilengkapi AI sederhana

data sqlite3 : data dummy

selain memakai requirements.txt
semua lokal instalasi berbasis streamlit 
juga memerlukan instalasi python Faker
database sqlite3

hal penting : web ini dimulai degan pertanyaan bantu AI sebagai saran/sugestion utk pengalihan hasil search karena kepadatan pasien diatas 10 ( saya anggap padat )
mulailah dengan filter : dokter umum pada hari senin ( menghasilkan saran , jika disetujui karenapasien padat ) , memunculkan nama dokter lain dan hari jumat ( oleh AI ). 
