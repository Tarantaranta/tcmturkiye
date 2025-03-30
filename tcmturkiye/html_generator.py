"""
HTML Sayfası Oluşturma Modülü

Bu modül, toplanan içeriklerden HTML sayfaları oluşturur.
Her kategori için bir ana sayfa ve içerikler için detay sayfaları oluşturulur.
"""

import os
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import hashlib

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Sabit değişkenler
OUTPUT_DIR = "output"
CONTENT_DIR = os.path.join(OUTPUT_DIR, "content")
JSON_DIR = os.path.join(CONTENT_DIR, "json")
HTML_DIR = os.path.join(CONTENT_DIR, "html")

# Kategori bilgileri
CATEGORIES = {
    "research": {
        "name": "Araştırmalar",
        "description": "TCM ve akupunktur ile ilgili en güncel araştırma makaleleri",
        "icon": "fa-microscope",
        "color": "#4285F4"
    },
    "theory": {
        "name": "Teoriler",
        "description": "Geleneksel Çin Tıbbı'nın temel teorileri ve prensipleri",
        "icon": "fa-book",
        "color": "#EA4335"
    },
    "mechanism": {
        "name": "Mekanizmalar",
        "description": "TCM ve akupunkturun etki mekanizmaları",
        "icon": "fa-cogs",
        "color": "#FBBC05"
    },
    "clinical_case": {
        "name": "Klinik Vakalar",
        "description": "TCM ve akupunktur ile tedavi edilen vaka raporları",
        "icon": "fa-user-md",
        "color": "#34A853"
    },
    "event": {
        "name": "Etkinlikler",
        "description": "TCM ve akupunktur ile ilgili konferanslar, seminerler ve diğer etkinlikler",
        "icon": "fa-calendar-alt",
        "color": "#FF6D01"
    },
    "education": {
        "name": "Eğitimler",
        "description": "TCM ve akupunktur eğitim programları",
        "icon": "fa-graduation-cap",
        "color": "#46BDC6"
    }
}

def ensure_directories():
    """Gerekli dizinleri oluşturur"""
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(HTML_DIR, exist_ok=True)
    
    for category in CATEGORIES.keys():
        os.makedirs(os.path.join(HTML_DIR, category), exist_ok=True)
    
    logging.info(f"Dizinler oluşturuldu")


def generate_unique_id(content: Dict) -> str:
    """
    İçerik için benzersiz bir ID oluşturur
    
    Args:
        content: İçerik verisi
        
    Returns:
        Benzersiz ID
    """
    # İçeriğin başlığı ve kaynağı gibi değişmez bilgilerini kullan
    title = content.get('title', '')
    source = content.get('source_url', '') or content.get('url', '')
    
    # Benzersiz bir string oluştur
    unique_string = f"{title}_{source}"
    
    # MD5 hash oluştur (tam benzersizlik için)
    return hashlib.md5(unique_string.encode()).hexdigest()


def slugify(text: str) -> str:
    """
    Metni URL-dostu bir formata dönüştürür
    
    Args:
        text: Dönüştürülecek metin
        
    Returns:
        URL-dostu metin
    """
    # Türkçe karakterleri değiştir
    text = text.lower()
    text = text.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u')
    text = text.replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    
    # Alfanumerik olmayan karakterleri kaldır ve boşlukları tire ile değiştir
    text = re.sub(r'[^\w\s-]', '', text).strip()
    text = re.sub(r'[-\s]+', '-', text)
    
    return text


def read_json_content(file_path: str) -> Dict:
    """
    JSON dosyasından içerik okur
    
    Args:
        file_path: JSON dosyası yolu
        
    Returns:
        İçerik verisi
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"JSON dosyası okunurken hata: {str(e)}")
        return {}


def write_json_content(content: Dict, file_path: str) -> None:
    """
    İçeriği JSON dosyasına yazar
    
    Args:
        content: İçerik verisi
        file_path: JSON dosyası yolu
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        logging.info(f"JSON dosyası yazıldı: {file_path}")
    except Exception as e:
        logging.error(f"JSON dosyası yazılırken hata: {str(e)}")


def get_template(template_name: str) -> str:
    """
    HTML şablonunu okur
    
    Args:
        template_name: Şablon adı
        
    Returns:
        HTML şablonu
    """
    template_path = os.path.join("tcmturkiye", "templates", f"{template_name}.html")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Şablon dosyası okunurken hata: {str(e)}")
        return ""


def generate_category_page(category: str, items: List[Dict]) -> None:
    """
    Kategori sayfası oluşturur
    
    Args:
        category: Kategori adı
        items: İçerik öğeleri listesi
    """
    category_info = CATEGORIES.get(category, {})
    category_name = category_info.get('name', category.capitalize())
    category_desc = category_info.get('description', '')
    category_color = category_info.get('color', '#4285F4')
    
    template = get_template("category_template")
    if not template:
        logging.error(f"Kategori şablonu bulunamadı")
        return
    
    # İçerik kartlarını oluştur
    content_cards = ""
    for item in items:
        item_id = item.get('id', generate_unique_id(item))
        item_title = item.get('title', 'Başlıksız')
        item_desc = item.get('content', '') or item.get('description', '')
        if len(item_desc) > 150:
            item_desc = item_desc[:150] + "..."
        
        item_date = item.get('publication_date', '') or item.get('start_date', '')
        item_source = item.get('source_name', '')
        item_url = f"{category}/{item_id}.html"
        
        card_template = get_template("card_template")
        if card_template:
            card = card_template.replace("{{item_title}}", item_title)
            card = card.replace("{{item_desc}}", item_desc)
            card = card.replace("{{item_date}}", item_date)
            card = card.replace("{{item_source}}", item_source)
            card = card.replace("{{item_url}}", item_url)
            card = card.replace("{{category_color}}", category_color)
            content_cards += card
    
    # Şablonu doldur
    html_content = template.replace("{{category_name}}", category_name)
    html_content = html_content.replace("{{category_desc}}", category_desc)
    html_content = html_content.replace("{{content_cards}}", content_cards)
    html_content = html_content.replace("{{category_color}}", category_color)
    
    # Aktif kategoriyi işaretle
    for cat in CATEGORIES.keys():
        if cat == category:
            html_content = html_content.replace(f"{{{{active_{cat}}}}}", "active")
        else:
            html_content = html_content.replace(f"{{{{active_{cat}}}}}", "")
    
    # Sayfayı kaydet
    output_path = os.path.join(HTML_DIR, category, "index.html")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Kategori sayfası oluşturuldu: {output_path}")
    except Exception as e:
        logging.error(f"Kategori sayfası oluşturulurken hata: {str(e)}")


def generate_detail_page(category: str, item: Dict) -> None:
    """
    Detay sayfası oluşturur
    
    Args:
        category: Kategori adı
        item: İçerik öğesi
    """
    category_info = CATEGORIES.get(category, {})
    category_name = category_info.get('name', category.capitalize())
    category_color = category_info.get('color', '#4285F4')
    
    template = get_template("detail_template")
    if not template:
        logging.error(f"Detay şablonu bulunamadı")
        return
    
    item_id = item.get('id', generate_unique_id(item))
    item_title = item.get('title', 'Başlıksız')
    item_content = item.get('content', '') or item.get('description', '')
    item_date = item.get('publication_date', '') or item.get('start_date', '')
    item_source = item.get('source_name', '')
    item_source_url = item.get('source_url', '') or item.get('url', '')
    item_author = item.get('author', '') or ', '.join(item.get('authors', []))
    
    # Kategori özel alanları
    additional_content = ""
    if category == "clinical_case":
        patient_info = item.get('patient_info', '')
        diagnosis = item.get('diagnosis', '')
        treatment = item.get('treatment', '')
        outcome = item.get('outcome', '')
        
        if patient_info:
            additional_content += f"<h3>Hasta Bilgileri</h3><p>{patient_info}</p>"
        if diagnosis:
            additional_content += f"<h3>Tanı</h3><p>{diagnosis}</p>"
        if treatment:
            additional_content += f"<h3>Tedavi</h3><p>{treatment}</p>"
        if outcome:
            additional_content += f"<h3>Sonuç</h3><p>{outcome}</p>"
    
    elif category == "event":
        location = item.get('location', '')
        end_date = item.get('end_date', '')
        organizer = item.get('organizer', '')
        registration_url = item.get('registration_url', '')
        
        if location:
            additional_content += f"<p><strong>Konum:</strong> {location}</p>"
        if end_date:
            additional_content += f"<p><strong>Bitiş Tarihi:</strong> {end_date}</p>"
        if organizer:
            additional_content += f"<p><strong>Organizatör:</strong> {organizer}</p>"
        if registration_url:
            additional_content += f'<p><a href="{registration_url}" target="_blank" class="btn" style="background-color: {category_color}; color: white;">Kayıt Ol</a></p>'
    
    elif category == "education":
        institution = item.get('institution', '')
        duration = item.get('duration', '')
        location = item.get('location', '')
        certification = item.get('certification', '')
        price = item.get('price', '')
        
        if institution:
            additional_content += f"<p><strong>Kurum:</strong> {institution}</p>"
        if duration:
            additional_content += f"<p><strong>Süre:</strong> {duration}</p>"
        if location:
            additional_content += f"<p><strong>Konum:</strong> {location}</p>"
        if certification:
            additional_content += f"<p><strong>Sertifikasyon:</strong> {certification}</p>"
        if price:
            additional_content += f"<p><strong>Ücret:</strong> {price}</p>"
    
    # Referanslar
    references = item.get('references', [])
    if references:
        additional_content += "<h3>Referanslar</h3><ul>"
        for ref in references:
            additional_content += f"<li>{ref}</li>"
        additional_content += "</ul>"
    
    # Şablonu doldur
    html_content = template.replace("{{category_name}}", category_name)
    html_content = html_content.replace("{{item_title}}", item_title)
    html_content = html_content.replace("{{item_content}}", item_content)
    html_content = html_content.replace("{{item_date}}", item_date)
    html_content = html_content.replace("{{item_source}}", item_source)
    html_content = html_content.replace("{{item_source_url}}", item_source_url)
    html_content = html_content.replace("{{item_author}}", item_author)
    html_content = html_content.replace("{{additional_content}}", additional_content)
    html_content = html_content.replace("{{category_color}}", category_color)
    html_content = html_content.replace("{{category_url}}", f"/{category}")
    
    # Aktif kategoriyi işaretle
    for cat in CATEGORIES.keys():
        if cat == category:
            html_content = html_content.replace(f"{{{{active_{cat}}}}}", "active")
        else:
            html_content = html_content.replace(f"{{{{active_{cat}}}}}", "")
    
    # Sayfayı kaydet
    output_path = os.path.join(HTML_DIR, category, f"{item_id}.html")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Detay sayfası oluşturuldu: {output_path}")
    except Exception as e:
        logging.error(f"Detay sayfası oluşturulurken hata: {str(e)}")


def update_content_tracking(category: str, items: List[Dict]) -> List[Dict]:
    """
    İçerik takip dosyasını günceller ve yeni içerikleri döndürür
    
    Args:
        category: Kategori adı
        items: Yeni içerik öğeleri listesi
        
    Returns:
        Yeni içerik öğeleri listesi (ID'ler eklenmiş)
    """
    tracking_file = os.path.join(JSON_DIR, f"{category}_tracking.json")
    
    # Mevcut takip verilerini oku
    tracking_data = {}
    if os.path.exists(tracking_file):
        tracking_data = read_json_content(tracking_file)
    
    tracked_items = tracking_data.get('items', {})
    
    # Yeni öğeleri işle
    updated_items = []
    for item in items:
        item_id = generate_unique_id(item)
        
        # Öğe daha önce işlendi mi kontrol et
        if item_id in tracked_items:
            # Öğe zaten var, güncelleme gerekiyorsa yap
            continue
        
        # Yeni öğe, takip verilerine ekle
        item['id'] = item_id
        tracked_items[item_id] = {
            'title': item.get('title', ''),
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': item.get('source_name', '')
        }
        
        updated_items.append(item)
    
    # Takip verilerini güncelle
    tracking_data['items'] = tracked_items
    tracking_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tracking_data['count'] = len(tracked_items)
    
    # Takip dosyasını kaydet
    write_json_content(tracking_data, tracking_file)
    
    return updated_items


def process_content_for_category(category: str, content_file: str) -> None:
    """
    Belirli bir kategori için içerikleri işler ve HTML sayfaları oluşturur
    
    Args:
        category: Kategori adı
        content_file: İçerik dosyası adı
    """
    file_path = os.path.join(JSON_DIR, content_file)
    if not os.path.exists(file_path):
        logging.warning(f"İçerik dosyası bulunamadı: {file_path}")
        return
    
    # İçeriği oku
    content_data = read_json_content(file_path)
    
    # İçerik türüne göre öğeleri al
    items = []
    if category == "research":
        items = content_data.get('articles', [])
    elif category == "theory":
        items = content_data.get('theories', [])
    elif category == "mechanism":
        items = content_data.get('mechanisms', [])
    elif category == "clinical_case":
        items = content_data.get('cases', [])
    elif category == "event":
        items = content_data.get('events', [])
    elif category == "education":
        items = content_data.get('education', [])
    
    # Yeni içerikleri işle
    new_items = update_content_tracking(category, items)
    
    if new_items:
        logging.info(f"{category} kategorisinde {len(new_items)} yeni içerik bulundu.")
        
        # Her yeni içerik için detay sayfası oluştur
        for item in new_items:
            generate_detail_page(category, item)
        
        # Kategori sayfasını güncelle (tüm içeriklerle)
        tracking_file = os.path.join(JSON_DIR, f"{category}_tracking.json")
        if os.path.exists(tracking_file):
            tracking_data = read_json_content(tracking_file)
            tracked_items = tracking_data.get('items', {})
            
            # Tüm izlenen öğeleri al
            all_items = []
            for item_id, item_info in tracked_items.items():
                # İçerik dosyasından tam öğeyi bul
                full_item = next((item for item in items if generate_unique_id(item) == item_id), None)
                if full_item:
                    full_item['id'] = item_id
                    all_items.append(full_item)
            
            # Kategori sayfasını oluştur
            generate_category_page(category, all_items)
    else:
        logging.info(f"{category} kategorisinde yeni içerik bulunamadı.")


def generate_html_pages() -> None:
    """Tüm kategoriler için HTML sayfaları oluşturur"""
    ensure_directories()
    
    # Kategori sayfalarını oluştur
    process_content_for_category("research", "research_content.json")
    process_content_for_category("theory", "theory_content.json")
    process_content_for_category("mechanism", "mechanism_content.json")
    process_content_for_category("clinical_case", "clinical_case_content.json")
    process_content_for_category("event", "event_content.json")
    process_content_for_category("education", "education_content.json")
    
    # Ana sayfayı güncelle
    update_index_page()
    
    logging.info("HTML sayfaları oluşturuldu.")


def update_index_page() -> None:
    """Ana sayfayı günceller"""
    template = get_template("index_template")
    if not template:
        logging.error("Ana sayfa şablonu bulunamadı")
        return
    
    # Kategori kartlarını oluştur
    category_cards = ""
    for category_key, category_info in CATEGORIES.items():
        card_template = get_template("category_card_template")
        if card_template:
            card = card_template.replace("{{category_name}}", category_info['name'])
            card = card.replace("{{category_desc}}", category_info['description'])
            card = card.replace("{{category_url}}", f"content/html/{category_key}")
            card = card.replace("{{category_icon}}", category_info['icon'])
            card = card.replace("{{category_color}}", category_info['color'])
            category_cards += card
    
    # Şablonu doldur
    html_content = template.replace("{{category_cards}}", category_cards)
    
    # Son güncelleme bilgisini ekle
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html_content = html_content.replace("{{last_updated}}", now)
    
    # Ana sayfayı kaydet
    output_path = os.path.join(OUTPUT_DIR, "index.html")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Ana sayfa güncellendi: {output_path}")
    except Exception as e:
        logging.error(f"Ana sayfa güncellenirken hata: {str(e)}")


def copy_static_files() -> None:
    """Statik dosyaları kopyalar"""
    static_src = os.path.join("tcmturkiye", "templates", "static")
    static_dest = os.path.join(OUTPUT_DIR, "static")
    
    if os.path.exists(static_src):
        if os.path.exists(static_dest):
            shutil.rmtree(static_dest)
        
        shutil.copytree(static_src, static_dest)
        logging.info(f"Statik dosyalar kopyalandı: {static_dest}")
    else:
        logging.warning(f"Statik dosyalar bulunamadı: {static_src}")


class HTMLGenerator:
    """HTML sayfaları oluşturmak için kullanılan sınıf"""
    
    def __init__(self):
        """HTMLGenerator sınıfını başlatır"""
        # Gerekli dizinlerin var olduğundan emin ol
        ensure_directories()
    
    def generate_all_pages(self):
        """Tüm HTML sayfalarını oluşturur"""
        logging.info("Tüm HTML sayfaları oluşturuluyor...")
        
        try:
            # Tüm kategoriler için HTML sayfalarını oluştur
            generate_html_pages()
            
            # Ana sayfayı güncelle
            update_index_page()
            
            # Statik dosyaları kopyala
            copy_static_files()
            
            logging.info("HTML sayfaları başarıyla oluşturuldu.")
            
        except Exception as e:
            logging.error(f"HTML sayfaları oluşturulurken hata: {str(e)}")
            raise


if __name__ == "__main__":
    generator = HTMLGenerator()
    generator.generate_all_pages()
