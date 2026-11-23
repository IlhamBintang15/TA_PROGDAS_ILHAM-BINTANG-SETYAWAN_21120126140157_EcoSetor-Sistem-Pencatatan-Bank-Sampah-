#logika.py - Logika Bank Sampah (tanpa GUI).

import  json
import os
from datetime import datetime

#PENGATURAN
FILE_DATA = "data_bank_sampah.json"
MIN_PENARIKAN = 10000  # rupiah

LEVEL_NASABAH = [
  ("Sepuh", 150, 10),
  ("Abangkuh", 50, 5),
  ("Pemula", 0, 2),
]

KATEGORI_AWAL = {
    "Plastik": 2500,
    "Kardus": 15000,
    "Kertas": 12000,
    "Besi": 4800,
    "Kaca": 5000,
}

#FUNGSI
def tentukan_level(total_berat):
    """Mengembalikan (nama_level, bonus_persen) menurut total berat setoran."""
    for nama, minimal, bonus in LEVEL_NASABAH:
        if total_berat >= minimal:
            return nama, bonus
    # cadangan: level paling bawah
    return LEVEL_NASABAH[-1][0], LEVEL_NASABAH[-1][2]


def hitung_nilai(berat, harga_per_kg, bonus_persen=0):
    """Nilai rupiah satu setoran, sudah termasuk bonus level."""
    return int(round(berat * harga_per_kg * (1 + bonus_persen / 100)))

#KELAS
class 
