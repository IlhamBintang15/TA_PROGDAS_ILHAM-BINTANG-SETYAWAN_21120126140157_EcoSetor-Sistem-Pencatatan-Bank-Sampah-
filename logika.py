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
    """Kelas pengelola yang memegang seluruh data."""
    def __init__(self):
        self.kategori = [] 
        self.nasabah = []
        self.riwayat = []
        for nama, harga in KATEGORI_AWAL.items():
            self.kategori.append(KategoriSampah(nama, harga))


#--------pencarian data--------
    def cari_nasabah(self, id_nasabah):
        for n in self.nasabah:
            if n.id == id_nasabah:
                return n 
            raise ValueError("Nasabah tidak ditemukan.")


    def cari_kategori(self, nama_kategori):
        for k in self.kategori:
            if k.nama == nama_kategori:
                return k
        raise ValueError("Kategori tidak ditemukan.")


# ---------- nasabah ----------
    def tambah_nasabah(self, nama, alamat):
        nama = nama.strip()
        alamat = alamat.strip()
        if nama == "":
            raise ValueError("Nama nasabah tidak boleh kosong.")
        if alamat == "":
            raise ValueError("Alamat atau RT tidak boleh kosong.")
        id_baru = "N" + str(len(self.nasabah) + 1).zfill(3)
        n = Nasabah(id_baru, nama, alamat)
        self.nasabah.append(n)
        return n

#           transaksi 
    def catat_setoran(self, id_nasabah, nama_kategori, berat):
        if berat <= 0:
            raise ValueError("Berat setoran harus lebih dari 0 kg.")
        n = self.cari_nasabah(id_nasabah)
        k = self.cari_kategori(nama_kategori)

        # Bonus memakai level SEBELUM setoran ini dihitung.
        _, bonus = tentukan_level(n.total_berat)
        nilai = hitung_nilai(berat, k.harga_per_kg, bonus)

        n.tambah_saldo(nilai)
        n.total_berat += berat
        t = Transaksi(self._sekarang(), n.id, "setor", k.nama, berat, nilai, bonus)
        self.transaksi.append(t)
        return t

    def tarik_saldo(self, id_nasabah, jumlah):
        n = self.cari_nasabah(id_nasabah)
        n.tarik_saldo(jumlah)  
        t = Transaksi(self._sekarang(), n.id, "tarik", "-", 0, jumlah)
        self.transaksi.append(t)
        return t

    def riwayat(self, id_nasabah=None):
        """Semua transaksi, atau hanya milik satu nasabah."""
        hasil = []
        for t in self.transaksi:
            if id_nasabah is None or t.id_nasabah == id_nasabah:
                hasil.append(t)
        return hasil

    #            rekap 
    def rekap_bulanan(self, tahun, bulan):
        """
        Mengembalikan dict:
          per_kategori : {nama: {"kg": ..., "rupiah": ...}}
          total_kg, total_rupiah
          top_nasabah  : (nama, kg) atau None
        Yang dihitung hanya transaksi setoran pada bulan tersebut.
        """
        awalan = f"{tahun:04d}-{bulan:02d}"
        per_kategori = {}
        kg_per_nasabah = {}
        total_kg = 0.0
        total_rupiah = 0

        for t in self.transaksi:
            if t.jenis != "setor" or not t.tanggal.startswith(awalan):
                continue
            if t.kategori not in per_kategori:
                per_kategori[t.kategori] = {"kg": 0.0, "rupiah": 0}
            per_kategori[t.kategori]["kg"] += t.berat
            per_kategori[t.kategori]["rupiah"] += t.nominal
            kg_per_nasabah[t.id_nasabah] = kg_per_nasabah.get(t.id_nasabah, 0.0) + t.berat
            total_kg += t.berat
            total_rupiah += t.nominal

        top = None
        for id_n, kg in kg_per_nasabah.items():
            if top is None or kg > top[1]:
                top = (self.cari_nasabah(id_n).nama, kg)

        return {
            "per_kategori": per_kategori,
            "total_kg": total_kg,
            "total_rupiah": total_rupiah,
            "top_nasabah": top,
        }

    #             simpan dan muat
    def simpan(self, path=FILE_DATA):
        data = {
            "kategori": [k.to_dict() for k in self.kategori],
            "nasabah": [n.to_dict() for n in self.nasabah],
            "transaksi": [t.to_dict() for t in self.transaksi],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def muat(path=FILE_DATA):
        bank = BankSampah()
        if not os.path.exists(path):
            return bank  # belum ada data, jadi pakai kategori awal
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        bank.kategori = [KategoriSampah.from_dict(d) for d in data.get("kategori", [])] or bank.kategori
        bank.nasabah = [Nasabah.from_dict(d) for d in data.get("nasabah", [])]
        bank.transaksi = [Transaksi.from_dict(d) for d in data.get("transaksi", [])]
        return bank

    @staticmethod
    def _sekarang():
        return datetime.now().strftime("%Y-%m-%d %H:%M")