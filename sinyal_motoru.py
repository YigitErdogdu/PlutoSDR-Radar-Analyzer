"""
sinyal_motoru.py - RF Sinyal İşleme Modülü (Ağır Siklet & %50 Overlap)
PlutoSDR C-Server ile konuşur.
20 MHz Bant Genişliği, 10 MHz Adım (%50 Örtüşme), 1 Milyon Örnek, 2048 FFT.
"""
import socket
import struct
import numpy as np
import scipy.signal as sig

class SinyalIslemeMotoru:
    def __init__(self, ip_address="192.168.2.1", port=80):
        self.ip = ip_address
        self.port = port
        self.sock = None
        self._baglan()

    def _baglan(self):
        """TCP üzerinden Pluto içindeki sunucuya bağlanır."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            print(f"Pluto C-Server'a Bağlanıldı: {self.ip}:{self.port}")
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")

    def taramayi_baslat(self):
        """
        Pluto'ya AĞIR SIKLET tarama komutunu gönderir.
        Start: 100 MHz
        Stop:  3000 MHz
        Step:  10 MHz (10000000)
        BW:    20 MHz (20000000)
        Örnek: 1 Milyon (1000000)
        Kazanç: 60 dB
        """
        if not self.sock: return
        
        komut = "SWEEP START 100000000 3000000000 10000000 20000000 1000000 60 10000\n"
        self.sock.sendall(komut.encode('utf-8'))
        print("Keskin Nişancı Tarama (%50 Overlap, 1M Örnek) başlatıldı!")

    def taramayi_durdur(self):
        """Taramayı durdurur."""
        if self.sock:
            self.sock.sendall(b"SWEEP STOP\n")

    def _tam_veri_al(self, byte_sayisi):
        """1 Milyon örnek = 4 MB veriyi RAM'i yormadan çeker."""
        veri = bytearray(byte_sayisi)
        view = memoryview(veri)
        alinan = 0
        while alinan < byte_sayisi:
            paket_boyu = self.sock.recv_into(view[alinan:], byte_sayisi - alinan)
            if not paket_boyu:
                return None
            alinan += paket_boyu
        return bytes(veri)

    def siradaki_bandi_oku(self):
        """Ham veriyi alır, FFT shift ve %50 Overlap kesimi yapar."""
        if not self.sock: return None, None, None

        magic_data = self._tam_veri_al(4)
        if not magic_data: return None, None, None
        
        magic = struct.unpack('<I', magic_data)[0]

        if magic == 0x00000000:
            return "TUR_SONU", None, None

        if magic == 0xDEADBEEF:
            hdr_data = self._tam_veri_al(16)
            freq_hz, samp_rate, n_samples = struct.unpack('<QII', hdr_data)

            iq_data = self._tam_veri_al(n_samples * 4)
            ham_veri = np.frombuffer(iq_data, dtype=np.int16)
            i_kanal = ham_veri[0::2].astype(np.float32)
            q_kanal = ham_veri[1::2].astype(np.float32)
            
            # ADIM 1: 12-bit ADC Normalizasyonu
            kompleks_sinyal = (i_kanal + 1j * q_kanal) / 2048.0

            # ADIM 2: LO Leakage (DC Offset) Temizliği
            kompleks_sinyal = kompleks_sinyal - np.mean(kompleks_sinyal)

            # ADIM 3: Welch PSD (Yüksek Çözünürlük: 2048 FFT)
            f, psd = sig.welch(kompleks_sinyal, fs=samp_rate, 
                               window='blackman', 
                               nperseg=2048, 
                               return_onesided=False,
                               scaling='density')
            
            # ADIM 4: FFT SHIFT
            f = np.fft.fftshift(f)
            psd = np.fft.fftshift(psd)

            # ADIM 5: Gerçek RF Frekansları
            f_eksen = f + freq_hz
            genlik_db = 10 * np.log10(psd + 1e-20)

            # 🛠️ ADIM 6: %50 OVERLAP KESİMİ (Kusursuz Dikiş)
            # 20 MHz'lik bandın sadece ortadaki 10 MHz'ini alıyoruz.
            # Yani soldan %25, sağdan %25 kesiyoruz.
            kesim_miktari = len(f_eksen) // 4  
            
            f_temiz = f_eksen[kesim_miktari:-kesim_miktari]
            genlik_temiz = genlik_db[kesim_miktari:-kesim_miktari]

            return freq_hz, f_temiz, genlik_temiz

        return None, None, None

    def akilli_esik_tespit(self, f_eksen, genlik_db):
        gurultu_tabani = np.median(genlik_db)
        esik_degeri = gurultu_tabani + 12 
        tepeler, _ = sig.find_peaks(genlik_db, height=esik_degeri, distance=10)
        
        hedefler = []
        for p in tepeler:
            hedefler.append({"frekans": f_eksen[p] / 1e6, "guc": genlik_db[p]})
        return hedefler