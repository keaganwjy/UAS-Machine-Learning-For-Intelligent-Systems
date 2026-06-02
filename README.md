# PENGGUNAAN COMPUTER VISION UNTUK GAME SPACE INVADERS

Anggota Kelompok:
- Keagan Wijaya (36240041)
- Bryan Harijanto (36240045)

### Project Overview
Project yang kami kerjakan ini adalah hasil modifikasi game klasik Space Invaders agar bisa dimainkan dengan gerakan tangan. Project yang kami kerjakan ini menggunakan computer vision lewat webcam pada laptop, nantinya untuk menggerakkan karakter dalam game tidak menggunakan keyboard pada laptop melainkan menggunakan gerakan tangan secara real-time dan langsung diubah jadi kontrol buat pesawat di dalam game

##### Fitur Utama:
1. AI Hand Tracking (MediaPipe)
   - Tracking posisi tangan secara real-time.
   - Geser tangan ke kiri/kanan untuk gerakin pesawat (sumbu X).
   - Gestur nembak: tekuk jari telunjuk ke bawah (di bawah ruas jari yang lain).

2. Asynchronous Multithreading
   - Biar game nggak ngelag, proses berat AI (kamera & deteksi) 
     dijalanin di background (worker thread).
   - Urusan render grafik dan UI tetap jalan mulus di main thread 
     bawaan Pygame. FPS tetap aman!

3. Dynamic Difficulty & Bos Abadi (Immortal)
   - Makin tinggi levelnya, alien bakal gerak makin ngacir.
   - Bosnya sengaja dibikin abadi dan punya sistem "Rage". Makin 
     sering kamu tembaki, bosnya bakal makin ngamuk dan tembakannya 
     makin brutal.

### Game Objective
Di Space Invaders versi ini, tugas kamu adalah:

- Bertahan hidup! Jangan sampai nabrak atau kena peluru musuh.
- Basmi semua alien kroco (kecil) buat naik ke level selanjutnya.
- Tembaki bos abadi buat *farming* skor ekstra (tapi ingat, risiko ditanggung sendiri kalau bosnya ngamuk!).
- Kumpulin skor sebanyak-banyaknya sambil senam tangan.

### Project Architecture
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/4d11fa24-5012-4dd9-88e0-6c6241bf9f33" />


### Directory Structure
Space-Invaders-Vision
│
├── LICENSE
├── README
├── requirements.txt
└── space_invaders.py

### Quick Start
Pastikan webcam kalian sudah terpasang dan berfungsi dengan baik. Lalu silahkan jalankan file space_invaders.py

Kontrol game:
- Mouse: BUat klik tombol saat di layar menu.
- Keyboard: Tekan 'P' kalau mau Pause atau melanjutkan game.
- Tangan: Arahkan tangan ke kamera buat mulai gerak, munculkan jari telunjuk untuk menembak ke arah musuh

### System Mechanics
1. Procedural Pixel Art:
   Aset visual kayak pesawat, alien, sampai bosnya digenerate 
   langsung pakai string matriks di dalam kodenya. Nggak butuh 
   file `.png` eksternal sama sekali, terus langsung di-render 
   jadi Surface Pygame. Simpel dan ringan.

2. Sistem Boss Rage:
   Tiap kali peluru kamu kena bos, variabel `boss_rage` bakal nambah.
   Nah, delay tembakan bos dihitung pakai rumus ini:
   max(250, 1500 - (level * 100) - (boss_rage * 50))
   Intinya: makin sering ditembak, makin cepet dia balas dendam.

### Future Improvements
Beberapa ide buat pengembangan ke depannya kalau ada waktu luang:

[AI / VISION]
- Nambahin deteksi dua tangan biar bisa mode *co-op* atau keluarin *skill ultimate*.
- *Fine-tuning* deteksi gestur nembaknya biar lebih *smooth* dan akurat.

[GAMEPLAY]
- Kasih sistem *drop item* / *power-up* tiap kali ngehancurin alien.
- Bikin pola pergerakan alien atau bos lebih *random* biar makin menantang.

[AUDIO]
- Tambahin BGM retro sama efek suara (SFX) pas nembak atau meledak. Biar makin berasa *arcade*-nya.

[ENGINEERING]
- Rapihin kodenya (*Refactoring* ke OOP). Misahin logika generator art, mekanik game, sama AI ke file yang beda biar lebih *clean*.

### System Requirements
Minimum:
CPU      : Intel Core i3 / AMD Ryzen 3 (Wajib ada Webcam)
RAM      : 4 GB
Python   : 3.8+

Recommended:
CPU      : Intel Core i5 / AMD Ryzen 5
RAM      : 8 GB
Python   : 3.10+

### References
- Pygame Docs: https://www.pygame.org/docs/
- MediaPipe Hands: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
- OpenCV Python: https://pypi.org/project/opencv-python/

### License
MIT License

### Author
Project : Penggunaan Computer Vision Untuk Game Space Invaders
Purpose : Project yang saya dan teman saya kerjakan ini untuk memenuhi Ujian AKhir Semester (UAS) mata kuliah Machine Learning For Intelligence Systems
