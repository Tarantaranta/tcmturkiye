# scheduler.py

"""
Bu modül, belirli aralıklarla içerik üretim sürecini çalıştırmak için zamanlayıcı içerir.
Farklı içerik türlerini farklı zamanlarda veya sıklıklarda çalıştırabilir.
"""

import schedule
import time
import importlib
import logging
from datetime import datetime
from typing import Dict, List, Callable, Optional

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='scheduler.log',
    filemode='a'
)

# Konsola da log yazdırmak için
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# İçerik yöneticisi modülü
from tcmturkiye.content_manager import (
    collect_all_content,
    collect_research_content,
    collect_theory_mechanism_content,
    collect_clinical_case_content,
    collect_event_education_content,
    create_index_file
)

def job_all_content():
    """Tüm içerik türlerini toplar"""
    logging.info("Tüm içerik türleri için içerik üretimi başlatılıyor...")
    try:
        collect_all_content()
        logging.info("Tüm içerik türleri için içerik üretimi tamamlandı.")
    except Exception as e:
        logging.exception("İçerik üretimi sırasında hata oluştu:")

def job_research_content():
    """Sadece araştırma içeriklerini toplar"""
    logging.info("Araştırma içerikleri için içerik üretimi başlatılıyor...")
    try:
        collect_research_content()
        create_index_file()  # İndeksi güncelle
        logging.info("Araştırma içerikleri için içerik üretimi tamamlandı.")
    except Exception as e:
        logging.exception("Araştırma içerikleri üretimi sırasında hata oluştu:")

def job_theory_mechanism_content():
    """Teori ve mekanizma içeriklerini toplar"""
    logging.info("Teori ve mekanizma içerikleri için içerik üretimi başlatılıyor...")
    try:
        collect_theory_mechanism_content()
        create_index_file()  # İndeksi güncelle
        logging.info("Teori ve mekanizma içerikleri için içerik üretimi tamamlandı.")
    except Exception as e:
        logging.exception("Teori ve mekanizma içerikleri üretimi sırasında hata oluştu:")

def job_clinical_case_content():
    """Klinik vaka içeriklerini toplar"""
    logging.info("Klinik vaka içerikleri için içerik üretimi başlatılıyor...")
    try:
        collect_clinical_case_content()
        create_index_file()  # İndeksi güncelle
        logging.info("Klinik vaka içerikleri için içerik üretimi tamamlandı.")
    except Exception as e:
        logging.exception("Klinik vaka içerikleri üretimi sırasında hata oluştu:")

def job_event_education_content():
    """Etkinlik ve eğitim içeriklerini toplar"""
    logging.info("Etkinlik ve eğitim içerikleri için içerik üretimi başlatılıyor...")
    try:
        collect_event_education_content()
        create_index_file()  # İndeksi güncelle
        logging.info("Etkinlik ve eğitim içerikleri için içerik üretimi tamamlandı.")
    except Exception as e:
        logging.exception("Etkinlik ve eğitim içerikleri üretimi sırasında hata oluştu:")

def start_scheduler(config: Optional[Dict] = None):
    """
    Zamanlayıcıyı başlatır
    
    Args:
        config: Zamanlama yapılandırması. Belirtilmezse varsayılan yapılandırma kullanılır.
    """
    if config is None:
        # Varsayılan zamanlama yapılandırması
        config = {
            'all_content': {'time': '03:00', 'days': 'monday'},  # Pazartesi günleri saat 3'te tüm içerikler
            'research': {'time': '04:00', 'days': 'daily'},      # Her gün saat 4'te araştırma içerikleri
            'theory_mechanism': {'time': '05:00', 'days': 'wednesday,saturday'},  # Çarşamba ve Cumartesi
            'clinical_case': {'time': '06:00', 'days': 'tuesday,friday'},  # Salı ve Cuma
            'event_education': {'time': '07:00', 'days': 'thursday,sunday'}  # Perşembe ve Pazar
        }
    
    # Job fonksiyonları
    job_map = {
        'all_content': job_all_content,
        'research': job_research_content,
        'theory_mechanism': job_theory_mechanism_content,
        'clinical_case': job_clinical_case_content,
        'event_education': job_event_education_content
    }
    
    # Zamanlamaları ayarla
    for job_type, job_config in config.items():
        if job_type not in job_map:
            logging.warning(f"Bilinmeyen iş türü: {job_type}, atlanıyor.")
            continue
        
        job_func = job_map[job_type]
        job_time = job_config.get('time', '03:00')
        job_days = job_config.get('days', 'daily')
        
        if job_days == 'daily':
            schedule.every().day.at(job_time).do(job_func)
            logging.info(f"{job_type} işi her gün {job_time} saatinde çalışacak.")
        else:
            days = job_days.split(',')
            for day in days:
                day = day.strip().lower()
                if day == 'monday':
                    schedule.every().monday.at(job_time).do(job_func)
                elif day == 'tuesday':
                    schedule.every().tuesday.at(job_time).do(job_func)
                elif day == 'wednesday':
                    schedule.every().wednesday.at(job_time).do(job_func)
                elif day == 'thursday':
                    schedule.every().thursday.at(job_time).do(job_func)
                elif day == 'friday':
                    schedule.every().friday.at(job_time).do(job_func)
                elif day == 'saturday':
                    schedule.every().saturday.at(job_time).do(job_func)
                elif day == 'sunday':
                    schedule.every().sunday.at(job_time).do(job_func)
                else:
                    logging.warning(f"Bilinmeyen gün: {day}, atlanıyor.")
                    continue
                
                logging.info(f"{job_type} işi her {day} günü {job_time} saatinde çalışacak.")
    
    logging.info("Zamanlayıcı başlatıldı.")
    
    # Zamanlayıcıyı çalıştır
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Tüm içerikleri hemen topla
    job_all_content()
    
    # Zamanlayıcıyı başlat
    start_scheduler()