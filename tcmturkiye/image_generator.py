"""
Bu modül, GPT tarafından verilen özet veya başlığa göre DALL·E API ile görsel üretir.
"""

import openai
import os
import requests
from datetime import datetime
from pathlib import Path

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_image(subject: str) -> str:
    """
    DALL·E 3 API kullanarak, verilen konuya uygun yüksek kaliteli, 3D bilimsel bir görsel oluşturur.
    Görselde metin veya grafiksel overlay bulunmaz.
    """
    import openai
    # Yeni prompt: 3D, detaylı, profesyonel bilimsel çizim, metinsiz, gerçekçi detaylar.
    prompt = (
        f"A high-quality 3D scientific illustration of {subject}. "
        "The image should be professional and highly detailed with realistic lighting and textures, "
        "minimal background, no text or watermarks, and suitable for academic publication."
    )
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        # Hata durumunda default bir resim URL'si dönebilir veya hata loglanabilir.
        import logging
        logging.exception("Görsel oluşturulurken hata meydana geldi:")
        return ""
