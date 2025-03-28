"""
Bu modül, içerikleri Markdown formatında oluşturur ve kaydeder.
"""

import os
from datetime import datetime

def generate_markdown(
    title: str,
    authors: list,
    abstract: str,
    summary: str,
    summary_en: str,
    commentary: str,
    commentary_en: str,
    image_path: str,
    categories: list,
    pubmed_url: str = "",
    image_url: str = ""
) -> str:
    content = f"# {title}\n\n"
    content += f"**Yazarlar:** {', '.join(authors)}\n\n"
    content += "## 🧬 Özet (Makale)\n"
    content += f"{abstract}\n\n"
    content += "## 🧬 Summary (English)\n"
    content += f"{summary_en}\n\n"
    content += "## 💬 Bilimsel Yorum\n"
    content += f"{commentary}\n\n"
    content += "## 💬 Commentary (English)\n"
    content += f"{commentary_en}\n\n"
    if image_url:
        content += "## 🖼️ İlgili Görsel\n"
        content += f"![Görsel]({image_url})\n\n"
    elif image_path:
        content += "## 🖼️ İlgili Görsel\n"
        content += f"![Görsel]({image_path})\n\n"
    if pubmed_url:
        content += f"[PubMed'de Görüntüle]({pubmed_url})\n\n"
    if categories:
        content += "## 🗂️ Kategoriler\n"
        content += ", ".join(f"`{cat}`" for cat in categories) + "\n\n"
        content += "**Etiketler:** " + ", ".join(f"`{cat.lower().replace(' ', '_')}`" for cat in categories) + "\n"
    return content

def save_markdown(article: dict, summary: str, output_dir: str = "output"):
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{sanitize_filename(article['title'])}.md"
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {article['title']}\n\n")
        f.write(f"**Yazarlar:** {', '.join(article['authors'])}\n\n")
        f.write("## 🧬 Özet (Makale)\n")
        f.write(f"{article['abstract']}\n\n")
        if "summary_en" in article:  # English summary follows the Turkish summary
            f.write("## 🧬 Summary (English)\n")
            f.write(f"{article['summary_en']}\n\n")
        if "commentary" in article:
            f.write("## 💬 Bilimsel Yorum\n")
            f.write(f"{article['commentary']}\n\n")
            if "commentary_en" in article:
                f.write("## 💬 Commentary (English)\n")
                f.write(f"{article['commentary_en']}\n\n")
        if "image_path" in article:
            image_rel_path = os.path.relpath(article["image_path"], output_dir)
            f.write("## 🖼️ İlgili Görsel\n")
            f.write(f"![Görsel]({image_rel_path})\n\n")
        if "pubmed_url" in article:
            f.write(f"[PubMed'de Görüntüle]({article['pubmed_url']})\n")
        else:
            f.write("[PubMed'de Görüntüle](https://pubmed.ncbi.nlm.nih.gov/)\n")
        if "categories" in article:
            f.write("## 🗂️ Kategoriler\n")
            f.write(", ".join(f"`{cat}`" for cat in article["categories"]))
            f.write("\n\n")
            f.write("**Etiketler:** ")
            f.write(", ".join(f"`{cat.lower().replace(' ', '_')}`" for cat in article["categories"]))
            f.write("\n")

    print(f"Markdown dosyası oluşturuldu: {path}")


def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:100]

def build_markdown_content(
    title: str,
    authors: str,
    abstract: str,
    summary_tr: str,
    summary_en: str,
    commentary_tr: str,
    commentary_en: str,
    image_path: str,
    pubmed_url: str,
    categories: list,
    tags: list
) -> str:
    """
    Markdown içeriğini birleştirir.
    """
    content = f"# {title}\n\n"
    content += f"**Yazarlar:** {authors}\n\n"
    content += "## 🧬 Özet (Makale)\n"
    content += f"{abstract}\n\n"
    content += "## ✨ GPT Destekli Özet\n"
    content += f"**Türkçe:**\n\n{summary_tr}\n\n"
    content += f"**English:**\n\n{summary_en}\n\n"
    content += "## 🧠 Bilimsel Yorum\n"
    content += f"**Türkçe:**\n\n{commentary_tr}\n\n"
    content += f"**English:**\n\n{commentary_en}\n\n"
    content += f"![Görsel]({image_path})\n\n"
    content += "## 🔗 Kaynak\n"
    content += f"[PubMed'de Görüntüle]({pubmed_url})\n\n"
    content += "## 🗂️ Kategoriler\n"
    content += ", ".join(f"`{cat}`" for cat in categories) + "\n\n"
    content += "**Etiketler:** " + ", ".join(f"`{tag}`" for tag in tags) + "\n"
    return content
