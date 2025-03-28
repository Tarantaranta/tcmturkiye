# scheduler.py

"""
Bu modül, belirli aralıklarla içerik üretim sürecini çalıştırmak için zamanlayıcı içerir.
"""

import schedule
import time
import subprocess
from datetime import datetime

def job():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] İçerik üretimi başlatılıyor...")
    with open("scheduler.log", "a") as log_file:
        log_file.write(f"[{timestamp}] İçerik üretimi başlatılıyor...\n")
    subprocess.run(["python3", "-m", "tcmturkiye.tcmturkiye"])

def start_scheduler(run_time="09:00"):
    # Belirtilen saatte günlük çalıştır
    schedule.every().day.at(run_time).do(job)

    print(f"Zamanlayıcı başlatıldı. Her gün {run_time} saatinde çalışacak.")
    while True:
        schedule.run_pending()
        time.sleep(60)
