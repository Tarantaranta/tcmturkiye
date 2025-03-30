"""
J-STAGE Scraper Module

Bu modül, J-STAGE (Japan Science and Technology Agency) platformundan 
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

class JStageArticle:
    """J-STAGE makale verilerini temsil eden sınıf"""
    
    def __init__(self, title: str, authors: List[str], abstract: str, 
                 url: str, publication_date: str, journal: str, 
                 doi: Optional[str] = None, keywords: Optional[List[str]] = None):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.url = url
        self.publication_date = publication_date
        self.journal = journal
        self.doi = doi
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
            "doi": self.doi,
            "keywords": self.keywords,
            "source": "J-STAGE"
        }


def search_jstage(query: str, max_results: int = 5) -> List[JStageArticle]:
    """
    J-STAGE'de arama yapar ve sonuçları JStageArticle nesneleri listesi olarak döndürür.
    
    Args:
        query: Arama sorgusu
        max_results: Maksimum sonuç sayısı
        
    Returns:
        JStageArticle nesneleri listesi
    """
    base_url = "https://www.jstage.jst.go.jp/result/global/-char/en"
    params = {
        "item1": query,
        "word1": "AND",
        "item2": "",
        "word2": "AND",
        "item3": "",
        "sortFlag": "1", # Yeniden eskiye sıralama
        "filterTypeName": "all",
        "filterTypeCode": "1"
    }
    
    logging.info(f"J-STAGE'de '{query}' araması yapılıyor...")
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_elements = soup.select('.searchlist-items')
        
        results = []
        for idx, article_elem in enumerate(article_elements[:max_results]):
            try:
                # Başlık ve URL
                title_elem = article_elem.select_one('.searchlist-title a')
                title = title_elem.text.strip() if title_elem else "Başlık bulunamadı"
                url = "https://www.jstage.jst.go.jp" + title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                
                # Yazarlar
                author_elem = article_elem.select_one('.searchlist-authortags')
                authors = [a.text.strip() for a in author_elem.select('a')] if author_elem else []
                
                # Dergi ve Tarih
                journal_elem = article_elem.select_one('.searchlist-jounal-date')
                journal_text = journal_elem.text.strip() if journal_elem else ""
                journal = journal_text.split(',')[0].strip() if ',' in journal_text else journal_text
                
                # Yayın tarihi
                date_text = journal_text.split(',')[1].strip() if ',' in journal_text else ""
                try:
                    publication_date = datetime.strptime(date_text, '%Y/%m/%d').strftime('%Y-%m-%d')
                except:
                    publication_date = date_text
                
                # Makale detaylarını almak için makale sayfasına git
                article_details = get_article_details(url) if url else {}
                
                article = JStageArticle(
                    title=title,
                    authors=authors,
                    abstract=article_details.get('abstract', ''),
                    url=url,
                    publication_date=publication_date,
                    journal=journal,
                    doi=article_details.get('doi', ''),
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
        logging.error(f"J-STAGE araması sırasında hata: {str(e)}")
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
        abstract_elem = soup.select_one('.abstract-content')
        abstract = abstract_elem.text.strip() if abstract_elem else ""
        
        # DOI
        doi_elem = soup.select_one('meta[name="citation_doi"]')
        doi = doi_elem['content'] if doi_elem and 'content' in doi_elem.attrs else ""
        
        # Anahtar kelimeler
        keyword_elems = soup.select('.keywords-list li')
        keywords = [k.text.strip() for k in keyword_elems] if keyword_elems else []
        
        return {
            'abstract': abstract,
            'doi': doi,
            'keywords': keywords
        }
        
    except Exception as e:
        logging.error(f"Makale detayları alınırken hata: {str(e)}")
        return {}


def save_jstage_articles(articles: List[JStageArticle], output_file: str) -> None:
    """
    J-STAGE makalelerini JSON formatında kaydeder
    
    Args:
        articles: JStageArticle nesneleri listesi
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
    articles = search_jstage("acupuncture", max_results=3)
    if articles:
        save_jstage_articles(articles, "jstage_articles.json")
