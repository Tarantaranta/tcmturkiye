"""
Bu modül, makalelerden gelen verileri GPT ile özetleyip içerik yapısına dönüştürür.
Amaç:
 1) PubMed'den gelen makalenin orijinal özetini tam olarak koruyabilmek,
 2) GPT destekli özet ve yorumları da çift dilde (TR/EN) üretmek,
 3) Başlıkların Türkçeye çevirisini yapmak.
"""

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(title: str, abstract: str) -> dict:
    """
    Makale başlığı ve orijinal özetini kullanarak GPT ile Türkçe ve İngilizce özet oluşturur.
    """
    prompt = (
        f"Makale başlığı: {title}\n\n"
        f"Orijinal Özet:\n{abstract}\n\n"
        f"Lütfen bu makalenin hem Türkçe hem de İngilizce kısa birer özetini oluştur.\n"
        f"Aşağıdaki formatta üret:\n\n"
        f"---\n[Türkçe Özet]\n...\n---\n[English Summary]\n...\n"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a bilingual medical content summarizer."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content.strip()

    # Split into Turkish and English parts
    try:
        parts = content.split('---')
        summary_tr = parts[1].replace("[Türkçe Özet]", "").strip()
        summary_en = parts[2].replace("[English Summary]", "").strip()
    except Exception:
        # Eğer parse edemezsek tüm içerik TR'ye atanır, EN boş kalır.
        summary_tr = content
        summary_en = ""

    return {"summary_tr": summary_tr, "summary_en": summary_en}
import openai

def generate_commentary(title: str, abstract: str) -> str:
    """
    Makalenin bilimsel değerlendirmesini oluşturur (TR ve EN yorum).
    """
    prompt = (
        f"Makale başlığı: {title}\n\n"
        f"Orijinal Özet:\n{abstract}\n\n"
        f"Bu çalışma, Geleneksel Çin Tıbbı (özellikle akupunktur) perspektifinden nasıl yorumlanabilir? "
        f"Bilimsel geçerliliği, klinik uygulamadaki potansiyel önemi ve metodolojik güçlü/zayıf yönleri nedir?\n\n"
        f"\"\"\"Lütfen profesyonel bir TCM doktorunun gözünden önce Türkçe sonra İngilizce kısa ve anlamlı birer yorum üret. "
        f"Her iki dilin başlangıcını da '##TR##' ve '##EN##' şeklinde ayır.\"\"\""
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert Traditional Chinese Medicine (TCM) practitioner and clinical research analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    # Örnek çıktı: "##TR## ... \n##EN## ..."
    return response.choices[0].message.content.strip()
def translate_title(title: str, target_lang="tr") -> str:
    """
    Makale başlığını hedef dile çevirir (varsayılan: Türkçe).
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": f"Translate the following article title to {target_lang}: {title}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return title  # Hata durumunda orijinal başlığı dön

def classify_article(title: str, abstract: str) -> list:
    """
    Makale başlığı ve özeti üzerinden olası kategori/etiketleri belirler.
    """
    prompt = (
        f"Makale başlığı: {title}\n"
        f"Özet: {abstract}\n\n"
        "Bu makale için aşağıdaki sınıflardan en uygun olanları belirle:\n"
        "- Bilimsel Araştırmalar\n"
        "- Mekanizma & Teori\n"
        "- Hastalık Bazlı Uygulamalar\n"
        "- Klasik Metinler\n"
        "- İstatistik & Tablolar\n"
        "- Teknikler\n"
        "- Vaka Sunumları\n"
        "- Güncel Etkinlikler\n\n"
        "Sadece uygun kategori başlıklarını liste olarak ver. Açıklama yazma."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a medical domain classifier that categorizes TCM and acupuncture research papers."},
            {"role": "user", "content": prompt}
        ]
    )

    categories_raw = response.choices[0].message.content.strip()
    categories = [line.strip("- ").strip() for line in categories_raw.splitlines() if line.strip()]
    return categories