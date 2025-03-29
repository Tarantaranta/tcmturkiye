"""
PubMed XML verisini ayrıştırmak için yardımcı fonksiyonlar.
Amaç: Başlık, özet (abstract), yazar bilgileri gibi verileri almak.
"""

from typing import List, Dict
import xml.etree.ElementTree as ET

def parse_pubmed_xml(xml_data: str) -> List[Dict]:
    articles = []
    root = ET.fromstring(xml_data)
    for article in root.findall(".//PubmedArticle"):
        title_elem = article.find(".//ArticleTitle")
        abstract_elem = article.find(".//Abstract/AbstractText")
        author_list = article.findall(".//AuthorList/Author")

        title = title_elem.text if title_elem is not None else "Başlık yok"
        abstract = abstract_elem.text if abstract_elem is not None else "Özet bulunamadı"

        authors = []
        for author in author_list:
            last = author.findtext("LastName", "")
            first = author.findtext("ForeName", "")
            if last or first:
                authors.append(f"{first} {last}".strip())

        pmid_elem = article.find(".//PMID")
        pmid = pmid_elem.text.strip() if pmid_elem is not None and pmid_elem.text else "PMID bulunamadı"

        articles.append({
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "pmid": pmid
        })

    return articles