# TCM Türkiye İçerik Otomasyonu

Bu proje, TCM Türkiye web sitesi için otomatik içerik toplama ve HTML sayfası oluşturma sistemini içerir. Sistem, çeşitli kaynaklardan Geleneksel Çin Tıbbı (TCM) ve akupunktur ile ilgili en güncel içerikleri toplayarak görsel olarak zengin HTML sayfaları oluşturur.

## İçerik Kategorileri

Sistem aşağıdaki kategorilerde içerik toplar:

1. **Araştırmalar** - J-STAGE ve CiNii gibi akademik kaynaklardan araştırma makaleleri
2. **Teoriler** - WHO ve NCCIH gibi kaynaklardan TCM teorileri
3. **Mekanizmalar** - TCM'nin etki mekanizmaları hakkında bilgiler
4. **Klinik Vakalar** - PubMed Central ve Journal of Chinese Medicine'dan klinik vaka raporları
5. **Etkinlikler** - TCM ile ilgili konferanslar, seminerler ve diğer etkinlikler
6. **Eğitimler** - TCM ve akupunktur eğitim programları

## Sistem Bileşenleri

- **Scraper Modülleri** - Farklı kaynaklardan içerik çekmek için özel modüller
- **İçerik Yöneticisi** - Tüm scraperları koordine eden ve içerikleri düzenleyen modül
- **HTML Oluşturucu** - Toplanan içeriklerden görsel olarak zengin HTML sayfaları oluşturan modül
- **Firebase Kimlik Doğrulama** - Kullanıcıların Google hesaplarıyla giriş yapabilmesini sağlayan sistem
- **Zamanlayıcı** - İçerik toplama ve HTML oluşturma işlemlerini belirli aralıklarla otomatik olarak çalıştıran modül

## Kullanım

### Kurulum

Gerekli bağımlılıkları yüklemek için:

```bash
pip install -r requirements.txt
```

### Manuel Çalıştırma

Tüm içerikleri toplamak ve HTML sayfalarını oluşturmak için:

```bash
python main.py
```

### Zamanlayıcı ile Çalıştırma

Zamanlayıcıyı başlatmak için:

```bash
python main.py --schedule
```

Bu, varsayılan olarak her gün sabah 08:00'de içerik toplama ve HTML oluşturma işlemlerini otomatik olarak çalıştırır.

Çalışma saatini değiştirmek için:

```bash
python main.py --schedule --time "16:30"
```

## HTML Sayfaları

Sistem, toplanan içeriklerden aşağıdaki HTML sayfalarını oluşturur:

1. **Ana Sayfa** - Tüm kategorilerin özetini ve en son eklenen içerikleri gösteren sayfa
2. **Kategori Sayfaları** - Her kategori için içerik listesi ve filtreleme seçenekleri sunan sayfalar
3. **Detay Sayfaları** - Her içerik öğesi için ayrıntılı bilgi içeren sayfalar

Oluşturulan HTML sayfaları `tcm_content/html` dizininde saklanır ve doğrudan bir web sunucusunda yayınlanabilir.

## Firebase Kimlik Doğrulama

Sistem, kullanıcıların Google hesaplarıyla giriş yapabilmesini sağlayan Firebase Authentication entegrasyonunu içerir. Bu özellik sayesinde:

- Kullanıcılar Google hesaplarıyla kolaylıkla giriş yapabilir
- Giriş yapan kullanıcıların profil bilgileri görüntülenebilir
- Dropdown menü aracılığıyla kullanıcı işlemleri yönetilebilir

## Dizin Yapısı

```
tcm_content/
├── json/         # JSON formatında içerik dosyaları
├── html/         # Oluşturulan HTML sayfaları
│   ├── index.html  # Ana sayfa
│   ├── research/   # Araştırma sayfaları
│   ├── theory/     # Teori sayfaları
│   ├── mechanism/  # Mekanizma sayfaları
│   ├── clinical/   # Klinik vaka sayfaları
│   ├── event/      # Etkinlik sayfaları
│   └── education/  # Eğitim sayfaları
└── static/       # CSS, JavaScript ve görsel dosyaları
```
- Her Çarşamba ve Cumartesi 05:00'de teori ve mekanizma içerikleri
- Her Salı ve Cuma 06:00'da klinik vaka içerikleri
- Her Perşembe ve Pazar 07:00'de etkinlik ve eğitim içerikleri

### GitHub Actions ile Çalıştırma

GitHub Actions, `.github/workflows/content_scraper.yml` dosyasındaki yapılandırmaya göre içerik toplama işlemlerini otomatik olarak çalıştırır. Varsayılan olarak, her gün 03:00 UTC'de (Türkiye saati ile 06:00) tüm içerikler toplanır.

Ayrıca, GitHub web arayüzünden manuel olarak da çalıştırılabilir.

## Geliştirme

### Yeni Scraper Ekleme

Yeni bir scraper eklemek için:

1. `tcmturkiye/scrapers/` dizininde yeni bir Python dosyası oluşturun
2. Scraper sınıfını veya fonksiyonlarını tanımlayın
3. `tcmturkiye/content_manager.py` dosyasında yeni scraper'ı içe aktarın ve ilgili fonksiyonu ekleyin
4. `tcmturkiye/main.py` dosyasında yeni scraper türünü ekleyin

### Bağımlılıklar

Gerekli Python paketlerini yüklemek için:

```bash
pip install -r requirements.txt
```

## Lisans

Bu proje, ACUSNAP tarafından geliştirilmiştir ve tüm hakları saklıdır.

## İletişim

Sorularınız veya önerileriniz için: [info@acusnap.com](mailto:info@acusnap.com)
