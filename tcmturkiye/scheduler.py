# scheduler.py

"""
Bu modül, belirli aralıklarla içerik üretim sürecini çalıştırmak için zamanlayıcı içerir.
"""

import schedule
import time
import subprocess
from datetime import datetime
import logging

# Loglama konfigürasyonu: scheduler.log dosyasına yazacak şekilde ayarlanmıştır.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='scheduler.log',
    filemode='a'
)

def job():
    logging.info("İçerik üretimi başlatılıyor...")
    try:
        subprocess.run(["python3", "-m", "tcmturkiye.tcmturkiye"], check=True)
    except Exception as e:
        logging.exception("İçerik üretimi sırasında hata oluştu:")

def start_scheduler(run_time="16:10"):
    # Belirtilen saatte günlük çalıştır
    schedule.every().day.at(run_time).do(job)

    logging.info(f"Zamanlayıcı başlatıldı. Her gün {run_time} saatinde çalışacak.")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    job()        