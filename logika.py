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
class KategoriSampah:
    def __init__(self, nama, harga_per_kg):
        self.nama = nama
        self.harga_per_kg = harga_per_kg

    def to_dict(self):
        return {"nama": self.nama, "harga_per_kg": self.harga_per_kg}

    @staticmethod
    def from_dict(d):
        return KategoriSampah(d["nama"], d["harga_per_kg"])


class Nasabah:
    def __init__(self, id_nasabah, nama, alamat, saldo=0, total_berat=0.0):
        self.id = id_nasabah
        self.nama = nama
        self.alamat = alamat
        self.saldo = saldo
        self.total_berat = total_berat

    def tambah_saldo(self, jumlah):
        if jumlah <= 0:
            raise ValueError("Jumlah saldo yang ditambahkan harus lebih dari 0.")
        self.saldo += jumlah

    def tarik_saldo(self, jumlah):
        if jumlah <= 0:
            raise ValueError("Jumlah penarikan harus lebih dari 0.")
        if jumlah < MIN_PENARIKAN:
            raise ValueError(f"Minimal penarikan Rp{MIN_PENARIKAN:,}.".replace(",", "."))
        if jumlah > self.saldo:
            raise ValueError("Saldo tidak cukup.")
        self.saldo -= jumlah

    def level(self):
        """Nama level nasabah saat ini."""
        return tentukan_level(self.total_berat)[0]

    def to_dict(self):
        return {
            "id": self.id,
            "nama": self.nama,
            "alamat": self.alamat,
            "saldo": self.saldo,
            "total_berat": self.total_berat,
        }

    @staticmethod
    def from_dict(d):
        return Nasabah(d["id"], d["nama"], d["alamat"], d["saldo"], d["total_berat"])


class Transaksi:
    """Satu baris riwayat. jenis = 'setor' atau 'tarik'."""

    def __init__(self, tanggal, id_nasabah, jenis, kategori, berat, nominal, bonus_persen=0):
        self.tanggal = tanggal  # format "YYYY-MM-DD HH:MM"
        self.id_nasabah = id_nasabah
        self.jenis = jenis
        self.kategori = kategori
        self.berat = berat
        self.nominal = nominal
        self.bonus_persen = bonus_persen

    def to_dict(self):
        return dict(self.__dict__)

    @staticmethod
    def from_dict(d):
        return Transaksi(
            d["tanggal"], d["id_nasabah"], d["jenis"], d["kategori"],
            d["berat"], d["nominal"], d.get("bonus_persen", 0),
        )

class BankSampah:
    