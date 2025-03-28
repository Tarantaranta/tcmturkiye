from pathlib import Path

def generate_index_html(output_dir="output"):
    md_files = sorted(Path(output_dir).glob("*.md"))

    html_content = [
        "<!DOCTYPE html>",
        "<html lang='tr'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<title>TCM Türkiye Makaleleri</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 2rem; }",
        "h1 { color: #2e3d49; }",
        "ul { list-style-type: none; padding: 0; }",
        "li { margin-bottom: 1rem; }",
        "a { text-decoration: none; color: #007acc; font-weight: bold; }",
        "a:hover { text-decoration: underline; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Yayınlanan Makaleler</h1><ul>"
    ]

    for file in md_files:
        html_content.append(f'<li><a href="{file.name}">{file.name}</a></li>')

    html_content.append("</ul></body></html>")

    with open(Path(output_dir) / "index.html", "w") as f:
        f.write("\n".join(html_content))

if __name__ == "__main__":
    generate_index_html()