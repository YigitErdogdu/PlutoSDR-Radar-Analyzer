"""
ana_uygulama.py - HUB-10 Radar Analiz Sistemi
Ana pencere, giriş ekranı ve radar sahne yönetimi

Kullanım:
    python ana_uygulama.py
"""
import os
import sys
import numpy as np
import matplotlib

# --- PLATFORM UYUMLULUK ---
# Qt platform eklentisi Windows'ta bazen yanlış dizinden aranabiliyor
if sys.platform == 'win32':
    try:
        import PyQt5
        _qt_plugin = os.path.join(os.path.dirname(PyQt5.__file__),
                                  "Qt5", "plugins", "platforms")
        if os.path.exists(_qt_plugin):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = _qt_plugin
    except Exception:
        pass

# matplotlib metin renkleri (koyu arka plan uyumluluğu)
matplotlib.rcParams.update({
    'text.color':       'white',
    'axes.labelcolor':  'white',
    'xtick.color':      'white',
    'ytick.color':      'white',
})

from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget,
                              QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel)
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

from sinyal_motoru import SinyalIslemeMotoru
from radar_ekrani import RadarSahnesi


# =====================================================================
#  Sabitler
# =====================================================================
PENCERE_BASLIGI = "HUB 10 - RADAR ANALİZ SİSTEMİ"
PENCERE_BOYUT = (1280, 800)
ARKAPLAN_DOSYASI = "wp6047743.jpg"
KARARTMA_ALFA = 160

SWEEP_VERI_DIZINI = os.path.join("D:", os.sep, "PyQt_Dersleri", "sweep_data")

# frekans ekseni
FREKANS_MIN = 325
FREKANS_MAX = 3015
FREKANS_ADIM = 10

# renk paleti
RENK = {
    'zemin':        '#070b14',
    'beyaz_yumusak': '#f0f0f0',
    'yesil_neon':   '#39ff14',
    'yesil_koyu':   '#2ecc71',
    'amber':        'rgba(234, 179, 8, 0.6)',
    'yesil_soluk':  'rgba(57, 255, 20, 0.65)',
    'durum_yesil':  'rgba(100, 200, 100, 0.7)',
    'grafik_ana':   '#00ffff',
    'grafik_ham':   '#2c3e50',
    'esik_renk':    '#eab308',
    'eksen_gri':    '#999999',
    'cerceve_gri':  '#333333',
}


# =====================================================================
#  Ana Pencere
# =====================================================================
class AnaPencere(QMainWindow):
    """
    Uygulamanın ana penceresi.
    Giriş ve radar ekranları arasında geçiş sağlar.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(PENCERE_BASLIGI)
        self.setGeometry(100, 100, *PENCERE_BOYUT)

        # sahne yöneticisi (stacked widget ile ekran geçişleri)
        self.sahne_yoneticisi = QStackedWidget()
        self.setCentralWidget(self.sahne_yoneticisi)

        # sinyal motoru
        self.motor = SinyalIslemeMotoru(SWEEP_VERI_DIZINI)

        # ekranları oluştur
        self._giris_ekrani_kur()
        self._radar_ekrani_kur()

    # ------------------------------------------------------------------
    #  Giriş Ekranı
    # ------------------------------------------------------------------
    def _giris_ekrani_kur(self):
        """Başlangıç splash ekranını hazırlar."""
        self.giris_widget = QWidget()
        self.giris_widget.setStyleSheet(f"background-color: {RENK['zemin']};")

        # arkaplan fotoğrafı
        self._arkaplan_ayarla()

        # üst logo
        ust_logo = self._etiket_olustur(
            "[ PLUTOSDR ]", self.giris_widget,
            renk=RENK['amber'], boyut=13, bosluk=6
        )

        # ana başlık
        baslik = self._etiket_olustur(
            "HUB-10\nSİNYAL ANALİZ SİSTEMİ", self.giris_widget,
            renk=RENK['beyaz_yumusak'], boyut=42, kalin=True, bosluk=3
        )

        # alt başlık
        alt_baslik = self._etiket_olustur(
            "Geniş Spektrum RF Tarama & Hedef Analizi", self.giris_widget,
            renk=RENK['yesil_soluk'], boyut=15, bosluk=1
        )

        # başlat butonu
        self.btn_baslat = QPushButton("▶  SİSTEMİ BAŞLAT", self.giris_widget)
        self.btn_baslat.setFixedSize(300, 60)
        self.btn_baslat.setCursor(Qt.PointingHandCursor)
        self.btn_baslat.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #d4d4d4;
                border: 2px solid {RENK['yesil_neon']};
                border-radius: 6px;
                font-size: 17px; font-weight: bold;
                font-family: 'Courier New'; letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: {RENK['yesil_neon']};
                color: {RENK['zemin']}; border-color: {RENK['yesil_neon']};
            }}
            QPushButton:pressed {{
                background-color: {RENK['yesil_koyu']};
                border-color: {RENK['yesil_koyu']}; color: {RENK['zemin']};
            }}
        """)
        self.btn_baslat.clicked.connect(self._radar_sahnesine_gec)

        # durum çubuğu
        durum = self._etiket_olustur(
            "• SİSTEM HAZIR  •  VERİ YOLU: sweep_data  •", self.giris_widget,
            renk=RENK['durum_yesil'], boyut=11, bosluk=2
        )

        # düzen
        layout = QVBoxLayout(self.giris_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(2)
        layout.addWidget(ust_logo)
        layout.addSpacing(15)
        layout.addWidget(baslik)
        layout.addSpacing(10)
        layout.addWidget(alt_baslik)
        layout.addSpacing(40)
        layout.addWidget(self.btn_baslat, alignment=Qt.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(durum)
        layout.addStretch(3)

        self.lbl_arkaplan.lower()
        self.sahne_yoneticisi.addWidget(self.giris_widget)

        # pencere boyutuyla birlikte arka planı da genişlet
        self.giris_widget.resizeEvent = self._arkaplan_yeniden_boyutla

    def _arkaplan_ayarla(self):
        """Giriş ekranı arka plan görselini ayarlar ve karartma uygular."""
        resim_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  ARKAPLAN_DOSYASI)
        self.lbl_arkaplan = QLabel(self.giris_widget)
        self.lbl_arkaplan.setGeometry(0, 0, *PENCERE_BOYUT)
        self.lbl_arkaplan.setScaledContents(True)

        if not os.path.exists(resim_yolu):
            return

        orijinal = QPixmap(resim_yolu)

        # karartma katmanı
        karanlik = QPixmap(orijinal.size())
        karanlik.fill(Qt.transparent)
        p = QPainter(karanlik)
        p.fillRect(karanlik.rect(), QColor(0, 0, 0, KARARTMA_ALFA))
        p.end()

        # birleştirilmiş görsel
        birlesik = QPixmap(orijinal.size())
        p2 = QPainter(birlesik)
        p2.drawPixmap(0, 0, orijinal)
        p2.drawPixmap(0, 0, karanlik)
        p2.end()

        self.lbl_arkaplan.setPixmap(birlesik)

    def _arkaplan_yeniden_boyutla(self, event):
        """Pencere boyutu değiştiğinde arka planı uyarlar."""
        self.lbl_arkaplan.setGeometry(0, 0, event.size().width(), event.size().height())

    # ------------------------------------------------------------------
    #  Radar Ekranı
    # ------------------------------------------------------------------
    def _radar_ekrani_kur(self):
        """Radar sahnesini ve kontrol butonlarını oluşturur."""
        self.radar_sahne = RadarSahnesi()

        # --- üst kontrol paneli ---
        kontrol_bandi = QWidget()
        kontrol_bandi.setStyleSheet("background-color: #000000;")
        band_layout = QHBoxLayout(kontrol_bandi)
        band_layout.setContentsMargins(0, 0, 0, 0)
        band_layout.setSpacing(10)

        # geri butonu
        self.btn_geri = self._kontrol_butonu_olustur(
            "◀  GİRİŞ EKRANI", 200, "#ff3131", "#ff3131"
        )
        self.btn_geri.clicked.connect(self._giris_ekranina_don)

        # yenile butonu
        self.btn_yenile = self._kontrol_butonu_olustur(
            "🔄  VERİYİ YENİLE", 220, "#eab308", "#eab308"
        )
        self.btn_yenile.clicked.connect(self._grafik_ciz)

        band_layout.addWidget(self.btn_geri)
        band_layout.addStretch()
        band_layout.addWidget(self.btn_yenile)

        self.radar_sahne.layout.insertWidget(0, kontrol_bandi)
        self.sahne_yoneticisi.addWidget(self.radar_sahne)

    # ------------------------------------------------------------------
    #  Ekran geçişleri
    # ------------------------------------------------------------------
    def _radar_sahnesine_gec(self):
        """Giriş ekranından radar sahnesine geçiş yapar."""
        self.btn_baslat.setText("Radar Detayları Çiziliyor...")
        QApplication.processEvents()
        self._grafik_ciz()
        self.sahne_yoneticisi.setCurrentWidget(self.radar_sahne)

    def _giris_ekranina_don(self):
        """Radar sahnesinden giriş ekranına döner."""
        self.btn_baslat.setText("▶  SİSTEMİ BAŞLAT")
        self.sahne_yoneticisi.setCurrentWidget(self.giris_widget)

    # ------------------------------------------------------------------
    #  Grafik çizimi
    # ------------------------------------------------------------------
    def _grafik_ciz(self):
        """
        Animasyonlu grafik çizimi — tüm çizgi katmanları dahil.
        Veri önceden işlenir, çizgi akıcıca ilerler, kartlar tek tek gelir.
        """
        ham_x, yumusak_y, ham_y = self.motor.verileri_hazirla()

        if ham_x is None:
            self.btn_baslat.setText("VERİ HATASI!")
            return

        toplam = len(ham_x)
        KARE = 250
        self._a_x = ham_x
        self._a_ham = ham_y
        self._a_smooth = yumusak_y
        self._a_adim = max(1, toplam // KARE)
        self._a_pos = 0

        # tepe noktaları:
        # - pozisyon sırası → hangi frame'de çıkacak (animasyon için)
        # - amplitude sırası → kart numarası (HEDEF 1 = en güçlü)
        tepeler_ham = self.motor.tepe_noktalarini_bul(ham_x, yumusak_y)
        if len(tepeler_ham) > 0:
            # pozisyona göre sırala (soldan sağa = 1'den n'e)
            self._a_poz_sirali = sorted(int(t) for t in tepeler_ham)
            # kart numarası = pozisyon sırası (1 = en solda)
            self._a_kart_no = {idx: no for no, idx in enumerate(self._a_poz_sirali, start=1)}
        else:
            self._a_kart_no = {}
            self._a_poz_sirali = []
        self._a_eklenenler = set()  # zaten kart olarak eklenmiş tepe indisleri

        # sahneyi hazırla
        self.radar_sahne.sahneli_temizle()
        self.radar_sahne.hedefleri_temizle()
        ax = self.radar_sahne.ax
        ax.clear()
        ax.set_facecolor('#000000')
        self.radar_sahne.fig.subplots_adjust(
            left=0.03, right=0.99, top=0.90, bottom=0.20
        )

        self.radar_sahne.fig.text(
            0.01, 0.96, "PLUTOSDR RADAR ANALİZ SİSTEMİ",
            color='white', fontsize=16, fontweight='bold'
        )
        ax.set_xlabel("FREKANS (MHz)", color='white', fontsize=12,
                       fontweight='bold', labelpad=15)
        ax.set_ylabel("GÜÇ (dBFS)", color='white', fontsize=12,
                       fontweight='bold', labelpad=10)

        ax.set_xlim(ham_x.min(), ham_x.max())
        ax.set_ylim(np.min(yumusak_y) - 5, np.max(yumusak_y) + 25)
        ax.set_xticks(np.arange(FREKANS_MIN, FREKANS_MAX, FREKANS_ADIM))
        ax.tick_params(axis='x', rotation=90)
        ax.tick_params(axis='both', colors=RENK['eksen_gri'], labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(RENK['cerceve_gri'])

        # eşik çizgisi
        esik = np.median(yumusak_y) + 12
        ax.axhline(y=esik, color=RENK['esik_renk'], linestyle='--', linewidth=1.2)

        # 3 boş çizgi nesnesi (set_data ile güncellenecek)
        self._ln_ham, = ax.plot([], [], color=RENK['grafik_ham'],
                                linewidth=0.5, alpha=0.9)
        self._ln_smooth, = ax.plot([], [], color=RENK['grafik_ana'],
                                   linewidth=1.0)

        # scroll'u kilitle (animasyon sırasında kullanıcı kaydıramaz)
        self.radar_sahne.scroll_kilitle()

        self.radar_sahne.canvas.draw()

        # 16ms = ~60fps
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._anim_tick)
        self._anim_timer.start(16)

    def _anim_tick(self):
        """Her frame'de çizgiyi uzat, tepeleri işaretle, kartları ekle, scroll'u kaydır."""
        toplam = len(self._a_x)
        self._a_pos += self._a_adim

        bitti = self._a_pos >= toplam
        if bitti:
            self._a_pos = toplam

        n = self._a_pos

        # çizgileri güncelle (sadece set_data — süper hafif)
        self._ln_ham.set_data(self._a_x[:n], self._a_ham[:n])
        self._ln_smooth.set_data(self._a_x[:n], self._a_smooth[:n])

        # geçilen tepe noktalarına kırmızı nokta + doğru numaralı kart ekle
        for idx in self._a_poz_sirali:
            if idx < n and idx not in self._a_eklenenler:
                self._a_eklenenler.add(idx)
                kart_no = self._a_kart_no[idx]
                self.radar_sahne.ax.plot(
                    self._a_x[idx], self._a_smooth[idx], "ro", markersize=4
                )
                self.radar_sahne.tek_kart_ekle(
                    kart_no, float(self._a_x[idx]), float(self._a_smooth[idx])
                )

        # otomatik scroll — çizimin ucunu takip et
        oran = n / toplam
        self.radar_sahne.scroll_pozisyon_ayarla(oran)

        self.radar_sahne.canvas.draw_idle()

        if bitti:
            self._anim_timer.stop()

            # fill efektini en sonda ekle (görsel tamamlama)
            self.radar_sahne.ax.fill_between(
                self._a_x, np.min(self._a_smooth) - 10,
                self._a_smooth, color=RENK['grafik_ana'], alpha=0.08
            )
            self.radar_sahne.canvas.draw()

            # scroll'u aç — artık kullanıcı kaydırabilir
            self.radar_sahne.scroll_ac()
            self.radar_sahne.scroll_pozisyon_ayarla(0.0)  # başa dön

    # ------------------------------------------------------------------
    #  Yardımcı fabrika metodları
    # ------------------------------------------------------------------
    @staticmethod
    def _etiket_olustur(metin, parent, renk, boyut, kalin=False, bosluk=0):
        """Tekrarlayan QLabel oluşturma kodunu sadeleştirir."""
        etiket = QLabel(metin, parent)
        kalinlik = "bold" if kalin else "normal"
        etiket.setStyleSheet(f"""
            color: {renk}; font-size: {boyut}px;
            font-weight: {kalinlik}; font-family: 'Courier New';
            letter-spacing: {bosluk}px;
        """)
        etiket.setAlignment(Qt.AlignCenter)
        return etiket

    @staticmethod
    def _kontrol_butonu_olustur(metin, genislik, renk, border_renk):
        """Radar ekranı kontrol butonları için fabrika metodu."""
        btn = QPushButton(metin)
        btn.setFixedSize(genislik, 36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {renk};
                border: 1px solid {border_renk}; border-radius: 5px;
                font-size: 13px; font-weight: bold; font-family: 'Courier New';
            }}
            QPushButton:hover {{
                background-color: {border_renk}; color: #000000;
            }}
        """)
        return btn


# =====================================================================
#  Uygulama başlangıcı
# =====================================================================
if __name__ == "__main__":
    uygulama = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(uygulama.exec_())