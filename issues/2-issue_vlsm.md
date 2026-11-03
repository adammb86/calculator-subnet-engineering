# [Feature] Alokasi VLSM

## Deskripsi

Menambahkan kemampuan alokasi IP berbasis **Variable Length Subnet Mask
(VLSM)** pada aplikasi Kalkulator Subnet. VLSM memungkinkan pembagian blok
jaringan dengan ukuran subnet yang berbeda-beda sesuai kebutuhan host tiap
segmen, sehingga penggunaan alamat IP menjadi efisien.

Fungsi inti yang diimplementasikan dan diuji menggunakan `pytest`:

- `alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]`
  — mengalokasikan subnet secara berurutan dari yang kebutuhan terbesar ke
  terkecil.
- Endpoint `POST /api/vlsm` dengan body JSON
  `{ "network": "string", "kebutuhan_host": [int, ...] }`.

Seluruh detail (aturan validasi, logika perhitungan, dan tabel test case)
mengacu pada `SPEC.md`.

## Tugas

- [ ] Implementasikan `alokasi_vlsm` pada `main.py`.
- [ ] Validasi `network_cidr` sebagai alamat network yang valid (IP input harus
      sama dengan network hasil kalkulasinya) dan validasi `kebutuhan_host`.
- [ ] Urutkan `kebutuhan_host` dari terbesar ke terkecil (*descending*).
- [ ] Alokasikan blok secara berurutan dengan ukuran blok = pangkat 2 terkecil
      di mana `kapasitas >= kebutuhan + 2`, dengan batas blok terkecil `/30`.
- [ ] Lempar `ValueError` bila sisa blok tidak cukup menampung kebutuhan.
- [ ] Implementasikan endpoint `POST /api/vlsm`.
- [ ] Hubungkan tab VLSM di `index.html` ke endpoint API.
- [ ] Tulis seluruh test case VLSM di `test_main.py`.

## Kriteria Penerimaan

Test case berikut (merujuk `SPEC.md` §6) harus lulus dengan `pytest`:

| Kasus | Input | Hasil yang Diharapkan | Status |
| --- | --- | --- | --- |
| VLSM: Alokasi Normal | `192.168.1.0/24` (Host: 100, 50, 20, 2) | `/25` (.0), `/26` (.128), `/27` (.192), `/30` (.224) | Lulus |
| VLSM: Kapasitas Overload | `192.168.1.0/24` (Host: 200, 100) | Ditolak, blok tidak cukup (ValueError / HTTP 400) | Lulus |

## Alur Kerja

1. **Issue** — Issue dibuat di GitHub dari dokumen ini.
2. **Branch** — Buat branch `feature/issue-<nomor>-vlsm` dari `main`.
3. **Test dulu** — Tulis test VLSM di `test_main.py` terlebih dahulu (TDD *red*).
4. **Implementasi** — Implementasikan `alokasi_vlsm` dan endpoint `POST /api/vlsm`
   hingga test *green*.
5. **Commit** — Commit perubahan dengan pesan yang deskriptif.
6. **Pull request** — Buka PR dari branch menuju `main`.
7. **CI** — Pastikan pipeline CI (test + coverage) lulus.
8. **Merge** — Merge PR ke `main` setelah review dan CI hijau.