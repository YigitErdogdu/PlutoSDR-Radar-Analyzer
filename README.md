# PlutoSDR Radar Analiz Sistemi (HUB 10)

Bu çalışma, PlutoSDR donanımı aracılığıyla elde edilen spektrum verilerinin gerçek zamanlı görselleştirilmesi ve analizi için geliştirilmiş bir arayüz uygulamasıdır. Balıkesir Üniversitesi Bilgisayar Mühendisliği bölümü bünyesindeki eğitim faaliyetleri kapsamında hazırlanmıştır.

## Geliştirme Metodolojisi ve Yapay Zeka İş Birliği

Projenin geliştirme sürecinde modern yazılım mühendisliği yaklaşımları ve yapay zeka destekli kodlama tekniklerinden (Claude ve Gemini) birer asistan olarak yararlanılmıştır:

* **Sistem Mimarisi:** Uygulamanın temel iskeleti, giriş sayfası tasarımı ve arayüzdeki fonksiyonel bileşenlerin yerleşimi Claude (Anthropic) asistanlığı ile yapılandırılmıştır.
* **Görselleştirme ve Grafik Optimizasyonu:** Spektrum verilerinin grafik üzerine işlenmesi, arayüzün estetik düzenlemeleri ve sinyal işleme algoritmalarının optimizasyonu Gemini (Google) asistanlığı ile gerçekleştirilmiştir.
* **Sistem Entegrasyonu:** Proje sahibi Yiğit Erdoğdu, tüm bu çıktıları birleştirmiş, donanım uyumluluğunu sağlamış ve sistemin son halini yönetmiştir.

## Gelecek Planları ve Geliştirme Süreci

Bu proje, dinamik ve geliştirmeye açık bir sistem mimarisi üzerine inşa edilmiştir. TEKNOFEST ve benzeri mühendislik yarışmaları için hedeflenen nihai sistem kapsamında aşağıdaki modüller üzerinde geliştirme çalışmaları devam etmektedir:

* **İleri Sinyal Analizi:** Welch Metodu ve Güç Spektral Yoğunluğu (PSD) kestirimi entegrasyonu.
* **Akıllı Enerji Tespiti:** Dinamik eşik değerleri (CFAR) ile sinyal ayrıştırma algoritmaları.
* **Donanım Genişletme:** Farklı SDR donanımları ile uyumluluk ve çoklu anten desteği.

## Teknik Gereksinimler

Sistemin çalışması için aşağıdaki Python kütüphanelerinin kurulu olması gerekmektedir:
* PyQt5
* Matplotlib
* NumPy
* SciPy

## Telif Hakkı ve Lisans

Copyright (c) 2026 Yiğit Erdoğdu. Tüm Hakları Saklıdır. Detaylı bilgi için LICENSE dosyasına bakınız.
