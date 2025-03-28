# tcmturkiye.py
# tcm_scraper_automation.py

"""
Otomatik TCM (Geleneksel Çin Tıbbı) bilgi sistemi mimarisi
Amaç: PubMed üzerinden akupunkturla ilgili güncel makaleleri çekmek,
      özet çıkarmak, görsel üretmek ve yayınlanabilir içerik formatı oluşturmak
"""

# Bölüm 1: Gereken kütüphaneler
import requests
import datetime
import os
from typing import List, Dict
from tcmturkiye.pubmed_parser import parse_pubmed_xml
from tcmturkiye.content_builder import generate_summary
from tcmturkiye.content_builder import classify_article
from tcmturkiye.content_builder import generate_commentary
from tcmturkiye.generate_index import generate_index_html
from tcmturkiye.image_generator import generate_image
from tcmturkiye.markdown_writer import save_markdown, build_markdown_content

# -- GPT ve DALL·E için OpenAI bağlantısı
import openai

# Bölüm 2: Ayarlar
openai.api_key = os.getenv("OPENAI_API_KEY")

SEARCH_TERM = "acupuncture"
RESULT_COUNT = 3

# Bölüm 3: PubMed API üzerinden veri çekme

def get_pubmed_articles(query: str, max_results: int = 5) -> List[Dict]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "sort": "pub date"
    }
    response = requests.get(base_url, params=params)
    id_list = response.json()["esearchresult"]["idlist"]

    # Makale detaylarını al
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }
    fetch_response = requests.get(fetch_url, params=fetch_params)
    return fetch_response.text

# Bölüm 4: GPT ile özetleme

def summarize_article(text: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a scientific summarizer who explains medical research in simple, structured format."},
            {"role": "user", "content": f"Please summarize this research in Turkish and English:\n{text}"}
        ]
    )
    return response.choices[0].message.content

# Gelecek adımlar:
# - XML parser ile makale başlık, özet ayrıştırılacak
# - İçerik dosyası olarak Markdown/HTML üretilecek
# - Web'e otomatik yükleme yapılacak

# Test başlatıcı (manuel çalıştırma için)
if __name__ == "__main__":
    print("🔍 Makaleler PubMed üzerinden çekiliyor...")
    xml_data = get_pubmed_articles(SEARCH_TERM, RESULT_COUNT)

    with open("pubmed_raw.xml", "w", encoding="utf-8") as f:
        f.write(xml_data)
    print("📄 pubmed_raw.xml dosyasına veri yazıldı.")

    print("🧠 XML çözümlemesi yapılıyor...")
    articles = parse_pubmed_xml(xml_data)
    print(f"📋 {len(articles)} makale ayrıştırıldı.")

    for article in articles:
        if "pmid" not in article:
            print(f"❌ Hata: 'pmid' alanı bulunamadı. Makale atlanıyor. Başlık: {article.get('title', 'Bilinmiyor')}")
            continue
        article["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/"
        print("🏷️ Makale kategorilendiriliyor...")
        article["categories"] = classify_article(article["title"], article["abstract"])

        print(f"✍️ Özet hazırlanıyor: {article['title']}")
        summary_parts = generate_summary(article["title"], article["abstract"])

        print("🧠 Yorum oluşturuluyor...")
        commentary = generate_commentary(article["title"], article["abstract"])

        print("🎨 Görsel üretiliyor...")
        image_url = generate_image(article["title"] + " acupuncture medical illustration")

        print("📄 Markdown formatı hazırlanıyor...")
        markdown = build_markdown_content(
            title=article["title"],
            abstract=article["abstract"],
            summary=summary_parts["summary_tr"],
            summary_en=summary_parts["summary_en"],
            commentary=commentary,
            commentary_en="",
            categories=article["categories"],
            image_url=image_url,
            image_path=image_url,  # same as image_url for now
            pubmed_url=article["url"],
            authors=article.get("authors", [])
        )

        print("💾 Markdown olarak kaydediliyor...")
        save_markdown(article, markdown)

    generate_index_html()

    print("✅ Tüm işlemler tamamlandı.")