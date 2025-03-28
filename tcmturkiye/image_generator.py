"""
Bu modül, GPT tarafından verilen özet veya başlığa göre DALL·E API ile görsel üretir.
"""

import openai
import os
import requests
from datetime import datetime
from pathlib import Path

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_image(prompt: str) -> str:
    """Verilen metin açıklamasına göre DALL·E API kullanarak görsel üretir ve yerel olarak kaydeder."""
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )
        image_url = response['data'][0]['url']

        # Görseli URL'den indir
        image_data = requests.get(image_url).content

        # Dosya adı ve dizini
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt)[:50]
        image_dir = Path("output/images")
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / f"{timestamp}_{safe_prompt}.png"

        with open(image_path, "wb") as f:
            f.write(image_data)

        print(f"✅ Görsel başarıyla oluşturuldu: {image_path}")
        return str(image_path.relative_to("output"))
    except KeyError:
        print("❌ Görsel üretilemedi. 'data' içinde 'url' bulunamadı.")
        return ""

