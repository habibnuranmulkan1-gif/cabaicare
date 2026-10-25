# CabaiCare — Botanical Care Studio

Aplikasi sistem pakar untuk rekomendasi awal pemupukan tanaman cabai. Antarmuka dibuat dengan inspirasi visual natural: warna hijau sage, krem hangat, dan aksen merah cabai; ilustrasi kebun dibuat khusus dalam format SVG, ditambah kartu informasi, ikon, visual nilai CF, dan tata letak responsif.

## Fitur

- Konsultasi gejala tanaman cabai pada fase vegetatif atau generatif.
- Mesin inferensi berbasis **forward chaining**.
- Perhitungan dan penggabungan **Certainty Factor (CF)**.
- Penjelasan proses penalaran: WHY dan HOW.
- Basis pengetahuan IF–THEN: tambah, edit, hapus, cari, dan lihat aturan.
- Riwayat konsultasi dengan pencarian, grafik ringkas, dan ekspor CSV.
- Unduh laporan konsultasi dalam format TXT.
- Tema tampilan terang dan malam.
- Referensi awal dan catatan batasan sistem.

## Sumber pengetahuan dan fase tanaman

Daftar sumber dan pemetaan ID sumber ke rule tersimpan di `knowledge_base.json`:

- `S1` memberi konteks umum budidaya cabai.
- `S2` menjadi rujukan awal untuk rule gejala defisiensi `R01` sampai `R10`. Cocokkan setiap rule dengan isi dan halaman dokumen sebelum laporan final; gejala visual tidak memastikan defisiensi.
- `S3` mendukung panduan pemupukan menurut fase, bukan diagnosis gejala. Artikel menyebut nitrogen umumnya diberikan pada fase vegetatif, sementara fosfor dan kalium umumnya pada fase generatif, serta menekankan dosis sesuai kebutuhan.

Fase vegetatif/generatif memengaruhi panduan yang ditambahkan ke rekomendasi dan reasoning trace. Fase tidak mengubah rule diagnosis atau nilai CF, karena referensi fase mendukung waktu pemupukan, bukan kepastian diagnosis gejala.

## Instalasi dan menjalankan

Pastikan Python sudah terpasang. Buka terminal di folder ini, lalu jalankan:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app_.py
```

Aplikasi biasanya terbuka di `http://localhost:8501`.

Pada Windows, kamu juga bisa menjalankan file `run_windows.bat`.

## Pengujian mesin inferensi

Jalankan perintah ini dari folder project:

```bash
python -m unittest discover -s tests -v
```

## File utama

- `app_.py` — antarmuka dan alur aplikasi Streamlit.
- `engine.py` — mesin inferensi dan perhitungan CF.
- `knowledge_base.json` — data gejala dan aturan IF–THEN.
- `storage.py` — penyimpanan basis pengetahuan dan riwayat konsultasi.
- `test_cases.csv` — contoh skenario pengujian.
- `assets/ilustrasi_kebun_cabai.svg` — ilustrasi kebun cabai yang digunakan sebagai referensi aset visual.

## Catatan akademik

Aturan dan nilai CF dalam project adalah basis pengetahuan awal untuk demonstrasi UTS. Gejala visual tidak membuktikan kekurangan unsur hara secara pasti. Verifikasi kondisi tanah, air, pH, akar, hama, dan penyakit; jangan menentukan dosis pupuk hanya dari hasil aplikasi. Validasi isi aturan dengan literatur pertanian dan arahan dosen sebelum presentasi akhir.
