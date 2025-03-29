# tcmturkiye.py
# tcm_scraper_automation.py

"""
Otomatik TCM (Geleneksel Çin Tıbbı) bilgi sistemi mimarisi
Amaç: PubMed üzerinden akupunkturla ilgili en yeni makaleleri tek tek çekmek,
      her seferinde yeni bir makale işlemek,
      özet çıkarmak, görsel üretmek ve yayınlanabilir içerik formatı oluşturmak.
"""

import logging
import requests
import datetime
import os
import sys
from dotenv import load_dotenv
load_dotenv()
from typing import List, Dict

# PubMed XML ayrıştırma
from tcmturkiye.pubmed_parser import parse_pubmed_xml
# GPT tabanlı içerik fonksiyonları
from tcmturkiye.content_builder import (
    generate_summary,
    classify_article,
    generate_commentary,
    translate_title
)
# index oluşturma (örneğin, index-tr.html / index-en.html)
from tcmturkiye.generate_index import generate_index_html
# DALL·E API ile görsel üretimi
from tcmturkiye.image_generator import generate_image
# Markdown dosyaları yazma
from tcmturkiye.markdown_writer import (
    save_markdown,
    build_markdown_content_tr,
    build_markdown_content_en
)

# -- GPT ve DALL·E için OpenAI bağlantısı
import openai

# Loglama konfigürasyonu: INFO seviyesinde log alacak ve zaman damgası ekleyecek.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Ayarlar
openai.api_key = os.getenv("OPENAI_API_KEY")

SEARCH_TERM = "acupuncture"
# Bu kod tek bir makale çekmeye çalışacak
RETMAX_SINGLE = 1

def get_pubmed_articles_single(query: str, retstart: int = 0) -> str:
    """
    PubMed'den, belirtilen arama terimiyle tek bir makale (retmax=1) çeker.
    retstart parametresi sıralamada ileri gitmeyi sağlar.
    Geriye XML verisi döndürür.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": RETMAX_SINGLE,  # 1 sonuç
        "retstart": retstart,
        "sort": "pub date"
    }
    response = requests.get(base_url, params=params)
    id_list = response.json()["esearchresult"]["idlist"]
    if not id_list:
        # Hiç sonuç dönmediyse boş string verelim
        return ""

    # Makale detaylarını al
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }
    fetch_response = requests.get(fetch_url, params=fetch_params)
    return fetch_response.text

if __name__ == "__main__":
    logging.info("🔍 Yeni bir makale aranıyor...")

    # Daha önce işlenmiş PMID'leri tutan dosya
    processed_ids_file = "processed_pmids.txt"
    if not os.path.exists(processed_ids_file):
        open(processed_ids_file, "w").close()

    with open(processed_ids_file, "r", encoding="utf-8") as f:
        processed_ids = set(line.strip() for line in f if line.strip())

    retstart = 0
    new_article_found = False
    max_tries = 50  # çok sayıda deneme hakkı

    while not new_article_found and max_tries > 0:
        max_tries -= 1
        # Tek makale XML'i çek
        xml_data = get_pubmed_articles_single(SEARCH_TERM, retstart=retstart)
        if not xml_data.strip():
            logging.info(f"❌ Makale bulunamadı veya retstart={retstart} için sonuç yok.")
            retstart += 1
            continue

        with open("pubmed_raw.xml", "w", encoding="utf-8") as f:
            f.write(xml_data)
        logging.info("📄 pubmed_raw.xml dosyasına veri yazıldı.")

        articles = parse_pubmed_xml(xml_data)
        if len(articles) == 0:
            logging.info(f"❌ parse_pubmed_xml ile makale bulunamadı (retstart={retstart}).")
            retstart += 1
            continue

        # Tek makale
        article = articles[0]
        pmid = article.get("pmid", "PMID bulunamadı")
        if pmid == "PMID bulunamadı":
            logging.error("❌ PMID alınamadı, bu makale atlanıyor.")
            retstart += 1
            continue

        if pmid in processed_ids:
            logging.info(f"Bu makale zaten işlenmiş (PMID={pmid}). Sonraki retstart={retstart+1}")
            retstart += 1
            continue

        # Yeni makale bulundu!
        new_article_found = True
        logging.info(f"✅ Yeni makale bulundu: PMID={pmid}")
        article["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

        logging.info("🏷️ Makale kategorilendiriliyor...")
        article["categories"] = classify_article(article["title"], article["abstract"])

        logging.info(f"✍️ Özet hazırlanıyor: {article['title']}")
        summary_parts = generate_summary(article["title"], article["abstract"])
        article["summary_tr"] = summary_parts.get("summary_tr", "")
        article["summary_en"] = summary_parts.get("summary_en", "")

        logging.info("🧠 Yorum oluşturuluyor...")
        commentary_raw = generate_commentary(article["title"], article["abstract"])
        # Örnek çıktı: \"##TR## ... \\n##EN## ...\"
        commentary_parts = commentary_raw.split("##EN##")
        commentary_tr = commentary_parts[0].replace("##TR##", "").strip()
        commentary_en = commentary_parts[1].strip() if len(commentary_parts) > 1 else ""
        article["commentary_tr"] = commentary_tr
        article["commentary_en"] = commentary_en

        logging.info("🔤 Başlık Türkçeye çevriliyor...")
        article["title_tr"] = translate_title(article["title"], target_lang="tr")

        logging.info("🎨 Görsel üretiliyor...")
        image_url = generate_image(article["title"] + " acupuncture medical illustration")
        article["image_path"] = image_url

        logging.info("📄 Markdown formatı hazırlanıyor (TR & EN)...")
        # Türkçe içerik
        markdown_tr = build_markdown_content_tr(
            title=article["title_tr"],
            authors=article.get("authors", []),
            abstract=article["abstract"],
            summary_tr=article["summary_tr"],
            commentary_tr=article["commentary_tr"],
            image_path=article["image_path"],
            pubmed_url=article["url"],
            categories=article["categories"],
            tags=[]
        )
        save_markdown(article, markdown_tr, language="tr")

        # İngilizce içerik
        markdown_en = build_markdown_content_en(
            title=article["title"],
            authors=article.get("authors", []),
            abstract=article["abstract"],
            summary_en=article["summary_en"],
            commentary_en=article["commentary_en"],
            image_path=article["image_path"],
            pubmed_url=article["url"],
            categories=article["categories"],
            tags=[]
        )
        save_markdown(article, markdown_en, language="en")

        logging.info("💾 Markdown olarak kaydedildi.")

        # Makale işlem bitti, PMID kaydedelim
        processed_ids.add(pmid)
        with open(processed_ids_file, "a", encoding="utf-8") as ff:
            ff.write(pmid + "\n")

    # Döngüden çıkınca index.html güncellenebilir
    if new_article_found:
        generate_index_html()
        logging.info("✅ Tüm işlemler tamamlandı.")
    else:
        logging.info("💡 Yeni makale bulunamadı; muhtemelen arama sonuçları tükendi veya limit aşıldı.")