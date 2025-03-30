"""
Etkinlikler ve Eğitimler Scraper Module

Bu modül, TCM ve akupunktur ile ilgili etkinlikler (konferanslar, seminerler) ve 
eğitim programları hakkında bilgi toplamak için kullanılır.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import json
import re
import os
from typing import List, Dict, Optional, Union
from datetime import datetime

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class TCMEvent:
    """TCM etkinliği bilgilerini temsil eden sınıf"""
    
    def __init__(self, title: str, description: str, event_type: str,
                 start_date: str, end_date: Optional[str] = None,
                 location: Optional[str] = None, organizer: Optional[str] = None,
                 url: Optional[str] = None, registration_url: Optional[str] = None,
                 source_name: str = "", keywords: Optional[List[str]] = None):
        self.title = title
        self.description = description
        self.event_type = event_type  # 'conference', 'seminar', 'workshop', etc.
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.organizer = organizer
        self.url = url
        self.registration_url = registration_url
        self.source_name = source_name
        self.keywords = keywords or []
        
    def to_dict(self) -> Dict:
        """Etkinlik verilerini sözlük formatına dönüştürür"""
        return {
            "title": self.title,
            "description": self.description,
            "event_type": self.event_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "location": self.location,
            "organizer": self.organizer,
            "url": self.url,
            "registration_url": self.registration_url,
            "source_name": self.source_name,
            "keywords": self.keywords
        }


class TCMEducation:
    """TCM eğitim programı bilgilerini temsil eden sınıf"""
    
    def __init__(self, title: str, description: str, program_type: str,
                 duration: str, institution: str, start_date: Optional[str] = None,
                 location: Optional[str] = None, url: Optional[str] = None,
                 certification: Optional[str] = None, price: Optional[str] = None,
                 source_name: str = "", keywords: Optional[List[str]] = None):
        self.title = title
        self.description = description
        self.program_type = program_type  # 'course', 'degree', 'certificate', etc.
        self.duration = duration
        self.institution = institution
        self.start_date = start_date
        self.location = location
        self.url = url
        self.certification = certification
        self.price = price
        self.source_name = source_name
        self.keywords = keywords or []
        
    def to_dict(self) -> Dict:
        """Eğitim programı verilerini sözlük formatına dönüştürür"""
        return {
            "title": self.title,
            "description": self.description,
            "program_type": self.program_type,
            "duration": self.duration,
            "institution": self.institution,
            "start_date": self.start_date,
            "location": self.location,
            "url": self.url,
            "certification": self.certification,
            "price": self.price,
            "source_name": self.source_name,
            "keywords": self.keywords
        }


def scrape_tcm_events_from_tcmworld() -> List[TCMEvent]:
    """
    TCM World Foundation'dan etkinlikleri çeker
    
    Returns:
        TCMEvent nesneleri listesi
    """
    base_url = "https://www.tcmworld.org/events/"
    
    logging.info(f"TCM World Foundation'dan etkinlikler çekiliyor...")
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Etkinlik kartlarını bul
        event_elements = soup.select('.event-card, .event-item')
        
        results = []
        for event_elem in event_elements:
            try:
                # Başlık
                title_elem = event_elem.select_one('.event-title, .title')
                title = title_elem.text.strip() if title_elem else "Başlık bulunamadı"
                
                # URL
                url_elem = title_elem.find('a') if title_elem else None
                url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
                
                # Tarih
                date_elem = event_elem.select_one('.event-date, .date')
                date_text = date_elem.text.strip() if date_elem else ""
                
                start_date = ""
                end_date = ""
                
                if date_text:
                    # Tarih formatını ayrıştırma
                    date_parts = date_text.split('-')
                    
                    if len(date_parts) > 1:
                        # Başlangıç ve bitiş tarihi var
                        try:
                            start_date_obj = parse_date(date_parts[0].strip())
                            end_date_obj = parse_date(date_parts[1].strip())
                            
                            start_date = start_date_obj.strftime('%Y-%m-%d') if start_date_obj else ""
                            end_date = end_date_obj.strftime('%Y-%m-%d') if end_date_obj else ""
                        except:
                            start_date = date_parts[0].strip()
                            end_date = date_parts[1].strip()
                    else:
                        # Sadece tek tarih var
                        try:
                            date_obj = parse_date(date_text)
                            start_date = date_obj.strftime('%Y-%m-%d') if date_obj else date_text
                        except:
                            start_date = date_text
                
                # Konum
                location_elem = event_elem.select_one('.event-location, .location')
                location = location_elem.text.strip() if location_elem else ""
                
                # Açıklama
                desc_elem = event_elem.select_one('.event-description, .description')
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Etkinlik türü belirleme
                event_type = "seminar"  # Varsayılan
                if any(kw in title.lower() for kw in ['conference', 'kongre', 'konferans']):
                    event_type = "conference"
                elif any(kw in title.lower() for kw in ['workshop', 'atölye']):
                    event_type = "workshop"
                
                # Kayıt URL'si
                register_elem = event_elem.select_one('.register-button, .register')
                registration_url = register_elem['href'] if register_elem and 'href' in register_elem.attrs else ""
                
                # Organizatör
                organizer = "TCM World Foundation"
                
                event = TCMEvent(
                    title=title,
                    description=description,
                    event_type=event_type,
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    organizer=organizer,
                    url=url,
                    registration_url=registration_url,
                    source_name="TCM World Foundation",
                    keywords=extract_keywords(title + " " + description)
                )
                
                results.append(event)
                logging.info(f"Etkinlik bulundu: {title}")
                
            except Exception as e:
                logging.error(f"Etkinlik ayrıştırma hatası: {str(e)}")
                continue
        
        logging.info(f"Toplam {len(results)} etkinlik bulundu.")
        return results
    
    except Exception as e:
        logging.error(f"TCM World Foundation etkinlikleri çekilirken hata: {str(e)}")
        return []


def scrape_tcm_events_from_iccmr() -> List[TCMEvent]:
    """
    International Congress on Complementary Medicine Research (ICCMR) etkinliklerini çeker
    
    Returns:
        TCMEvent nesneleri listesi
    """
    base_url = "https://www.iccmr-congress.org/upcoming-events/"
    
    logging.info(f"ICCMR etkinlikleri çekiliyor...")
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Etkinlik bölümlerini bul
        event_elements = soup.select('.event-item, .event-block')
        
        results = []
        for event_elem in event_elements:
            try:
                # Başlık
                title_elem = event_elem.select_one('h2, h3, .event-title')
                title = title_elem.text.strip() if title_elem else "Başlık bulunamadı"
                
                # URL
                url_elem = title_elem.find('a') if title_elem else None
                url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
                
                # Etkinlik detaylarını çek
                event_details = {}
                if url:
                    event_details = get_iccmr_event_details(url)
                
                # Tarih
                date_elem = event_elem.select_one('.event-date, .date')
                date_text = date_elem.text.strip() if date_elem else ""
                
                start_date = event_details.get('start_date', '')
                end_date = event_details.get('end_date', '')
                
                if not start_date and date_text:
                    # Tarih formatını ayrıştırma
                    date_parts = date_text.split('-')
                    
                    if len(date_parts) > 1:
                        # Başlangıç ve bitiş tarihi var
                        try:
                            start_date_obj = parse_date(date_parts[0].strip())
                            end_date_obj = parse_date(date_parts[1].strip())
                            
                            start_date = start_date_obj.strftime('%Y-%m-%d') if start_date_obj else ""
                            end_date = end_date_obj.strftime('%Y-%m-%d') if end_date_obj else ""
                        except:
                            start_date = date_parts[0].strip()
                            end_date = date_parts[1].strip()
                    else:
                        # Sadece tek tarih var
                        try:
                            date_obj = parse_date(date_text)
                            start_date = date_obj.strftime('%Y-%m-%d') if date_obj else date_text
                        except:
                            start_date = date_text
                
                # Konum
                location = event_details.get('location', '')
                if not location:
                    location_elem = event_elem.select_one('.event-location, .location')
                    location = location_elem.text.strip() if location_elem else ""
                
                # Açıklama
                description = event_details.get('description', '')
                if not description:
                    desc_elem = event_elem.select_one('.event-description, .description')
                    description = desc_elem.text.strip() if desc_elem else ""
                
                # Organizatör
                organizer = event_details.get('organizer', 'International Congress on Complementary Medicine Research')
                
                event = TCMEvent(
                    title=title,
                    description=description,
                    event_type="conference",
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    organizer=organizer,
                    url=url,
                    registration_url=event_details.get('registration_url', ''),
                    source_name="ICCMR",
                    keywords=extract_keywords(title + " " + description)
                )
                
                results.append(event)
                logging.info(f"Etkinlik bulundu: {title}")
                
            except Exception as e:
                logging.error(f"Etkinlik ayrıştırma hatası: {str(e)}")
                continue
        
        logging.info(f"Toplam {len(results)} etkinlik bulundu.")
        return results
    
    except Exception as e:
        logging.error(f"ICCMR etkinlikleri çekilirken hata: {str(e)}")
        return []


def get_iccmr_event_details(url: str) -> Dict:
    """
    ICCMR etkinlik sayfasından detaylı bilgileri çeker
    
    Args:
        url: Etkinlik URL'si
        
    Returns:
        Etkinlik detaylarını içeren sözlük
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {}
        
        # Tarihler
        date_elem = soup.select_one('.event-date, .date-info')
        if date_elem:
            date_text = date_elem.text.strip()
            date_parts = date_text.split('-')
            
            if len(date_parts) > 1:
                try:
                    start_date_obj = parse_date(date_parts[0].strip())
                    end_date_obj = parse_date(date_parts[1].strip())
                    
                    details['start_date'] = start_date_obj.strftime('%Y-%m-%d') if start_date_obj else ""
                    details['end_date'] = end_date_obj.strftime('%Y-%m-%d') if end_date_obj else ""
                except:
                    details['start_date'] = date_parts[0].strip()
                    details['end_date'] = date_parts[1].strip()
            else:
                try:
                    date_obj = parse_date(date_text)
                    details['start_date'] = date_obj.strftime('%Y-%m-%d') if date_obj else date_text
                except:
                    details['start_date'] = date_text
        
        # Konum
        location_elem = soup.select_one('.event-location, .location-info')
        if location_elem:
            details['location'] = location_elem.text.strip()
        
        # Açıklama
        desc_elem = soup.select_one('.event-description, .description')
        if desc_elem:
            details['description'] = desc_elem.text.strip()
        
        # Organizatör
        org_elem = soup.select_one('.organizer, .host')
        if org_elem:
            details['organizer'] = org_elem.text.strip()
        
        # Kayıt URL'si
        reg_elem = soup.select_one('.register-button, a:contains("Register")')
        if reg_elem and 'href' in reg_elem.attrs:
            details['registration_url'] = reg_elem['href']
        
        return details
        
    except Exception as e:
        logging.error(f"Etkinlik detayları alınırken hata: {str(e)}")
        return {}


def scrape_tcm_education_from_aborm() -> List[TCMEducation]:
    """
    American Board of Oriental Reproductive Medicine (ABORM) eğitim programlarını çeker
    
    Returns:
        TCMEducation nesneleri listesi
    """
    base_url = "https://aborm.org/education/"
    
    logging.info(f"ABORM eğitim programları çekiliyor...")
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Eğitim programı bölümlerini bul
        program_elements = soup.select('.education-item, .course-item')
        
        results = []
        for program_elem in program_elements:
            try:
                # Başlık
                title_elem = program_elem.select_one('h2, h3, .course-title')
                title = title_elem.text.strip() if title_elem else "Başlık bulunamadı"
                
                # URL
                url_elem = title_elem.find('a') if title_elem else None
                url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
                
                # Açıklama
                desc_elem = program_elem.select_one('.course-description, .description')
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Program türü belirleme
                program_type = "course"  # Varsayılan
                if any(kw in title.lower() for kw in ['certification', 'sertifika']):
                    program_type = "certificate"
                elif any(kw in title.lower() for kw in ['degree', 'diploma']):
                    program_type = "degree"
                
                # Süre
                duration_elem = program_elem.select_one('.duration, .course-duration')
                duration = duration_elem.text.strip() if duration_elem else "Belirtilmemiş"
                
                # Kurum
                institution = "American Board of Oriental Reproductive Medicine"
                
                # Başlangıç tarihi
                date_elem = program_elem.select_one('.start-date, .course-date')
                start_date = date_elem.text.strip() if date_elem else ""
                
                # Konum
                location_elem = program_elem.select_one('.location, .course-location')
                location = location_elem.text.strip() if location_elem else ""
                
                # Sertifikasyon
                cert_elem = program_elem.select_one('.certification, .course-certification')
                certification = cert_elem.text.strip() if cert_elem else ""
                
                # Fiyat
                price_elem = program_elem.select_one('.price, .course-price')
                price = price_elem.text.strip() if price_elem else ""
                
                education = TCMEducation(
                    title=title,
                    description=description,
                    program_type=program_type,
                    duration=duration,
                    institution=institution,
                    start_date=start_date,
                    location=location,
                    url=url,
                    certification=certification,
                    price=price,
                    source_name="ABORM",
                    keywords=extract_keywords(title + " " + description)
                )
                
                results.append(education)
                logging.info(f"Eğitim programı bulundu: {title}")
                
            except Exception as e:
                logging.error(f"Eğitim programı ayrıştırma hatası: {str(e)}")
                continue
        
        logging.info(f"Toplam {len(results)} eğitim programı bulundu.")
        return results
    
    except Exception as e:
        logging.error(f"ABORM eğitim programları çekilirken hata: {str(e)}")
        return []


def parse_date(date_text: str) -> Optional[datetime]:
    """
    Tarih metnini datetime nesnesine dönüştürür
    
    Args:
        date_text: Tarih metni
        
    Returns:
        datetime nesnesi veya None
    """
    date_formats = [
        '%B %d, %Y',       # January 1, 2023
        '%d %B %Y',        # 1 January 2023
        '%Y-%m-%d',        # 2023-01-01
        '%d/%m/%Y',        # 01/01/2023
        '%m/%d/%Y',        # 01/01/2023
        '%d.%m.%Y',        # 01.01.2023
        '%Y/%m/%d',        # 2023/01/01
        '%b %d, %Y',       # Jan 1, 2023
        '%d %b %Y',        # 1 Jan 2023
        '%B %Y',           # January 2023
        '%b %Y',           # Jan 2023
        '%Y'               # 2023
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_text, fmt)
        except ValueError:
            continue
    
    return None


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
        'alternative medicine', 'holistic medicine', 'oriental medicine',
        'conference', 'seminar', 'workshop', 'course', 'education', 'training',
        'certification', 'degree', 'diploma', 'continuing education'
    ]
    
    found_keywords = []
    
    for keyword in tcm_keywords:
        if keyword in text.lower():
            found_keywords.append(keyword)
    
    return found_keywords


def save_events_and_education(events: List[TCMEvent], education_programs: List[TCMEducation], 
                             events_file: str, education_file: str) -> None:
    """
    Etkinlikleri ve eğitim programlarını JSON formatında kaydeder
    
    Args:
        events: TCMEvent nesneleri listesi
        education_programs: TCMEducation nesneleri listesi
        events_file: Etkinlikler için çıktı dosyası yolu
        education_file: Eğitim programları için çıktı dosyası yolu
    """
    try:
        # Etkinlikleri kaydet
        events_data = [event.to_dict() for event in events]
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Etkinlikler {events_file} dosyasına kaydedildi.")
        
        # Eğitim programlarını kaydet
        education_data = [program.to_dict() for program in education_programs]
        with open(education_file, 'w', encoding='utf-8') as f:
            json.dump(education_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Eğitim programları {education_file} dosyasına kaydedildi.")
        
    except Exception as e:
        logging.error(f"Veriler kaydedilirken hata: {str(e)}")


def scrape_all_events_and_education() -> tuple[List[TCMEvent], List[TCMEducation]]:
    """
    Tüm kaynaklardan etkinlikleri ve eğitim programlarını çeker
    
    Returns:
        (events, education_programs) şeklinde bir tuple
    """
    all_events = []
    all_education = []
    
    # TCM World Foundation etkinlikleri
    tcmworld_events = scrape_tcm_events_from_tcmworld()
    all_events.extend(tcmworld_events)
    
    # ICCMR etkinlikleri
    iccmr_events = scrape_tcm_events_from_iccmr()
    all_events.extend(iccmr_events)
    
    # ABORM eğitim programları
    aborm_education = scrape_tcm_education_from_aborm()
    all_education.extend(aborm_education)
    
    return all_events, all_education


if __name__ == "__main__":
    # Çıktı klasörünü oluştur
    output_dir = "tcm_content"
    os.makedirs(output_dir, exist_ok=True)
    
    # Tüm etkinlikleri ve eğitim programlarını çek
    events, education = scrape_all_events_and_education()
    
    # Kaydet
    save_events_and_education(
        events, 
        education,
        os.path.join(output_dir, "tcm_events.json"),
        os.path.join(output_dir, "tcm_education.json")
    )
    
    logging.info(f"Toplam {len(events)} etkinlik ve {len(education)} eğitim programı bulundu.")
