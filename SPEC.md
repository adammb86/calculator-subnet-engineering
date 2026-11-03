Berikut adalah spesifikasi teknis untuk pengembangan Kalkulator Subnet dan VLSM. Anda dapat menyimpan teks di bawah ini langsung sebagai file `SPEC.md`.

---

# Spesifikasi Teknis: Kalkulator Subnet & VLSM

## 1. Tujuan

Membangun aplikasi berbasis web (Single Page Application) dengan backend Python 3.12 (FastAPI) untuk menghitung parameter subnetting IPv4 dan alokasi Variable Length Subnet Mask (VLSM). Aplikasi ini dirancang untuk memastikan akurasi perhitungan standar jaringan termasuk implementasi *edge cases* seperti RFC 3021.

## 2. Aturan Validasi

Seluruh input yang masuk ke sistem harus melewati aturan validasi ketat berikut sebelum diproses:

* **Alamat IPv4:** Harus memiliki tepat 4 oktet yang dipisahkan oleh titik. Setiap oktet harus bernilai antara `0` hingga `255`. Tidak diperbolehkan ada angka nol di depan (*leading zeros*, contoh: `192.168.01.1` ditolak) dan tidak boleh mengandung spasi.
* **Prefix CIDR:** Harus berupa bilangan bulat (integer) dengan rentang `0` hingga `32`.
* **Kebutuhan Host (VLSM):** Harus berupa *array/list* bilangan bulat. List tidak boleh kosong dan setiap elemen (kebutuhan host) harus bernilai `>= 1`.

## 3. Kontrak Fungsi

Fungsi-fungsi inti ini akan ditempatkan di `main.py` dan diuji secara menyeluruh di `test_main.py` menggunakan `pytest`.

### A. `hitung_subnet(ip: str, prefix: int) -> dict`

Melakukan kalkulasi parameter subnet berdasarkan IP dan prefix.

* **Logika Perhitungan:**
* Jika input IP atau prefix tidak sesuai *Aturan Validasi*, lemparkan `ValueError`.
* `network` dihitung secara *bitwise* (IP `AND` subnet mask).
* Untuk prefix `/0` sampai `/30`:
* `usable_hosts` = $2^{(32 - \text{prefix})} - 2$.


* Untuk prefix `/31` (Aturan Point-to-Point RFC 3021):
* `usable_hosts` = 2.
* `broadcast` = `None`.
* `first_host` dan `last_host` menggunakan seluruh blok jaringan.


* Untuk prefix `/32` (Host Route):
* `usable_hosts` = 1.
* `broadcast` = `None`.
* `first_host` = `last_host` = IP itu sendiri.




* **Struktur Kembalian (Dictionary):** Memuat kunci `mask`, `network`, `broadcast`, `first_host`, `last_host`, dan `usable_hosts`.

### B. `alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]`

Melakukan alokasi IP berdasarkan metode VLSM agar penggunaan IP efisien.

* **Logika Perhitungan:**
* Pisahkan `network_cidr` menjadi IP dan Prefix, lalu validasi. Lemparkan `ValueError` jika `network_cidr` bukan alamat *network* yang valid (IP input tidak sama dengan IP *network* hasil kalkulasinya).
* Lemparkan `ValueError` jika `kebutuhan_host` kosong atau berisi nilai `< 1`.
* Urutkan `kebutuhan_host` dari nilai terbesar ke terkecil (*descending*).
* Iterasi alokasi secara berurutan mulai dari alamat *network* awal.
* **Ukuran Blok:** Untuk setiap kebutuhan, cari pangkat 2 terkecil di mana $\text{kapasitas} \ge \text{kebutuhan} + 2$. Batas prefix alokasi maksimum (blok terkecil) adalah `/30`.
* Jika sisa blok IP tidak cukup untuk menampung seluruh kebutuhan yang tersisa, lemparkan `ValueError`.


* **Struktur Kembalian (List of Dictionaries):** Mengembalikan *list* di mana setiap elemen memuat kunci `kebutuhan`, `network_cidr`, beserta seluruh kunci yang dihasilkan oleh fungsi `hitung_subnet`.

## 4. Kontrak API

Sistem mengekspos 3 *endpoint* utama:

1. **`GET /`**
* **Tujuan:** Menyajikan antarmuka pengguna (Halaman Web HTML).
* **Response:** File `index.html` (Content-Type: `text/html`).


2. **`GET /api/subnet`**
* **Query Parameters:** `ip` (string), `prefix` (integer).
* **Response Sukses (200 OK):** JSON berisi hasil dari fungsi `hitung_subnet`.
* **Response Gagal (400 Bad Request):** JSON `{ "detail": "Pesan error spesifik" }`.


3. **`POST /api/vlsm`**
* **Body (JSON):** `{ "network": "string", "kebutuhan_host": [int, int, ...] }`.
* **Response Sukses (200 OK):** JSON berisi hasil dari fungsi `alokasi_vlsm`.
* **Response Gagal (400 Bad Request):** JSON `{ "detail": "Pesan error spesifik" }`.



## 5. Halaman Web

Antarmuka pengguna diimplementasikan dalam satu berkas HTML mandiri dengan spesifikasi berikut:

* Terdapat navigasi atau tab untuk beralih antara dua mode: **Mode Subnet** dan **Mode VLSM**.
* Input divalidasi terlebih dahulu di sisi klien (*client-side*) sebelum dikirim ke API.
* Hasil kalkulasi dirender dalam bentuk tabel yang mudah dibaca (*scannable*).
* Pesan *error* dari API (HTTP 400) ditangkap dan ditampilkan ke pengguna menggunakan kotak peringatan yang mencolok dan deskriptif.

## 6. Tabel Test Case

Berikut adalah metrik pengujian yang harus diimplementasikan pada `test_main.py` menggunakan `pytest`:

| Kasus | Input | Hasil yang Diharapkan | Status |
| --- | --- | --- | --- |
| **Subnet Standar** | `172.16.5.130/25` | Network: `172.16.5.128`, Broadcast: `172.16.5.255`, Host: 126 | Lulus |
| **Blok Minimum Standar** | `10.0.0.0/30` | Host `.1` sampai `.2`, Broadcast: `.3`, Host: 2 | Lulus |
| **Point-to-Point (RFC 3021)** | `192.168.1.0/31` | Point-to-point, Broadcast: `None`, Host: 2 | Lulus |
| **Host Route** | `192.168.1.5/32` | Network/IP/Broadcast tunggal, Host: 1 | Lulus |
| **IP Tidak Valid (Oktet >255)** | `256.1.1.1/24` | Ditolak (ValueError / HTTP 400) | Lulus |
| **IP Tidak Valid (Leading Zero)** | `192.168.01.1/24` | Ditolak (ValueError / HTTP 400) | Lulus |
| **Format Input Rusak** | `192.168.1`, `abc`, Kosong | Ditolak (ValueError / HTTP 400) | Lulus |
| **Prefix di Luar Batas** | Prefix `33`, Prefix `-1` | Ditolak (ValueError / HTTP 400) | Lulus |
| **VLSM: Alokasi Normal** | `192.168.1.0/24` (Host: 100, 50, 20, 2) | `/25` (.0), `/26` (.128), `/27` (.192), `/30` (.224) | Lulus |
| **VLSM: Kapasitas Overload** | `192.168.1.0/24` (Host: 200, 100) | Ditolak, blok tidak cukup (ValueError / HTTP 400) | Lulus |

## 7. Di Luar Cakupan (Out of Scope)

Fungsionalitas berikut secara eksplisit tidak termasuk dalam fase pengembangan ini:

* Dukungan untuk kalkulasi dan alokasi IPv6.
* Penyimpanan riwayat perhitungan ke *database*.
* Sistem autentikasi dan otorisasi pengguna.
* Pembuatan topologi visual atau ekspor hasil ke format PDF/CSV.