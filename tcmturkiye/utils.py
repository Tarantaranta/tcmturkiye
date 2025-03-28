# utils.py

"""
Ortak yardımcı fonksiyonlar: tarih formatlama, dosya adı temizleme vs.
"""

import re
from datetime import datetime

def get_timestamped_filename(title: str, extension: str = "md") -> str:
    """
    Makale başlığına göre zaman damgalı güvenli dosya adı oluşturur.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_title = sanitize_filename(title)
    return f"{timestamp}_{safe_title}.{extension}"

def sanitize_filename(name: str) -> str:
    """
    Dosya adı için geçersiz karakterleri temizler.
    """
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:100]
