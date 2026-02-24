# PlutoSDR Radar Analiz Sistemi (HUB 10)

Bu çalışma, PlutoSDR donanımı aracılığıyla elde edilen spektrum verilerinin gerçek zamanlı görselleştirilmesi ve analizi için geliştirilmiş bir arayüz uygulamasıdır. Balıkesir Üniversitesi Bilgisayar Mühendisliği bölümü bünyesindeki eğitim faaliyetleri kapsamında hazırlanmıştır.

## Geliştirme Metodolojisi ve Yapay Zeka İş Birliği

Projenin geliştirme sürecinde modern yazılım mühendisliği yaklaşımları ve yapay zeka destekli kodlama tekniklerinden yararlanılmıştır:

* **Sistem Mimarisi ve Mantıksal Kurgu:** Uygulamanın temel iskeleti, giriş sayfası tasarımı ve arayüzdeki fonksiyonel bileşenlerin yerleşimi Claude (Anthropic) asistanlığı ile yapılandırılmıştır.
* **Görselleştirme ve Grafik Optimizasyonu:** Spektrum verilerinin grafik üzerine işlenmesi, arayüzün estetik düzenlemeleri, veri yerleşimi ve sinyal işleme algoritmalarının optimizasyonu Gemini (Google) asistanlığı ile gerçekleştirilmiştir.
* **Sistem Entegrasyonu:** Proje sahibi Yiğit Erdoğdu, bir "AI Orchestrator" rolüyle farklı modellerden gelen çıktıları birleştirmiş, donanım uyumluluğunu sağlamış ve sistemin son halini yönetmiştir.

## Teknik Özellikler

* **Gerçek Zamanlı Spektrum Analizi:** PlutoSDR üzerinden gelen verilerin anlık ve akıcı bir şekilde görselleştirilmesi.
* **Optimize Edilmiş Grafik Arayüzü:** Analiz ekranının üst ve alt bölgelerinde sağlanan dengeli yerleşim ile tam boyutlu veri takibi.
* **Otomatik Sinyal Tespiti:** Spektrum üzerindeki pik noktalarının algoritma aracılığıyla tespit edilmesi ve görsel olarak işaretlenmesi.
* **Modüler Arayüz Tasarımı:** PyQt5 kütüphanesi kullanılarak oluşturulmuş profesyonel karanlık mod tasarımı.

## Teknik Gereksinimler

Sistemin çalışması için aşağıdaki Python kütüphanelerinin kurulu olması gerekmektedir:
* PyQt5
* Matplotlib
* NumPy
* SciPy

## Çalıştırma Talimatları

Proje dosyalarının bulunduğu dizin içerisinde aşağıdaki komutu çalıştırarak uygulamayı başlatabilirsiniz:

```bash
python ana_uygulama.py
