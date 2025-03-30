"""
Klinik Vaka Scraper Module

Bu modül, çeşitli akademik kaynaklardan TCM ve akupunktur ile ilgili 
klinik vaka raporlarını çekmek için kullanılır.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import json
import re
import os
from typing import List, Dict, Optional
from datetime import datetime

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ClinicalCase:
    """Klinik vaka bilgilerini temsil eden sınıf"""
    
    def __init__(self, title: str, patient_info: str, diagnosis: str, 
                 treatment: str, outcome: str, source_url: str, 
                 source_name: str, publication_date: Optional[str] = None,
                 authors: Optional[List[str]] = None,
                 keywords: Optional[List[str]] = None,
                 references: Optional[List[str]] = None):
        self.title = title
        self.patient_info = patient_info
        self.diagnosis = diagnosis
        self.treatment = treatment
        self.outcome = outcome
        self.source_url = source_url
        self.source_name = source_name
        self.publication_date = publication_date
        self.authors = authors or []
        self.keywords = keywords or []
        self.references = references or []
        
    def to_dict(self) -> Dict:
        """Vaka verilerini sözlük formatına dönüştürür"""
        return {
            "title": self.title,
            "patient_info": self.patient_info,
            "diagnosis": self.diagnosis,
            "treatment": self.treatment,
            "outcome": self.outcome,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "publication_date": self.publication_date,
            "authors": self.authors,
            "keywords": self.keywords,
            "references": self.references
        }


def scrape_case_reports_from_pmc(query: str = "acupuncture case report", max_results: int = 5) -> List[ClinicalCase]:
    """
    PubMed Central'dan klinik vaka raporlarını çeker
    
    Args:
        query: Arama sorgusu
        max_results: Maksimum sonuç sayısı
        
    Returns:
        ClinicalCase nesneleri listesi
    """
    base_url = "https://www.ncbi.nlm.nih.gov/pmc/search/api/"
    params = {
        "term": query,
        "sort": "relevance",
        "filter": "case reports[filter]",
        "format": "json",
        "start": 0,
        "resultsize": max_results
    }
    
    logging.info(f"PMC'den '{query}' araması yapılıyor...")
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('result', {}).get('docs', [])
        
        results = []
        for article in articles:
            try:
                # Makale URL'si
                pmcid = article.get('pmcid', '')
                url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/" if pmcid else ""
                
                if not url:
                    continue
                
                # Makale detaylarını al
                case_details = extract_case_details_from_pmc(url)
                if not case_details:
                    continue
                
                # Başlık
                title = article.get('title', 'Başlık bulunamadı')
                
                # Yazarlar
                authors = []
                author_list = article.get('authors', [])
                for author in author_list:
                    name = author.get('name', '')
                    if name:
                        authors.append(name)
                
                # Yayın tarihi
                pub_date = article.get('pubdate', '')
                
                case = ClinicalCase(
                    title=title,
                    patient_info=case_details.get('patient_info', ''),
                    diagnosis=case_details.get('diagnosis', ''),
                    treatment=case_details.get('treatment', ''),
                    outcome=case_details.get('outcome', ''),
                    source_url=url,
                    source_name="PubMed Central (PMC)",
                    publication_date=pub_date,
                    authors=authors,
                    keywords=case_details.get('keywords', []),
                    references=case_details.get('references', [])
                )
                
                results.append(case)
                logging.info(f"Klinik vaka bulundu: {title}")
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Vaka ayrıştırma hatası: {str(e)}")
                continue
        
        logging.info(f"Toplam {len(results)} klinik vaka bulundu.")
        return results
    
    except Exception as e:
        logging.error(f"PMC araması sırasında hata: {str(e)}")
        return []


def extract_case_details_from_pmc(url: str) -> Dict:
    """
    PMC makalesinden vaka detaylarını çıkarır
    
    Args:
        url: Makale URL'si
        
    Returns:
        Vaka detaylarını içeren sözlük
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tam metin içeriği
        full_text = ""
        content_div = soup.select_one('.jig-ncbiinpagenav')
        if content_div:
            paragraphs = content_div.select('p')
            full_text = ' '.join([p.text.strip() for p in paragraphs])
        
        if not full_text:
            return {}
        
        # Bölümleri tanımla
        patient_info = extract_section(full_text, ['case presentation', 'case report', 'patient information', 'medical history'])
        diagnosis = extract_section(full_text, ['diagnosis', 'assessment', 'clinical findings'])
        treatment = extract_section(full_text, ['treatment', 'intervention', 'therapy', 'acupuncture treatment'])
        outcome = extract_section(full_text, ['outcome', 'results', 'follow-up', 'discussion', 'conclusion'])
        
        # Anahtar kelimeler
        keywords = []
        keyword_section = soup.select_one('.keywords')
        if keyword_section:
            keyword_items = keyword_section.select('li')
            keywords = [k.text.strip() for k in keyword_items]
        
        # Referanslar
        references = []
        ref_section = soup.select_one('.ref-list')
        if ref_section:
            ref_items = ref_section.select('.element-citation')
            for ref in ref_items[:5]:  # İlk 5 referans
                ref_text = ref.text.strip()
                if ref_text:
                    references.append(ref_text)
        
        return {
            'patient_info': patient_info,
            'diagnosis': diagnosis,
            'treatment': treatment,
            'outcome': outcome,
            'keywords': keywords,
            'references': references
        }
        
    except Exception as e:
        logging.error(f"Vaka detayları alınırken hata: {str(e)}")
        return {}


def extract_section(text: str, section_keywords: List[str]) -> str:
    """
    Metinden belirli bir bölümü çıkarır
    
    Args:
        text: Tam metin
        section_keywords: Bölüm anahtar kelimeleri
        
    Returns:
        Çıkarılan bölüm metni
    """
    # Metni cümlelere böl
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Her cümleyi kontrol et
    section_start = -1
    for i, sentence in enumerate(sentences):
        if any(keyword.lower() in sentence.lower() for keyword in section_keywords):
            section_start = i
            break
    
    if section_start == -1:
        return ""
    
    # Bölüm sonunu bul (sonraki bölüm başlangıcı veya 10 cümle sonrası)
    section_end = min(section_start + 10, len(sentences))
    
    # Bölüm metnini oluştur
    section_text = ' '.join(sentences[section_start:section_end])
    return section_text


def scrape_case_reports_from_jcm() -> List[ClinicalCase]:
    """
    Journal of Chinese Medicine'dan klinik vaka raporlarını çeker
    
    Returns:
        ClinicalCase nesneleri listesi
    """
    base_url = "https://www.journalofchinesemedicine.com/case-histories"
    
    logging.info(f"Journal of Chinese Medicine'dan vaka raporları çekiliyor...")
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Vaka raporlarını bul
        case_elements = soup.select('.article-summary')
        
        results = []
        for case_elem in case_elements:
            try:
                # Başlık ve URL
                title_elem = case_elem.select_one('.article-title a')
                title = title_elem.text.strip() if title_elem else "Başlık bulunamadı"
                
                rel_url = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                url = f"https://www.journalofchinesemedicine.com{rel_url}" if rel_url.startswith('/') else rel_url
                
                if not url:
                    continue
                
                # Vaka detaylarını al
                case_details = extract_case_details_from_jcm(url)
                
                # Yazarlar
                author_elem = case_elem.select_one('.article-author')
                authors = [author_elem.text.strip()] if author_elem else []
                
                # Yayın tarihi
                date_elem = case_elem.select_one('.article-date')
                pub_date = date_elem.text.strip() if date_elem else ""
                
                case = ClinicalCase(
                    title=title,
                    patient_info=case_details.get('patient_info', ''),
                    diagnosis=case_details.get('diagnosis', ''),
                    treatment=case_details.get('treatment', ''),
                    outcome=case_details.get('outcome', ''),
                    source_url=url,
                    source_name="Journal of Chinese Medicine",
                    publication_date=pub_date,
                    authors=authors,
                    keywords=case_details.get('keywords', [])
                )
                
                results.append(case)
                logging.info(f"Klinik vaka bulundu: {title}")
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Vaka ayrıştırma hatası: {str(e)}")
                continue
        
        logging.info(f"Toplam {len(results)} klinik vaka bulundu.")
        return results
    
    except Exception as e:
        logging.error(f"JCM araması sırasında hata: {str(e)}")
        return []


def extract_case_details_from_jcm(url: str) -> Dict:
    """
    JCM makalesinden vaka detaylarını çıkarır
    
    Args:
        url: Makale URL'si
        
    Returns:
        Vaka detaylarını içeren sözlük
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tam metin içeriği
        full_text = ""
        content_div = soup.select_one('.article-full-text')
        if content_div:
            paragraphs = content_div.select('p')
            full_text = ' '.join([p.text.strip() for p in paragraphs])
        
        if not full_text:
            return {}
        
        # Bölümleri tanımla
        patient_info = extract_section(full_text, ['case', 'patient', 'history', 'presentation'])
        diagnosis = extract_section(full_text, ['diagnosis', 'assessment', 'pattern', 'syndrome'])
        treatment = extract_section(full_text, ['treatment', 'therapy', 'acupuncture', 'points', 'herbs'])
        outcome = extract_section(full_text, ['outcome', 'results', 'follow-up', 'discussion'])
        
        # Anahtar kelimeler
        keywords = []
        keyword_section = soup.select_one('.article-keywords')
        if keyword_section:
            keyword_text = keyword_section.text.strip()
            if 'Keywords:' in keyword_text:
                keyword_text = keyword_text.split('Keywords:')[1]
            keywords = [k.strip() for k in keyword_text.split(',') if k.strip()]
        
        return {
            'patient_info': patient_info,
            'diagnosis': diagnosis,
            'treatment': treatment,
            'outcome': outcome,
            'keywords': keywords
        }
        
    except Exception as e:
        logging.error(f"Vaka detayları alınırken hata: {str(e)}")
        return {}


def save_clinical_cases(cases: List[ClinicalCase], output_file: str) -> None:
    """
    Klinik vakaları JSON formatında kaydeder
    
    Args:
        cases: ClinicalCase nesneleri listesi
        output_file: Çıktı dosyası yolu
    """
    try:
        cases_data = [case.to_dict() for case in cases]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cases_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Klinik vakalar {output_file} dosyasına kaydedildi.")
    except Exception as e:
        logging.error(f"Klinik vakalar kaydedilirken hata: {str(e)}")


def scrape_all_clinical_cases() -> List[ClinicalCase]:
    """
    Tüm kaynaklardan klinik vakaları çeker
    
    Returns:
        ClinicalCase nesneleri listesi
    """
    all_cases = []
    
    # PMC'den vakalar
    pmc_cases = scrape_case_reports_from_pmc(query="acupuncture case report traditional chinese medicine", max_results=5)
    all_cases.extend(pmc_cases)
    
    # JCM'den vakalar
    jcm_cases = scrape_case_reports_from_jcm()
    all_cases.extend(jcm_cases)
    
    return all_cases


if __name__ == "__main__":
    # Çıktı klasörünü oluştur
    output_dir = "tcm_content"
    os.makedirs(output_dir, exist_ok=True)
    
    # Tüm klinik vakaları çek
    cases = scrape_all_clinical_cases()
    
    # Kaydet
    save_clinical_cases(cases, os.path.join(output_dir, "clinical_cases.json"))
    
    logging.info(f"Toplam {len(cases)} klinik vaka bulundu.")
