"""
TCM İçerik Yöneticisi

Bu modül, tüm scraper modüllerini bir araya getirir ve düzenli olarak içerik toplar.
Toplanan içerikler, web sitesinde kullanılmak üzere JSON formatında kaydedilir ve
HTML sayfaları olarak oluşturulur.
"""

import os
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Scraper modüllerini içe aktar
from tcmturkiye.scrapers.jstage_scraper import search_jstage, save_jstage_articles
from tcmturkiye.scrapers.cinii_scraper import search_cinii, save_cinii_articles
from tcmturkiye.scrapers.tcm_theory_scraper import scrape_all_tcm_theories, save_tcm_theories
from tcmturkiye.scrapers.clinical_case_scraper import scrape_all_clinical_cases, save_clinical_cases
from tcmturkiye.scrapers.events_education_scraper import (
    scrape_all_events_and_education, 
    save_events_and_education
)

# HTML oluşturucu modülünü içe aktar
from tcmturkiye.html_generator import generate_html_pages, copy_static_files

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='content_manager.log',
    filemode='a'
)

# Konsola da log yazdırmak için
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Sabit değişkenler
OUTPUT_DIR = "tcm_content"
JSON_DIR = os.path.join(OUTPUT_DIR, "json")
CONTENT_CATEGORIES = {
    "research": {
        "name": "Araştırmalar",
        "file": "research_content.json",
        "color": "#4285F4"
    },
    "theory": {
        "name": "Teoriler",
        "file": "theory_content.json",
        "color": "#EA4335"
    },
    "mechanism": {
        "name": "Mekanizmalar",
        "file": "mechanism_content.json",
        "color": "#FBBC05"
    },
    "clinical_case": {
        "name": "Klinik Vaka",
        "file": "clinical_case_content.json",
        "color": "#34A853"
    },
    "event": {
        "name": "Etkinlikler",
        "file": "event_content.json",
        "color": "#FF6D01"
    },
    "education": {
        "name": "Eğitimler",
        "file": "education_content.json",
        "color": "#46BDC6"
    }
}


def ensure_output_directory() -> None:
    """Çıktı dizinlerinin var olduğundan emin olur"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    logging.info(f"Çıktı dizinleri kontrol edildi: {OUTPUT_DIR}, {JSON_DIR}")


def collect_research_content() -> None:
    """Araştırma içeriklerini toplar - her kaynaktan en güncel 1 makale"""
    logging.info("Araştırma içerikleri toplanıyor...")
    
    try:
        # J-STAGE'den en güncel 1 araştırma makalesi
        jstage_articles = search_jstage(
            query="acupuncture OR traditional chinese medicine", 
            max_results=1
        )
        save_jstage_articles(jstage_articles, os.path.join(JSON_DIR, "jstage_articles.json"))
        
        # CiNii'den en güncel 1 araştırma makalesi
        cinii_articles = search_cinii(
            query="acupuncture OR traditional chinese medicine", 
            max_results=1
        )
        save_cinii_articles(cinii_articles, os.path.join(JSON_DIR, "cinii_articles.json"))
        
        # Araştırma içeriklerini birleştir
        combined_research = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "J-STAGE, CiNii",
            "articles": jstage_articles + cinii_articles
        }
        
        # Tarihe göre sırala (en yeni en üstte)
        combined_research["articles"].sort(
            key=lambda x: datetime.strptime(x.get("publication_date", "2000-01-01"), "%Y-%m-%d") 
            if x.get("publication_date") else datetime(2000, 1, 1),
            reverse=True
        )
        
        with open(os.path.join(JSON_DIR, "research_content.json"), 'w', encoding='utf-8') as f:
            json.dump(combined_research, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Toplam {len(jstage_articles) + len(cinii_articles)} araştırma makalesi toplandı.")
    
    except Exception as e:
        logging.error(f"Araştırma içerikleri toplanırken hata: {str(e)}")


def collect_theory_mechanism_content() -> None:
    """Teori ve mekanizma içeriklerini toplar - her kaynaktan en güncel 1 teori/mekanizma"""
    logging.info("Teori ve mekanizma içerikleri toplanıyor...")
    
    try:
        # Teori ve mekanizmaları çek (teoriler için tüm klasik teorileri alıyoruz)
        theories, mechanisms = scrape_all_tcm_theories()
        
        # Mekanizmalar için sadece en güncel olanı al
        if mechanisms:
            mechanisms = [mechanisms[0]]  # En güncel mekanizma
        
        # Kaydet
        save_tcm_theories(theories, os.path.join(JSON_DIR, "tcm_theories.json"))
        save_tcm_theories(mechanisms, os.path.join(JSON_DIR, "tcm_mechanisms.json"))
        
        # Teori içeriklerini birleştir
        combined_theories = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "WHO, NCCIH",
            "theories": [theory.to_dict() for theory in theories]
        }
        
        with open(os.path.join(JSON_DIR, "theory_content.json"), 'w', encoding='utf-8') as f:
            json.dump(combined_theories, f, ensure_ascii=False, indent=2)
        
        # Mekanizma içeriklerini birleştir
        combined_mechanisms = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "WHO, NCCIH",
            "mechanisms": [mechanism.to_dict() for mechanism in mechanisms]
        }
        
        with open(os.path.join(JSON_DIR, "mechanism_content.json"), 'w', encoding='utf-8') as f:
            json.dump(combined_mechanisms, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Toplam {len(theories)} teori ve {len(mechanisms)} mekanizma toplandı.")
    
    except Exception as e:
        logging.error(f"Teori ve mekanizma içerikleri toplanırken hata: {str(e)}")


def collect_clinical_case_content() -> None:
    """Klinik vaka içeriklerini toplar - her kaynaktan en güncel 1 vaka"""
    logging.info("Klinik vaka içerikleri toplanıyor...")
    
    try:
        # Klinik vakaları çek
        cases = scrape_all_clinical_cases()
        
        # En güncel 1 vakayı al
        if cases:
            # Tarihe göre sırala
            cases.sort(
                key=lambda x: datetime.strptime(x.publication_date, "%Y-%m-%d") 
                if hasattr(x, "publication_date") and x.publication_date else datetime(2000, 1, 1),
                reverse=True
            )
            cases = [cases[0]]  # En güncel vaka
        
        # Kaydet
        save_clinical_cases(cases, os.path.join(JSON_DIR, "clinical_cases.json"))
        
        # Klinik vaka içeriklerini birleştir
        combined_cases = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "PubMed Central, Journal of Chinese Medicine",
            "cases": [case.to_dict() for case in cases]
        }
        
        with open(os.path.join(JSON_DIR, "clinical_case_content.json"), 'w', encoding='utf-8') as f:
            json.dump(combined_cases, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Toplam {len(cases)} klinik vaka toplandı.")
    
    except Exception as e:
        logging.error(f"Klinik vaka içerikleri toplanırken hata: {str(e)}")


def collect_event_education_content() -> None:
    """Etkinlik ve eğitim içeriklerini toplar - her kaynaktan en güncel 1 etkinlik/eğitim"""
    logging.info("Etkinlik ve eğitim içerikleri toplanıyor...")
    
    try:
        # Etkinlik ve eğitimleri çek
        events, education = scrape_all_events_and_education()
        
        # En güncel 1 etkinlik ve 1 eğitim programını al
        if events:
            # Tarihe göre sırala (gelecek tarihli etkinlikler öncelikli)
            events.sort(
                key=lambda x: datetime.strptime(x.start_date, "%Y-%m-%d") 
                if hasattr(x, "start_date") and x.start_date else datetime(2000, 1, 1)
            )
            # Bugünden sonraki etkinlikleri filtrele
            future_events = [e for e in events if hasattr(e, "start_date") and 
                             e.start_date and 
                             datetime.strptime(e.start_date, "%Y-%m-%d") >= datetime.now()]
            
            if future_events:
                events = [future_events[0]]  # En yakın gelecek etkinlik
            else:
                events = [events[0]]  # En güncel etkinlik
        
        if education:
            education = [education[0]]  # En güncel eğitim programı
        
        # Kaydet
        save_events_and_education(
            events, 
            education,
            os.path.join(JSON_DIR, "tcm_events.json"),
            os.path.join(JSON_DIR, "tcm_education.json")
        )
        
        # Etkinlik içeriklerini birleştir
        combined_events = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "TCM World Foundation, ICCMR",
            "events": [event.to_dict() for event in events]
        }
        
        with open(os.path.join(JSON_DIR, "event_content.json"), 'w', encoding='utf-8') as f:
            json.dump(combined_events, f, ensure_ascii=False, indent=2)
        
        # Eğitim içeriklerini birleştir
        combined_education = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "ABORM",
            "education": [program.to_dict() for program in education]
        }
        
        with open(os.path.join(JSON_DIR, "education_content.json"), 'w', encoding='utf-8') as f:
            json.dump(combined_education, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Toplam {len(events)} etkinlik ve {len(education)} eğitim programı toplandı.")
    
    except Exception as e:
        logging.error(f"Etkinlik ve eğitim içerikleri toplanırken hata: {str(e)}")


def create_index_file() -> None:
    """İçerik indeks dosyasını oluşturur"""
    logging.info("İçerik indeks dosyası oluşturuluyor...")
    
    try:
        # İndeks dosyası için veri yapısı
        index_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "categories": CONTENT_CATEGORIES
        }
        
        # İndeks dosyasını kaydet
        with open(os.path.join(JSON_DIR, "content_index.json"), 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        logging.info("İçerik indeks dosyası oluşturuldu.")
    
    except Exception as e:
        logging.error(f"İçerik indeks dosyası oluşturulurken hata: {str(e)}")


def generate_html_pages() -> None:
    """JSON içeriklerinden HTML sayfaları oluşturur"""
    logging.info("HTML sayfaları oluşturuluyor...")
    
    try:
        # HTML Generator modülünü içe aktar
        from tcmturkiye.html_generator import HTMLGenerator
        
        # HTML Generator'u başlat
        generator = HTMLGenerator()
        
        # Tüm HTML sayfalarını oluştur
        generator.generate_all_pages()
        
        logging.info("HTML sayfaları başarıyla oluşturuldu.")
    
    except Exception as e:
        logging.error(f"HTML sayfaları oluşturulurken hata: {str(e)}")


def copy_static_files() -> None:
    """Statik dosyaları (CSS, JS, görseller) HTML dizinine kopyalar"""
    logging.info("Statik dosyalar kopyalanıyor...")
    
    try:
        import shutil
        from pathlib import Path
        
        # Kaynak ve hedef dizinleri
        templates_dir = Path(__file__).parent / "templates"
        static_src = templates_dir / "static"
        html_dir = Path(JSON_DIR).parent / "html"
        static_dest = html_dir / "static"
        
        # Hedef dizin varsa sil
        if static_dest.exists():
            shutil.rmtree(static_dest)
        
        # Statik dosyaları kopyala
        shutil.copytree(static_src, static_dest)
        
        logging.info("Statik dosyalar başarıyla kopyalandı.")
    
    except Exception as e:
        logging.error(f"Statik dosyalar kopyalanırken hata: {str(e)}")


def collect_all_content() -> None:
    """Tüm içerik türlerini toplar ve HTML sayfaları oluşturur"""
    logging.info("Tüm içerik türleri toplanıyor...")
    
    # Çıktı dizinlerinin var olduğundan emin ol
    ensure_output_directory()
    
    # İçerikleri topla
    collect_research_content()
    collect_theory_mechanism_content()
    collect_clinical_case_content()
    collect_event_education_content()
    
    # İndeks dosyasını oluştur
    create_index_file()
    
    # HTML sayfalarını oluştur
    generate_html_pages()
    
    # Statik dosyaları kopyala
    copy_static_files()
    
    logging.info("Tüm içerik türleri toplandı ve HTML sayfaları oluşturuldu.")


if __name__ == "__main__":
    logging.info("İçerik yöneticisi başlatılıyor...")
    collect_all_content()
    logging.info("İçerik yöneticisi tamamlandı.")
