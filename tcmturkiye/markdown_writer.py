"""
Bu modül, içerikleri Markdown formatında oluşturur ve kaydeder.
"""

import os
from datetime import datetime

def save_markdown(article: dict, markdown_str: str, language: str, output_dir: str = "output"):
    import os
    from datetime import datetime

    # Dil klasörünü belirleyelim (tr veya en)
    lang_folder = os.path.join(output_dir, language)
    os.makedirs(lang_folder, exist_ok=True)

    # Türkçe için çevirilmiş başlığı, İngilizce için orijinal başlığı kullanın
    title_for_filename = article.get("title_tr", article["title"]) if language == "tr" else article["title"]

    filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{sanitize_filename(title_for_filename)}_{language}.md"
    path = os.path.join(lang_folder, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_str)

    print(f"Markdown dosyası oluşturuldu: {path}")

def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:100]

def build_markdown_content_tr(
    title: str,
    authors: list,
    abstract: str,
    summary_tr: str,
    commentary_tr: str,
    image_path: str,
    pubmed_url: str,
    categories: list,
    tags: list = []
) -> str:
    """
    Makalenin yalnızca Türkçe içeriğini oluşturur.
    """
    content = f"# {title}\n\n"
    content += f"**Yazarlar:** {', '.join(authors)}\n\n"
    content += "## 🧬 Özet (Makale)\n"
    content += f"{abstract}\n\n"
    content += "## ✨ GPT Destekli Özet (Türkçe)\n"
    content += f"{summary_tr}\n\n"
    content += "## 🧠 Bilimsel Yorum (Türkçe)\n"
    content += f"{commentary_tr}\n\n"
    if image_path:
        content += "## 🖼️ İlgili Görsel\n"
        content += f"![Görsel]({image_path})\n\n"
    if pubmed_url:
        content += "## 🔗 Kaynak\n"
        content += f"[PubMed'de Görüntüle]({pubmed_url})\n\n"
    if categories:
        content += "## 🗂️ Kategoriler\n"
        content += ", ".join(f"`{cat}`" for cat in categories) + "\n\n"
    if tags:
        content += "**Etiketler:** " + ", ".join(f"`{tag}`" for tag in tags) + "\n"
    return content

def build_markdown_content_en(
    title: str,
    authors: list,
    abstract: str,
    summary_en: str,
    commentary_en: str,
    image_path: str,
    pubmed_url: str,
    categories: list,
    tags: list = []
) -> str:
    """
    Makalenin yalnızca İngilizce içeriğini oluşturur.
    """
    content = f"# {title}\n\n"
    content += f"**Authors:** {', '.join(authors)}\n\n"
    content += "## 🧬 Abstract\n"
    content += f"{abstract}\n\n"
    content += "## ✨ GPT Supported Summary (English)\n"
    content += f"{summary_en}\n\n"
    content += "## 🧠 Scientific Commentary (English)\n"
    content += f"{commentary_en}\n\n"
    if image_path:
        content += "## 🖼️ Related Image\n"
        content += f"![Image]({image_path})\n\n"
    if pubmed_url:
        content += "## 🔗 Source\n"
        content += f"[View on PubMed]({pubmed_url})\n\n"
    if categories:
        content += "## 🗂️ Categories\n"
        content += ", ".join(f"`{cat}`" for cat in categories) + "\n\n"
    if tags:
        content += "**Tags:** " + ", ".join(f"`{tag}`" for tag in tags) + "\n"
    return content