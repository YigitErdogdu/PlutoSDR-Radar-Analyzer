"""
arayuz_elemanlari.py - Özel Arayüz Bileşenleri
Hedef kartı, sinyal tipinden renklere kadar ortak UI elemanları burada tanımlanır.
"""
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


# sinyal bantlarına göre tip sınıflandırma tablosu
# (alt sınır, üst sınır, açıklama)
SINYAL_BANTLARI = [
    (433.0,  434.79, "ISM / LPD Kumanda"),
    (446.0,  446.2,  "PMR (El Telsizi)"),
    (868.0,  870.0,  "LoRa / Telemetri"),
    (915.0,  928.0,  "ISM / Drone Telemetri"),
    (2400.0, 2483.5, "Drone / Wi-Fi / BT"),
    (5725.0, 5875.0, "Drone Video Link"),
]


class HedefKarti(QFrame):
    """
    Tespit edilen her sinyal hedefi için bilgi kartı.
    Frekans, güç seviyesi ve tahmini sinyal tipi gösterir.
    """
    
    KART_GENISLIK = 180
    KART_YUKSEKLIK = 130

    STIL = """
        QFrame {
            background-color: rgba(10, 14, 20, 220);
            border: 1px solid #39ff14;
            border-radius: 8px;
        }
        QLabel {
            color: #b0b0b0; font-size: 11px;
            border: none; font-weight: bold;
        }
        QLabel#Baslik {
            color: #eab308; font-size: 14px;
            font-weight: bold; margin-bottom: 5px;
        }
        QLabel#Deger {
            color: #e0e0e0; font-size: 12px;
        }
    """

    def __init__(self, hedef_no: int, frekans: float, guc: float, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.KART_GENISLIK, self.KART_YUKSEKLIK)
        self.setStyleSheet(self.STIL)

        ana_layout = QVBoxLayout(self)
        ana_layout.setSpacing(4)

        sinyal_tipi = self._sinyal_tipi_belirle(frekans)

        # başlık
        baslik = QLabel(f"🎯 HEDEF {hedef_no}", objectName="Baslik")
        baslik.setAlignment(Qt.AlignCenter)
        ana_layout.addWidget(baslik)

        # detay satırları
        bilgiler = [
            f"• Frekans: {frekans:.2f} MHz",
            f"• Güç: {guc:.1f} dBFS",
            f"• Tip: {sinyal_tipi}",
            "• Bant Genişliği: Pasif",
        ]
        for satir in bilgiler:
            etiket = QLabel(satir, objectName="Deger")
            ana_layout.addWidget(etiket)

    @staticmethod
    def _sinyal_tipi_belirle(frekans_mhz: float) -> str:
        """Frekansa göre olası sinyal kaynağını tahmin eder."""
        for alt, ust, aciklama in SINYAL_BANTLARI:
            if alt <= frekans_mhz <= ust:
                return aciklama
        return "Bilinmeyen Sinyal"