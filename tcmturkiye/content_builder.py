"""Bu modül, makalelerden gelen verileri GPT ile özetleyip içerik yapısına dönüştürür.
"""

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
def generate_summary(title: str, abstract: str) -> dict:
    """Makale başlığı ve özeti kullanarak GPT ile Türkçe ve İngilizce özet oluşturur (ayrılmış)."""
    prompt = (
        f"Makale başlığı: {title}\n\n"
        f"Özet: {abstract}\n\n"
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
        summary_tr = content
        summary_en = ""

    return {"summary_tr": summary_tr, "summary_en": summary_en}

def generate_commentary(title: str, abstract: str) -> str:
    """Makalenin bilimsel değerlendirmesini oluşturur (TR ve EN yorum)."""
    prompt = (
        f"Makale başlığı: {title}\n\n"
        f"Özet: {abstract}\n\n"
        f"Bu çalışma, Geleneksel Çin Tıbbı (özellikle akupunktur) perspektifinden nasıl yorumlanabilir? "
        f"Bilimsel geçerliliği, klinik uygulamadaki potansiyel önemi ve metodolojik güçlü/zayıf yönleri nedir?\n\n"
        f"Lütfen profesyonel bir TCM doktorunun gözünden önce Türkçe sonra İngilizce kısa ve anlamlı birer yorum üret."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert Traditional Chinese Medicine (TCM) practitioner and clinical research analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def classify_article(title: str, abstract: str) -> list:
    """Makale başlığı ve özeti üzerinden olası kategori/etiketleri belirler."""
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

def generate_markdown(title: str, summary: str, commentary: str, categories: list, image_url: str, pubmed_url: str) -> str:
    """Markdown formatında tam sayfa içeriği üretir."""
    category_str = ", ".join(f"`{cat}`" for cat in categories)
    markdown = f"""# {title}

  ## 🧬 Kısa Özet  
  {summary}

  ## 🧠 Bilimsel Yorum  
  {commentary}

  ## 🔗 Kaynak  
  [PubMed'de Görüntüle]({pubmed_url})

  ## 🖼️ Görsel  
  ![Makale ile ilgili görsel]({image_url})

  ---
  Etiketler: {category_str}
  """
    return markdown
