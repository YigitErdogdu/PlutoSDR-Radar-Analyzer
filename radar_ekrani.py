"""
radar_ekrani.py - Radar Analiz Ekranı
Matplotlib grafik paneli ve hedef kartı listesini barındıran ana sahne widget'ı
"""
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from arayuz_elemanlari import HedefKarti


class RadarSahnesi(QWidget):
    """
    Üst kısımda yatay kaydırılabilir spektrum grafiği,
    alt kısımda tespit edilen hedef kartlarını gösteren panel.
    """

    GRAFIK_GENISLIK = 6000
    GRAFIK_FIGSIZE = (40, 5)
    HEDEF_PANEL_YUKSEKLIK = 170
    ARKAPLAN_RENK = "#000000"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {self.ARKAPLAN_RENK};")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # scrollbar stilleri ortak kullanılacağı için burada tanımlanıyor
        stil_kaydirma = self._scrollbar_stili_olustur()

        # üst bölüm: grafik paneli
        self._grafik_paneli_kur(stil_kaydirma)

        # alt bölüm: hedef kartları
        self._hedef_paneli_kur(stil_kaydirma)

    # ------------------------------------------------------------------
    #  Panel kurulum metodları
    # ------------------------------------------------------------------
    def _grafik_paneli_kur(self, stil: str):
        """Matplotlib canvas'ını scroll area içinde oluşturur."""
        self.ust_panel = QScrollArea()
        self.ust_panel.setWidgetResizable(True)
        self.ust_panel.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ust_panel.setStyleSheet(stil)

        grafik_konteyner = QWidget()
        grafik_konteyner.setStyleSheet(f"background-color: {self.ARKAPLAN_RENK};")
        self.grafik_layout = QVBoxLayout(grafik_konteyner)

        # matplotlib figure
        self.fig = Figure(figsize=self.GRAFIK_FIGSIZE, facecolor=self.ARKAPLAN_RENK)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.ARKAPLAN_RENK)

        self.canvas.setFixedWidth(self.GRAFIK_GENISLIK)
        self.grafik_layout.addWidget(self.canvas)
        self.ust_panel.setWidget(grafik_konteyner)

        self.layout.addWidget(self.ust_panel, stretch=1)

    def _hedef_paneli_kur(self, stil: str):
        """Alt kısımdaki yatay hedef kartı listesini hazırlar."""
        self.alt_scroll = QScrollArea()
        self.alt_scroll.setWidgetResizable(True)
        self.alt_scroll.setStyleSheet(stil)
        self.alt_scroll.setFixedHeight(self.HEDEF_PANEL_YUKSEKLIK)

        self._hedef_konteyner = QWidget()
        self.alt_layout = QHBoxLayout(self._hedef_konteyner)
        self.alt_layout.setSpacing(20)
        self.alt_layout.setAlignment(Qt.AlignLeft)

        self.alt_scroll.setWidget(self._hedef_konteyner)
        self.layout.addWidget(self.alt_scroll)

    # ------------------------------------------------------------------
    #  Sahne güncellemesi
    # ------------------------------------------------------------------
    def sahneli_temizle(self):
        """Grafik eksenini sıfırlar."""
        self.ax.clear()
        self.ax.set_facecolor(self.ARKAPLAN_RENK)

    def hedefleri_listele(self, frekanslar, gucler):
        """
        Alt paneldeki mevcut kartları temizleyip yeni
        hedef kartlarını sırayla ekler.
        """
        self.hedefleri_temizle()
        for sira, (f, g) in enumerate(zip(frekanslar, gucler), start=1):
            kart = HedefKarti(hedef_no=sira, frekans=f, guc=g)
            self.alt_layout.addWidget(kart)

    def hedefleri_temizle(self):
        """Alt paneldeki tüm hedef kartlarını kaldırır."""
        for i in reversed(range(self.alt_layout.count())):
            eski = self.alt_layout.itemAt(i).widget()
            if eski is not None:
                eski.setParent(None)
                eski.deleteLater()

    def tek_kart_ekle(self, sira: int, frekans: float, guc: float):
        """Alt panele tek bir hedef kartı ekler ve scroll'u sona kaydırır."""
        from PyQt5.QtCore import QTimer as _QT
        kart = HedefKarti(hedef_no=sira, frekans=frekans, guc=guc)
        self.alt_layout.addWidget(kart)
        # Layout yerleşince (bir sonraki event loop turunda) scroll'u sona at
        _QT.singleShot(0, lambda: self.alt_scroll.horizontalScrollBar().setValue(
            self.alt_scroll.horizontalScrollBar().maximum()
        ))

    def scroll_kilitle(self):
        """Animasyon sırasında kullanıcı kaydırmasını engeller."""
        self.ust_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def scroll_ac(self):
        """Animasyon bittikten sonra kullanıcı kaydırmasını açar."""
        self.ust_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def scroll_pozisyon_ayarla(self, oran: float):
        """Yatay scroll'u 0.0-1.0 arasında bir orana göre ayarlar."""
        sb = self.ust_panel.horizontalScrollBar()
        sb.setValue(int(oran * sb.maximum()))

    # ------------------------------------------------------------------
    #  Scrollbar stillerini üreten yardımcı
    # ------------------------------------------------------------------
    @staticmethod
    def _scrollbar_stili_olustur() -> str:
        """Özelleştirilmiş kırmızı-amber scrollbar CSS'ini döndürür."""
        return """
            QScrollArea {
                border: 1px solid #1a1a2e;
                background-color: #000000;
                border-radius: 8px;
            }

            /* --- YATAY SCROLLBAR --- */
            QScrollBar:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:0.5 #111111, stop:1 #0a0a0a);
                height: 14px;
                margin: 0px 14px 0px 14px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5e1a1a, stop:0.5 #ff3131, stop:1 #5e1a1a);
                min-width: 60px;
                border-radius: 5px;
                border: 1px solid rgba(255, 49, 49, 0.3);
            }
            QScrollBar::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #cc2929, stop:0.5 #ff4444, stop:1 #cc2929);
                border: 1px solid rgba(255, 49, 49, 0.7);
            }
            QScrollBar::sub-line:horizontal {
                background: #2a2000;
                width: 14px;
                subcontrol-position: left;
                subcontrol-origin: margin;
                border-radius: 3px;
                border: 1px solid #eab308;
            }
            QScrollBar::sub-line:horizontal:hover { background: #eab308; border-color: #eab308; }
            QScrollBar::add-line:horizontal {
                background: #2a2000;
                width: 14px;
                subcontrol-position: right;
                subcontrol-origin: margin;
                border-radius: 3px;
                border: 1px solid #eab308;
            }
            QScrollBar::add-line:horizontal:hover { background: #eab308; border-color: #eab308; }
            QScrollBar::left-arrow:horizontal  { width: 6px; height: 6px; }
            QScrollBar::right-arrow:horizontal { width: 6px; height: 6px; }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

            /* --- DİKEY SCROLLBAR --- */
            QScrollBar:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0a0a0a, stop:0.5 #111111, stop:1 #0a0a0a);
                width: 14px;
                margin: 14px 0px 14px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5e1a1a, stop:0.5 #ff3131, stop:1 #5e1a1a);
                min-height: 40px;
                border-radius: 5px;
                border: 1px solid rgba(255, 49, 49, 0.3);
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cc2929, stop:0.5 #ff4444, stop:1 #cc2929);
                border: 1px solid rgba(255, 49, 49, 0.7);
            }
            QScrollBar::sub-line:vertical {
                background: #2a2000;
                height: 14px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                border-radius: 3px;
                border: 1px solid #eab308;
            }
            QScrollBar::sub-line:vertical:hover { background: #eab308; border-color: #eab308; }
            QScrollBar::add-line:vertical {
                background: #2a2000;
                height: 14px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border-radius: 3px;
                border: 1px solid #eab308;
            }
            QScrollBar::add-line:vertical:hover { background: #eab308; border-color: #eab308; }
            QScrollBar::up-arrow:vertical   { width: 6px; height: 6px; }
            QScrollBar::down-arrow:vertical { width: 6px; height: 6px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """