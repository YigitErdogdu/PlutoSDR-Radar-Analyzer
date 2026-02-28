"""
ana_uygulama.py - HUB-10 Radar Analiz Sistemi (TCP CANLI YAYIN - OPTİMİZE)
Ana pencere, giriş ekranı ve PlutoSDR C-Server üzerinden gerçek zamanlı radar sahne yönetimi.
"""
import os
import sys
import numpy as np
import matplotlib

# --- PLATFORM UYUMLULUK ---
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
PENCERE_BASLIGI = "HUB 10 - RADAR ANALİZ SİSTEMİ (CANLI YAYIN)"
PENCERE_BOYUT = (1280, 800)
ARKAPLAN_DOSYASI = "wp6047743.jpg"
KARARTMA_ALFA = 160

# Frekans Ekseni (Şartnameye Göre 100 MHz - 3000 MHz)
FREKANS_MIN = 100
FREKANS_MAX = 3000
FREKANS_ADIM = 100

# Renk paleti 
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle(PENCERE_BASLIGI)
        self.setGeometry(100, 100, *PENCERE_BOYUT)

        self.sahne_yoneticisi = QStackedWidget()
        self.setCentralWidget(self.sahne_yoneticisi)

        # YENİ: TCP üzerinden Pluto'ya bağlanan Sinyal Motoru
        self.motor = SinyalIslemeMotoru(ip_address="192.168.2.1", port=80)

        # Canlı Tarama Değişkenleri
        self.tarama_aktif = False
        self._x_canli = []
        self._y_canli = []
        self._eklenen_hedefler = set()
        
        # PERFORMANS İÇİN ÇİZİM SAYACI
        self._cizim_sayaci = 0
        
        # Hızlı okuma için Timer
        self._canli_timer = QTimer()
        self._canli_timer.timeout.connect(self._canli_tarama_adimi)

        self._giris_ekrani_kur()
        self._radar_ekrani_kur()

    # ------------------------------------------------------------------
    #  Giriş Ekranı
    # ------------------------------------------------------------------
    def _giris_ekrani_kur(self):
        self.giris_widget = QWidget()
        self.giris_widget.setStyleSheet(f"background-color: {RENK['zemin']};")

        self._arkaplan_ayarla()

        ust_logo = self._etiket_olustur("[ PLUTOSDR ]", self.giris_widget, renk=RENK['amber'], boyut=13, bosluk=6)
        baslik = self._etiket_olustur("HUB-10\nSİNYAL ANALİZ SİSTEMİ", self.giris_widget, renk=RENK['beyaz_yumusak'], boyut=42, kalin=True, bosluk=3)
        alt_baslik = self._etiket_olustur("TCP Server Destekli Gerçek Zamanlı RF Tarama", self.giris_widget, renk=RENK['yesil_soluk'], boyut=15, bosluk=1)

        self.btn_baslat = QPushButton("▶  SİSTEMİ BAŞLAT", self.giris_widget)
        self.btn_baslat.setFixedSize(300, 60)
        self.btn_baslat.setCursor(Qt.PointingHandCursor)
        self.btn_baslat.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: #d4d4d4;
                border: 2px solid {RENK['yesil_neon']}; border-radius: 6px;
                font-size: 17px; font-weight: bold; font-family: 'Courier New'; letter-spacing: 2px;
            }}
            QPushButton:hover {{ background-color: {RENK['yesil_neon']}; color: {RENK['zemin']}; border-color: {RENK['yesil_neon']}; }}
            QPushButton:pressed {{ background-color: {RENK['yesil_koyu']}; border-color: {RENK['yesil_koyu']}; color: {RENK['zemin']}; }}
        """)
        self.btn_baslat.clicked.connect(self._radar_sahnesine_gec)

        durum = self._etiket_olustur("• SİSTEM HAZIR  •  BAĞLANTI: TCP/80  •", self.giris_widget, renk=RENK['durum_yesil'], boyut=11, bosluk=2)

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
        self.giris_widget.resizeEvent = self._arkaplan_yeniden_boyutla

    def _arkaplan_ayarla(self):
        resim_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), ARKAPLAN_DOSYASI)
        self.lbl_arkaplan = QLabel(self.giris_widget)
        self.lbl_arkaplan.setGeometry(0, 0, *PENCERE_BOYUT)
        self.lbl_arkaplan.setScaledContents(True)

        if not os.path.exists(resim_yolu): return

        orijinal = QPixmap(resim_yolu)
        karanlik = QPixmap(orijinal.size())
        karanlik.fill(Qt.transparent)
        p = QPainter(karanlik)
        p.fillRect(karanlik.rect(), QColor(0, 0, 0, KARARTMA_ALFA))
        p.end()

        birlesik = QPixmap(orijinal.size())
        p2 = QPainter(birlesik)
        p2.drawPixmap(0, 0, orijinal)
        p2.drawPixmap(0, 0, karanlik)
        p2.end()

        self.lbl_arkaplan.setPixmap(birlesik)

    def _arkaplan_yeniden_boyutla(self, event):
        self.lbl_arkaplan.setGeometry(0, 0, event.size().width(), event.size().height())

    # ------------------------------------------------------------------
    #  Radar Ekranı
    # ------------------------------------------------------------------
    def _radar_ekrani_kur(self):
        self.radar_sahne = RadarSahnesi()

        kontrol_bandi = QWidget()
        kontrol_bandi.setStyleSheet("background-color: #000000;")
        band_layout = QHBoxLayout(kontrol_bandi)
        band_layout.setContentsMargins(0, 0, 0, 0)
        band_layout.setSpacing(10)

        self.btn_geri = self._kontrol_butonu_olustur("◀  GİRİŞ EKRANI", 200, "#ff3131", "#ff3131")
        self.btn_geri.clicked.connect(self._giris_ekranina_don)

        self.btn_duraklat = self._kontrol_butonu_olustur("🛑  TARAMAYI DURDUR", 220, "#eab308", "#eab308")
        self.btn_duraklat.clicked.connect(self._tarama_toggle)

        band_layout.addWidget(self.btn_geri)
        band_layout.addStretch()
        band_layout.addWidget(self.btn_duraklat)

        self.radar_sahne.layout.insertWidget(0, kontrol_bandi)
        self.sahne_yoneticisi.addWidget(self.radar_sahne)

    # ------------------------------------------------------------------
    #  Canlı Geçiş ve Tarama Mantığı
    # ------------------------------------------------------------------
    def _radar_sahnesine_gec(self):
        self.btn_baslat.setText("Pluto'ya Bağlanılıyor...")
        QApplication.processEvents()
        
        self.sahne_yoneticisi.setCurrentWidget(self.radar_sahne)
        self._canli_grafik_hazirla()
        
        self.motor.taramayi_baslat()
        self.tarama_aktif = True
        self.btn_duraklat.setText("🛑  TARAMAYI DURDUR")
        self._canli_timer.start(1) 

    def _giris_ekranina_don(self):
        self.tarama_aktif = False
        self._canli_timer.stop()
        self.motor.taramayi_durdur() 
        self.btn_baslat.setText("▶  SİSTEMİ BAŞLAT")
        self.sahne_yoneticisi.setCurrentWidget(self.giris_widget)

    def _tarama_toggle(self):
        if self.tarama_aktif:
            # Taramayı manuel olarak yarıda keserse
            self.tarama_aktif = False
            self.motor.taramayi_durdur()
            self.btn_duraklat.setText("🔄 YENİDEN TARA")
            self.btn_duraklat.setStyleSheet("color: #39ff14; border-color: #39ff14;")
        else:
            # --- YENİ EKLENEN KISIM: Her yeni taramada ekranı sıfırla ---
            self._canli_grafik_hazirla() 
            
            self.tarama_aktif = True
            self.motor.taramayi_baslat()
            self.btn_duraklat.setText("🛑  TARAMAYI DURDUR")
            self.btn_duraklat.setStyleSheet("color: #eab308; border-color: #eab308;")
            self._canli_timer.start(1)

    # ------------------------------------------------------------------
    #  Canlı Çizim Fonksiyonları
    # ------------------------------------------------------------------
    def _canli_grafik_hazirla(self):
        self.radar_sahne.sahneli_temizle()
        self.radar_sahne.hedefleri_temizle()
        self._x_canli.clear()
        self._y_canli.clear()
        self._eklenen_hedefler.clear()
        self._cizim_sayaci = 0

        ax = self.radar_sahne.ax
        self.radar_sahne.fig.subplots_adjust(left=0.03, right=0.99, top=0.90, bottom=0.20)

        self.radar_sahne.fig.text(0.01, 0.96, "PLUTOSDR CANLI RADAR (TCP SERVER)", color='white', fontsize=16, fontweight='bold')
        ax.set_xlabel("FREKANS (MHz)", color='white', fontsize=12, fontweight='bold', labelpad=15)
        ax.set_ylabel("GÜÇ (dBFS)", color='white', fontsize=12, fontweight='bold', labelpad=10)

        ax.set_xlim(FREKANS_MIN, FREKANS_MAX)
        
        # GERÇEK DÜNYA SİNYAL SEVİYELERİ (-120 ile 20 dBFS arası)
        ax.set_ylim(-120, 20) 
        
        ax.set_xticks(np.arange(FREKANS_MIN, FREKANS_MAX + 100, FREKANS_ADIM))
        ax.tick_params(axis='x', rotation=90)
        ax.tick_params(axis='both', colors=RENK['eksen_gri'], labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(RENK['cerceve_gri'])

        self._ln_canli, = ax.plot([], [], color=RENK['grafik_ana'], linewidth=1.2)
        self.radar_sahne.canvas.draw()

    def _canli_tarama_adimi(self):
        if not self.tarama_aktif: return

        # Soketten veriyi çek
        freq_hz, f_eksen, genlik_db = self.motor.siradaki_bandi_oku()

        if freq_hz == "TUR_SONU":
            # --- İŞTE TEK ATIM (ONE-SHOT) MANTIĞI BURASI ---
            self.tarama_aktif = False
            self._canli_timer.stop()         # Arayüz döngüsünü tamamen durdur
            self.motor.taramayi_durdur()     # Pluto C-Server'a "Dur" emri yolla
            
            self.btn_duraklat.setText("🔄 YENİDEN TARA")
            self.btn_duraklat.setStyleSheet("color: #39ff14; border-color: #39ff14;")
            
            # Taramadan elde edilen tüm veriyi son bir kez pürüzsüzce çiz ve dondur
            if len(self._x_canli) > 0:
                idx = np.argsort(self._x_canli)
                x_sirali = np.array(self._x_canli)[idx]
                y_sirali = np.array(self._y_canli)[idx]
                self._ln_canli.set_data(x_sirali, y_sirali)
                self.radar_sahne.canvas.draw_idle()
                
            return # Döngüden tamamen çık

        elif f_eksen is not None:
            f_mhz = f_eksen / 1e6
            self._x_canli.extend(f_mhz)
            self._y_canli.extend(genlik_db)
            self._cizim_sayaci += 1

            hedefler = self.motor.akilli_esik_tespit(f_eksen, genlik_db)
            for h in hedefler:
                hedef_f = h["frekans"]
                hedef_g = h["guc"]
                
                if not any(abs(hedef_f - e) < 1.0 for e in self._eklenen_hedefler):
                    self._eklenen_hedefler.add(hedef_f)
                    self.radar_sahne.ax.plot(hedef_f, hedef_g, "ro", markersize=5)
                    self.radar_sahne.tek_kart_ekle(len(self._eklenen_hedefler), hedef_f, hedef_g)

            # Zikzak önleyici canlı çizim (Her 5 bantta bir günceller)
            if self._cizim_sayaci % 5 == 0:
                idx = np.argsort(self._x_canli)
                x_sirali = np.array(self._x_canli)[idx]
                y_sirali = np.array(self._y_canli)[idx]
                self._ln_canli.set_data(x_sirali, y_sirali)
                self.radar_sahne.canvas.draw_idle()

    # ------------------------------------------------------------------
    #  Yardımcı Fabrika Metodları
    # ------------------------------------------------------------------
    @staticmethod
    def _etiket_olustur(metin, parent, renk, boyut, kalin=False, bosluk=0):
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
        btn = QPushButton(metin)
        btn.setFixedSize(genislik, 36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {renk};
                border: 1px solid {border_renk}; border-radius: 5px;
                font-size: 13px; font-weight: bold; font-family: 'Courier New';
            }}
            QPushButton:hover {{ background-color: {border_renk}; color: #000000; }}
        """)
        return btn


if __name__ == "__main__":
    uygulama = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(uygulama.exec_())