import os
from datetime import datetime

OUTPUT_DIR = "output"
INDEX_FILE = os.path.join(OUTPUT_DIR, "index.html")

def generate_index():
    md_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md")]
    md_files.sort(reverse=True)

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Language" content="tr">
    <title>TCM Türkiye - Bilimsel İçerikler</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 2rem; background: #f9f9f9; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { background: white; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }
        a { text-decoration: none; color: #007acc; }
    </style>
</head>
<body>
    <h1>📚 TCM Türkiye - Scientific Articles</h1>
    <ul>
"""

    for md_file in md_files:
        filename = os.path.basename(md_file)
        date_str = filename.split("_")[0]
        try:
            formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %B %Y")
        except ValueError:
            formatted_date = date_str

        html_content += f'        <li><a href="{filename}" target="_blank">{formatted_date} - {filename}</a></li>\n'

    html_content += """    </ul>
</body>
</html>
"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ index.html başarıyla güncellendi: {INDEX_FILE}")

if __name__ == "__main__":
    generate_index()