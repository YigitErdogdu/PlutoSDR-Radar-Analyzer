"""
sinyal_motoru.py - RF Sinyal İşleme Modülü
PlutoSDR sweep verilerinin okunması, FFT analizi ve tepe noktası tespiti
"""
import os
import glob
import numpy as np
import scipy.signal as sig


class SinyalIslemeMotoru:
    """
    Sweep verilerini okuyup işleyen ana sinyal motoru.
    
    .bin formatındaki IQ verileri üzerinde FFT çalıştırarak
    frekans-genlik spektrumu oluşturur.
    """
    
    # sabit parametreler
    ORNEK_SAYISI = 32768
    MEDYAN_KERNEL = 11
    KENAR_KIRPMA_ORANI = 0.12
    DONUSTURME_ESIK = 30000

    def __init__(self, veri_dizini: str):
        """
        Parametreler
        ----------
        veri_dizini : str
            .bin dosyalarının bulunduğu klasör yolu
        """
        self._veri_dizini = veri_dizini

    @property
    def veri_yolu(self) -> str:
        return self._veri_dizini

    def dosya_listesi_al(self):
        """Sweep dizinindeki .bin dosyalarını sıralı şekilde döndürür."""
        return sorted(glob.glob(os.path.join(self._veri_dizini, "*.bin")))

    def tek_dosya_isle_ve_dondur(self, dosya_yolu: str):
        """
        Tek bir .bin dosyasını işler, kırpılmış frekans ve genlik dizisi döner.
        Hata durumunda None döner.
        """
        return self._tek_dosya_isle(dosya_yolu)

    # ---- toplu işleme ----
    def verileri_hazirla(self):
        """Sweep dosyalarını oku, FFT uygula ve son grafiğe uygun veriyi döndür."""
        dosyalar = sorted(glob.glob(os.path.join(self._veri_dizini, "*.bin")))
        if not dosyalar:
            return None, None, None

        tum_frekanslar = []
        tum_genlikler = []

        for dosya in dosyalar:
            sonuc = self._tek_dosya_isle(dosya)
            if sonuc is None:
                continue
            frekans_dilimi, genlik_dilimi = sonuc
            tum_frekanslar.append(frekans_dilimi)
            tum_genlikler.append(genlik_dilimi)

        if not tum_frekanslar:
            return None, None, None

        birlesik_f = np.concatenate(tum_frekanslar)
        birlesik_g = np.concatenate(tum_genlikler)

        # çözünürlük düşürme (görselleştirme performansı için)
        ham_x, ham_y = self._cozunurluk_dusur(birlesik_f, birlesik_g)
        yumusak_y = sig.medfilt(ham_y, self.MEDYAN_KERNEL)

        return ham_x, yumusak_y, ham_y

    def tepe_noktalarini_bul(self, frekanslar, genlikler):
        """Medyan üzeri sinyalleri tespit et."""
        esik_seviyesi = np.median(genlikler) + 12
        tepeler, _ = sig.find_peaks(genlikler, height=esik_seviyesi, distance=50)
        return tepeler

    # ---- yardımcı metodlar ----
    def _tek_dosya_isle(self, dosya_yolu: str):
        """
        Tek bir .bin dosyasını okur ve FFT uygular.
        Başarısızlık durumunda None döner.
        """
        try:
            merkez_frekans = self._dosyadan_frekans_cek(dosya_yolu)
            baslangic = merkez_frekans - 7.5
            bitis = merkez_frekans + 7.5

            ham_veri = np.fromfile(dosya_yolu, dtype=np.int16, count=self.ORNEK_SAYISI)
            if len(ham_veri) < 2:
                return None

            # IQ ayırma
            i_kanal = ham_veri[0::2].astype(np.float32)
            q_kanal = ham_veri[1::2].astype(np.float32)

            # pencere ve FFT
            pencere = sig.windows.blackmanharris(len(i_kanal))
            kompleks_sinyal = (i_kanal + 1j * q_kanal) * pencere
            fft_sonuc = np.fft.fftshift(np.fft.fft(kompleks_sinyal))
            genlik_db = 20 * np.log10(np.abs(fft_sonuc) + 1e-12)

            f_eksen = np.linspace(baslangic, bitis, len(i_kanal))

            # kenar artefaktlarını kırp
            kirp = int(len(i_kanal) * self.KENAR_KIRPMA_ORANI)
            return f_eksen[kirp:-kirp], genlik_db[kirp:-kirp]

        except (ValueError, IndexError, OSError):
            return None

    @staticmethod
    def _dosyadan_frekans_cek(dosya_yolu: str) -> int:
        """Dosya adından merkez frekansı pars et (ör: sweep_433mhz.bin -> 433)."""
        isim = os.path.basename(dosya_yolu).lower()
        sayi_kismi = isim.split('_')[-1].replace('mhz.bin', '')
        return int(sayi_kismi)

    def _cozunurluk_dusur(self, frekanslar, genlikler):
        """Çok yoğun veriyi grafik için sadeleştir (alt örnekleme)."""
        eleman = len(genlikler)
        parca = max(1, eleman // self.DONUSTURME_ESIK)
        kesme = parca * self.DONUSTURME_ESIK

        y_blok = genlikler[:kesme].reshape(-1, parca)
        x_blok = frekanslar[:kesme].reshape(-1, parca)

        return x_blok.mean(axis=1), y_blok.max(axis=1)