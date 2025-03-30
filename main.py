#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TCM Türkiye İçerik Otomasyonu Ana Modülü

Bu script, TCM Türkiye web sitesi için içerik toplama ve HTML sayfası oluşturma
işlemlerini otomatik olarak gerçekleştirir. Belirli bir zamanda çalışacak şekilde
ayarlanabilir veya doğrudan manuel olarak çalıştırılabilir.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import time
import schedule

# TCM Türkiye modüllerini içe aktar
from tcmturkiye.content_manager import collect_all_content

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='tcm_automation.log',
    filemode='a'
)

# Konsola da log yazdırmak için
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def run_automation():
    """İçerik toplama ve HTML oluşturma işlemlerini çalıştırır"""
    logging.info("TCM Türkiye içerik otomasyonu başlatılıyor...")
    start_time = time.time()
    
    try:
        # İçerik toplama ve HTML oluşturma işlemlerini çalıştır
        collect_all_content()
        
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"TCM Türkiye içerik otomasyonu tamamlandı. Süre: {duration:.2f} saniye")
    
    except Exception as e:
        logging.error(f"İçerik otomasyonu sırasında hata oluştu: {str(e)}")
        return False
    
    return True


def start_scheduler(run_time="08:00"):
    """Belirtilen saatte günlük çalışacak zamanlayıcıyı başlatır"""
    logging.info(f"Zamanlayıcı başlatılıyor. Çalışma saati: {run_time}")
    
    # Her gün belirtilen saatte çalışacak şekilde ayarla
    schedule.every().day.at(run_time).do(run_automation)
    
    logging.info(f"Zamanlayıcı başlatıldı. Her gün saat {run_time}'de çalışacak.")
    
    # Zamanlayıcıyı sürekli kontrol et
    while True:
        schedule.run_pending()
        time.sleep(60)  # Her dakika kontrol et


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='TCM Türkiye İçerik Otomasyonu')
    
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Zamanlayıcı modunda çalıştır'
    )
    
    parser.add_argument(
        '--time',
        type=str,
        default="08:00",
        help='Zamanlayıcının çalışacağı saat (format: HH:MM, varsayılan: 08:00)'
    )
    
    args = parser.parse_args()
    
    if args.schedule:
        # Zamanlayıcı modunda çalıştır
        start_scheduler(args.time)
    else:
        # Tek seferlik çalıştır
        run_automation()


if __name__ == "__main__":
    main()
