"""
TCM Teori ve Mekanizma Scraper Module

Bu modül, WHO, NCCIH ve diğer güvenilir kaynaklardan TCM teorileri ve
mekanizmaları hakkında bilgi çekmek için kullanılır.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import json
import re
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class TCMTheory:
    """TCM teorisi veya mekanizması bilgilerini temsil eden sınıf"""
    
    def __init__(self, title: str, content: str, source_url: str, 
                 source_name: str, category: str, 
                 publication_date: Optional[str] = None, 
                 author: Optional[str] = None,
                 keywords: Optional[List[str]] = None,
                 references: Optional[List[str]] = None):
        self.title = title
        self.content = content
        self.source_url = source_url
        self.source_name = source_name
        self.category = category  # 'theory' veya 'mechanism'
        self.publication_date = publication_date
        self.author = author
        self.keywords = keywords or []
        self.references = references or []
        
    def to_dict(self) -> Dict:
        """Teori verilerini sözlük formatına dönüştürür"""
        return {
            "title": self.title,
            "content": self.content,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "category": self.category,
            "publication_date": self.publication_date,
            "author": self.author,
            "keywords": self.keywords,
            "references": self.references
        }


def scrape_who_tcm_content() -> List[TCMTheory]:
    """
    WHO'nun TCM ile ilgili sayfalarından içerik çeker
    
    Returns:
        TCMTheory nesneleri listesi
    """
    base_urls = [
        "https://www.who.int/traditional-complementary-integrative-medicine/",
        "https://www.who.int/health-topics/traditional-complementary-and-integrative-medicine"
    ]
    
    results = []
    
    for base_url in base_urls:
        logging.info(f"WHO içeriği çekiliyor: {base_url}")
        
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ana içerik bölümü
            content_section = soup.select_one('.sf-content-block')
            if not content_section:
                continue
                
            # Başlıkları bul
            headers = content_section.select('h2, h3')
            
            for header in headers:
                title = header.text.strip()
                
                # Başlığın TCM ile ilgili olup olmadığını kontrol et
                tcm_keywords = ['traditional chinese medicine', 'tcm', 'acupuncture', 
                               'herbal medicine', 'moxibustion', 'cupping']
                
                if not any(kw in title.lower() for kw in tcm_keywords):
                    continue
                
                # İçeriği topla
                content_parts = []
                element = header.next_sibling
                
                while element and element.name not in ['h2', 'h3']:
                    if element.name == 'p':
                        content_parts.append(element.text.strip())
                    element = element.next_sibling
                
                content = '\n\n'.join(content_parts)
                
                if not content:
                    continue
                
                # Kategori belirleme
                category = 'theory'
                if any(kw in title.lower() for kw in ['mechanism', 'how it works', 'function']):
                    category = 'mechanism'
                
                # Yayın tarihi
                pub_date_elem = soup.select_one('meta[name="pubdate"]')
                pub_date = pub_date_elem['content'] if pub_date_elem and 'content' in pub_date_elem.attrs else None
                
                theory = TCMTheory(
                    title=title,
                    content=content,
                    source_url=base_url,
                    source_name="World Health Organization (WHO)",
                    category=category,
                    publication_date=pub_date,
                    keywords=extract_keywords(title + " " + content)
                )
                
                results.append(theory)
                logging.info(f"WHO içeriği bulundu: {title}")
            
            # Rate limiting
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"WHO içeriği çekilirken hata: {str(e)}")
    
    return results


def scrape_nccih_tcm_content() -> List[TCMTheory]:
    """
    NCCIH'nin TCM ile ilgili sayfalarından içerik çeker
    
    Returns:
        TCMTheory nesneleri listesi
    """
    base_urls = [
        "https://www.nccih.nih.gov/health/traditional-chinese-medicine-what-you-need-to-know",
        "https://www.nccih.nih.gov/health/acupuncture-in-depth",
        "https://www.nccih.nih.gov/health/tai-chi-and-qi-gong-in-depth"
    ]
    
    results = []
    
    for base_url in base_urls:
        logging.info(f"NCCIH içeriği çekiliyor: {base_url}")
        
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ana içerik bölümü
            content_section = soup.select_one('.page-body')
            if not content_section:
                continue
                
            # Başlık
            main_title_elem = soup.select_one('h1.page-title')
            main_title = main_title_elem.text.strip() if main_title_elem else "NCCIH TCM Content"
            
            # Alt başlıkları bul
            headers = content_section.select('h2, h3')
            
            for header in headers:
                title = header.text.strip()
                
                # İçeriği topla
                content_parts = []
                element = header.next_sibling
                
                while element and element.name not in ['h2', 'h3']:
                    if element.name == 'p':
                        content_parts.append(element.text.strip())
                    element = element.next_sibling
                
                content = '\n\n'.join(content_parts)
                
                if not content:
                    continue
                
                # Kategori belirleme
                category = 'theory'
                if any(kw in title.lower() for kw in ['mechanism', 'how it works', 'function', 'research']):
                    category = 'mechanism'
                
                # Yayın tarihi
                pub_date_elem = soup.select_one('.last-reviewed')
                pub_date = None
                if pub_date_elem:
                    date_match = re.search(r'Last Updated: ([A-Za-z]+ \d{4})', pub_date_elem.text)
                    if date_match:
                        try:
                            pub_date = datetime.strptime(date_match.group(1), '%B %Y').strftime('%Y-%m')
                        except:
                            pub_date = date_match.group(1)
                
                # Referanslar
                references = []
                ref_section = soup.select_one('.references')
                if ref_section:
                    ref_items = ref_section.select('li')
                    references = [ref.text.strip() for ref in ref_items]
                
                full_title = f"{main_title}: {title}" if main_title != title else title
                
                theory = TCMTheory(
                    title=full_title,
                    content=content,
                    source_url=base_url,
                    source_name="National Center for Complementary and Integrative Health (NCCIH)",
                    category=category,
                    publication_date=pub_date,
                    keywords=extract_keywords(title + " " + content),
                    references=references
                )
                
                results.append(theory)
                logging.info(f"NCCIH içeriği bulundu: {full_title}")
            
            # Rate limiting
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"NCCIH içeriği çekilirken hata: {str(e)}")
    
    return results


def extract_keywords(text: str) -> List[str]:
    """
    Metinden anahtar kelimeleri çıkarır
    
    Args:
        text: Anahtar kelimelerin çıkarılacağı metin
        
    Returns:
        Anahtar kelimeler listesi
    """
    # TCM ile ilgili yaygın anahtar kelimeler
    tcm_keywords = [
        'acupuncture', 'moxibustion', 'cupping', 'herbal medicine', 
        'qi', 'meridian', 'yin yang', 'five elements', 'traditional chinese medicine',
        'tcm', 'chinese medicine', 'integrative medicine', 'complementary medicine',
        'alternative medicine', 'holistic medicine', 'oriental medicine'
    ]
    
    found_keywords = []
    
    for keyword in tcm_keywords:
        if keyword in text.lower():
            found_keywords.append(keyword)
    
    return found_keywords


def save_tcm_theories(theories: List[TCMTheory], output_file: str) -> None:
    """
    TCM teorilerini JSON formatında kaydeder
    
    Args:
        theories: TCMTheory nesneleri listesi
        output_file: Çıktı dosyası yolu
    """
    try:
        theories_data = [theory.to_dict() for theory in theories]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(theories_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Teoriler {output_file} dosyasına kaydedildi.")
    except Exception as e:
        logging.error(f"Teoriler kaydedilirken hata: {str(e)}")


def scrape_all_tcm_theories() -> Tuple[List[TCMTheory], List[TCMTheory]]:
    """
    Tüm kaynaklardan TCM teorileri ve mekanizmalarını çeker
    
    Returns:
        (theories, mechanisms) şeklinde bir tuple
    """
    all_content = []
    
    # WHO içeriği
    who_content = scrape_who_tcm_content()
    all_content.extend(who_content)
    
    # NCCIH içeriği
    nccih_content = scrape_nccih_tcm_content()
    all_content.extend(nccih_content)
    
    # Teoriler ve mekanizmalar olarak ayır
    theories = [item for item in all_content if item.category == 'theory']
    mechanisms = [item for item in all_content if item.category == 'mechanism']
    
    return theories, mechanisms


if __name__ == "__main__":
    # Çıktı klasörünü oluştur
    output_dir = "tcm_content"
    os.makedirs(output_dir, exist_ok=True)
    
    # Tüm teorileri ve mekanizmaları çek
    theories, mechanisms = scrape_all_tcm_theories()
    
    # Kaydet
    save_tcm_theories(theories, os.path.join(output_dir, "tcm_theories.json"))
    save_tcm_theories(mechanisms, os.path.join(output_dir, "tcm_mechanisms.json"))
    
    logging.info(f"Toplam {len(theories)} teori ve {len(mechanisms)} mekanizma bulundu.")
