"""
CiNii Scraper Module

Bu modül, CiNii (Citation Information by National Institute of Informatics) platformundan 
akupunktur ve geleneksel Çin tıbbı ile ilgili makaleleri çekmek için kullanılır.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import json
from typing import List, Dict, Optional
from datetime import datetime

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class CiNiiArticle:
    """CiNii makale verilerini temsil eden sınıf"""
    
    def __init__(self, title: str, authors: List[str], abstract: str, 
                 url: str, publication_date: str, journal: str, 
                 naid: Optional[str] = None, keywords: Optional[List[str]] = None):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.url = url
        self.publication_date = publication_date
        self.journal = journal
        self.naid = naid  # CiNii Article ID
        self.keywords = keywords or []
        
    def to_dict(self) -> Dict:
        """Makale verilerini sözlük formatına dönüştürür"""
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "publication_date": self.publication_date,
            "journal": self.journal,
            "naid": self.naid,
            "keywords": self.keywords,
            "source": "CiNii"
        }


def search_cinii(query: str, max_results: int = 5) -> List[CiNiiArticle]:
    """
    CiNii'de arama yapar ve sonuçları CiNiiArticle nesneleri listesi olarak döndürür.
    
    Args:
        query: Arama sorgusu
        max_results: Maksimum sonuç sayısı
        
    Returns:
        CiNiiArticle nesneleri listesi
    """
    base_url = "https://ci.nii.ac.jp/search"
    params = {
        "q": query,
        "count": max_results,
        "sortorder": "1",  # Yeniden eskiye sıralama
        "type": "0",       # Tüm koleksiyonlar
        "lang": "en"       # İngilizce arayüz
    }
    
    logging.info(f"CiNii'de '{query}' araması yapılıyor...")
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_elements = soup.select('.item_body')
        
        results = []
        for idx, article_elem in enumerate(article_elements[:max_results]):
            try:
                # Başlık ve URL
                title_elem = article_elem.select_one('.itemheading a')
                title = title_elem.text.strip() if title_elem else "Başlık bulunamadı"
                
                rel_url = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                url = f"https://ci.nii.ac.jp{rel_url}" if rel_url.startswith('/') else rel_url
                
                # NAID (CiNii Article ID) çıkarma
                naid = None
                if rel_url and '/naid/' in rel_url:
                    naid = rel_url.split('/naid/')[1].split('/')[0]
                
                # Yazarlar
                author_elem = article_elem.select_one('.item_author')
                authors = [a.text.strip() for a in author_elem.select('a')] if author_elem else []
                
                # Dergi ve Tarih
                journal_elem = article_elem.select_one('.item_journal')
                journal_text = journal_elem.text.strip() if journal_elem else ""
                
                # Dergi adı ve tarih ayrıştırma
                journal = ""
                publication_date = ""
                if journal_text:
                    parts = journal_text.split(',')
                    journal = parts[0].strip() if parts else ""
                    
                    # Tarih formatını ayrıştırma
                    date_part = parts[1].strip() if len(parts) > 1 else ""
                    try:
                        # Farklı tarih formatlarını deneme
                        if date_part:
                            for fmt in ['%Y-%m', '%Y/%m', '%Y-%m-%d', '%Y/%m/%d', '%Y']:
                                try:
                                    parsed_date = datetime.strptime(date_part, fmt)
                                    publication_date = parsed_date.strftime('%Y-%m-%d')
                                    break
                                except ValueError:
                                    continue
                            
                            # Hiçbir format eşleşmediyse orijinal metni kullan
                            if not publication_date:
                                publication_date = date_part
                    except:
                        publication_date = date_part
                
                # Makale detaylarını almak için makale sayfasına git
                article_details = get_article_details(url) if url else {}
                
                article = CiNiiArticle(
                    title=title,
                    authors=authors,
                    abstract=article_details.get('abstract', ''),
                    url=url,
                    publication_date=publication_date,
                    journal=journal,
                    naid=naid,
                    keywords=article_details.get('keywords', [])
                )
                
                results.append(article)
                logging.info(f"Makale bulundu: {title}")
                
                # Rate limiting - sunucuya yük bindirmemek için
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Makale ayrıştırma hatası: {str(e)}")
                continue
        
        logging.info(f"Toplam {len(results)} makale bulundu.")
        return results
    
    except Exception as e:
        logging.error(f"CiNii araması sırasında hata: {str(e)}")
        return []


def get_article_details(article_url: str) -> Dict:
    """
    Makale URL'sinden detaylı bilgileri çeker
    
    Args:
        article_url: Makale URL'si
        
    Returns:
        Makale detaylarını içeren sözlük
    """
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Özet
        abstract_elem = soup.select_one('.itemAbstract')
        abstract = abstract_elem.text.strip() if abstract_elem else ""
        
        # Anahtar kelimeler
        keyword_elems = soup.select('.itemKeyword a')
        keywords = [k.text.strip() for k in keyword_elems] if keyword_elems else []
        
        return {
            'abstract': abstract,
            'keywords': keywords
        }
        
    except Exception as e:
        logging.error(f"Makale detayları alınırken hata: {str(e)}")
        return {}


def save_cinii_articles(articles: List[CiNiiArticle], output_file: str) -> None:
    """
    CiNii makalelerini JSON formatında kaydeder
    
    Args:
        articles: CiNiiArticle nesneleri listesi
        output_file: Çıktı dosyası yolu
    """
    try:
        articles_data = [article.to_dict() for article in articles]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Makaleler {output_file} dosyasına kaydedildi.")
    except Exception as e:
        logging.error(f"Makaleler kaydedilirken hata: {str(e)}")


if __name__ == "__main__":
    # Test
    articles = search_cinii("acupuncture", max_results=3)
    if articles:
        save_cinii_articles(articles, "cinii_articles.json")
