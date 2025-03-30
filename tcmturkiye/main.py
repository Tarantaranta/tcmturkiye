#!/usr/bin/env python3
"""
TCM Türkiye İçerik Toplama Sistemi

Bu script, tüm scraper modüllerini bir araya getirir ve otomatik olarak içerik toplar.
GitHub Actions ile düzenli olarak çalıştırılabilir.
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Scraper modüllerini içe aktar
from tcmturkiye.scrapers.jstage_scraper import search_jstage, save_articles as save_jstage_articles
from tcmturkiye.scrapers.cinii_scraper import search_cinii, save_articles as save_cinii_articles
from tcmturkiye.scrapers.tcm_theory_scraper import scrape_all_tcm_theories, save_tcm_theories
from tcmturkiye.scrapers.clinical_case_scraper import scrape_all_clinical_cases, save_clinical_cases
from tcmturkiye.scrapers.events_education_scraper import (
    scrape_all_events_and_education, 
    save_events_and_education
)
from tcmturkiye.content_manager import (
    collect_all_content,
    collect_research_content,
    collect_theory_mechanism_content,
    collect_clinical_case_content,
    collect_event_education_content,
    create_index_file
)

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("tcm_scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Sabit değişkenler
OUTPUT_DIR = "tcm_content"
WEB_OUTPUT_DIR = "output/content"


def setup_directories():
    """Gerekli dizinleri oluşturur"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(WEB_OUTPUT_DIR, exist_ok=True)
    logging.info(f"Dizinler oluşturuldu: {OUTPUT_DIR}, {WEB_OUTPUT_DIR}")


def copy_content_to_web():
    """İçerik dosyalarını web dizinine kopyalar"""
    try:
        # İndeks dosyasını oku
        index_path = os.path.join(OUTPUT_DIR, "content_index.json")
        if not os.path.exists(index_path):
            logging.warning(f"İndeks dosyası bulunamadı: {index_path}")
            return
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        # İndeks dosyasını web dizinine kopyala
        web_index_path = os.path.join(WEB_OUTPUT_DIR, "content_index.json")
        with open(web_index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        # Kategori dosyalarını kopyala
        for category_key, category_info in index.get('categories', {}).items():
            file_name = category_info.get('file', '')
            if not file_name:
                continue
            
            src_path = os.path.join(OUTPUT_DIR, file_name)
            dst_path = os.path.join(WEB_OUTPUT_DIR, file_name)
            
            if os.path.exists(src_path):
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                with open(dst_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                
                logging.info(f"{file_name} web dizinine kopyalandı.")
            else:
                logging.warning(f"Kaynak dosya bulunamadı: {src_path}")
        
        logging.info("İçerik dosyaları web dizinine kopyalandı.")
    
    except Exception as e:
        logging.error(f"İçerik dosyaları kopyalanırken hata: {str(e)}")


def run_specific_scraper(scraper_type: str):
    """
    Belirli bir scraper'ı çalıştırır
    
    Args:
        scraper_type: Çalıştırılacak scraper türü
    """
    setup_directories()
    
    if scraper_type == "all":
        logging.info("Tüm scraper'lar çalıştırılıyor...")
        collect_all_content()
    elif scraper_type == "research":
        logging.info("Araştırma scraper'ı çalıştırılıyor...")
        collect_research_content()
        create_index_file()
    elif scraper_type == "theory":
        logging.info("Teori ve mekanizma scraper'ı çalıştırılıyor...")
        collect_theory_mechanism_content()
        create_index_file()
    elif scraper_type == "clinical":
        logging.info("Klinik vaka scraper'ı çalıştırılıyor...")
        collect_clinical_case_content()
        create_index_file()
    elif scraper_type == "events":
        logging.info("Etkinlik ve eğitim scraper'ı çalıştırılıyor...")
        collect_event_education_content()
        create_index_file()
    else:
        logging.error(f"Bilinmeyen scraper türü: {scraper_type}")
        return
    
    # İçerikleri web dizinine kopyala
    copy_content_to_web()
    
    logging.info(f"{scraper_type} scraper çalışması tamamlandı.")


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="TCM Türkiye İçerik Toplama Sistemi")
    parser.add_argument(
        "--type", 
        choices=["all", "research", "theory", "clinical", "events"],
        default="all",
        help="Çalıştırılacak scraper türü"
    )
    
    args = parser.parse_args()
    run_specific_scraper(args.type)


if __name__ == "__main__":
    main()
