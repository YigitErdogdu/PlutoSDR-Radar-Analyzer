****PlutoSDR Radar Analiz Sistemi (HUB 10)****
Bu proje, PlutoSDR cihazından alınan spektrum verilerini görselleştirmek için geliştirilmiş bir Radar Analiz Arayüzüdür. Projenin en büyük özelliği, bir Bilgisayar Mühendisliği öğrencisi olarak tamamen yapay zeka asistanları (Claude & Gemini) ile kolaboratif bir şekilde geliştirilmiş olmasıdır.

****Yapay Zeka İş Bölümü (Development Workflow)
Bu uygulama, farklı yapay zeka modellerinin güçlü yanları birleştirilerek inşa edilmiştir:

Claude: Uygulamanın ana iskeletini, giriş sayfasını (Landing Page), butonların mantıksal kurgusunu ve arayüzdeki ikon yerleşimlerini oluşturmuştur.
Gemini (Google): Ham sinyal verisinin grafiğe dökülmesi, grafik ekranının tasarımı, "makyaj" denilen görsel iyileştirmeler (hizalamalar, renkler, boşluklar) ve tepe noktası bulma algoritmasının optimizasyonunu gerçekleştirmiştir.
Yiğit Erdoğdu: Bir "AI Orchestrator" olarak tüm bu parçaları birleştirmiş, sistemin akışını yönetmiş ve donanım uyumluluğunu denetlemiştir.

****Mevcut Özellikler
Gerçek Zamanlı Spektrum Grafiği: PlutoSDR verilerini akıcı bir şekilde ekrana yansıtır.
Gelişmiş Grafik Yerleşimi: Ekranın üst ve alt kısmından optimize edilmiş boşluklarla tam boyutlu analiz imkanı sunar.
Otomatik Peak (Tepe) Tespiti: Grafik üzerindeki en güçlü sinyalleri kırmızı noktalarla işaretler ve listeler.
Modern Karanlık Mod UI: PyQt5 kullanılarak tasarlanmış, göz yormayan profesyonel tasarım.

****Gereksinimler
Sistemi çalıştırmak için aşağıdaki Python kütüphaneleri gereklidir:

PyQt5

Matplotlib

NumPy

SciPy

****Çalıştırma
Projeyi klonladıktan sonra ana klasör içinde şu komutu çalıştırın:
python ana_uygulama.py
