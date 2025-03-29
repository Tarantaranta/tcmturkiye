import os
from datetime import datetime

def generate_index(language="tr"):
    """
    Airbnb benzeri modern, responsive ve arama/filtre destekli büyük bir HTML sayfa üretir.
    language='tr' veya 'en' olarak çağrıldığında, ilgili klasörde index dosyası oluşturur.
    """
    output_dir = os.path.join("output", language)
    os.makedirs(output_dir, exist_ok=True)
    index_file = os.path.join(output_dir, f"index-{language}.html")

    # .md dosyalarını toplayalım
    md_files = [f for f in os.listdir(output_dir) if f.endswith(".md")]
    md_files.sort(reverse=True)

    # Çeviriler ve metinler
    site_title         = "TCM Türkiye - Makale Listesi" if language == "tr" else "TCM Türkiye - Article List"
    heading_text       = "Türkçe Makaleler" if language == "tr" else "English Articles"
    placeholder_search = "Makalelerde Ara..." if language == "tr" else "Search in articles..."
    nav_home           = "Anasayfa" if language == "tr" else "Home"
    nav_about          = "Hakkında" if language == "tr" else "About"
    nav_contact        = "İletişim" if language == "tr" else "Contact"
    nav_toggle_lang    = "EN" if language == "tr" else "TR"

    # HTML başlangıcı – Airbnb tarzı modern tasarım
    html_content = f"""<!DOCTYPE html>
<html lang="{language}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{site_title}</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: 'Helvetica Neue', Arial, sans-serif;
      background: #f8f8f8;
      color: #333;
    }}
    header {{
      background: #ffffff;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      padding: 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .logo {{
      font-size: 1.3rem;
      font-weight: bold;
      color: #ff385c;
      text-decoration: none;
    }}
    nav a {{
      margin: 0 1rem;
      text-decoration: none;
      color: #333;
      font-weight: 500;
    }}
    nav a:hover {{
      color: #ff385c;
    }}
    .container {{
      max-width: 1200px;
      margin: 2rem auto;
      padding: 0 1rem;
    }}
    h1 {{
      margin-bottom: 1rem;
    }}
    .search-bar {{
      text-align: center;
      margin-bottom: 2rem;
    }}
    #searchInput {{
      width: 100%;
      max-width: 500px;
      padding: 0.8rem;
      border: 1px solid #ccc;
      border-radius: 8px;
      font-size: 1rem;
      outline: none;
    }}
    #searchInput:focus {{
      border-color: #ff385c;
      box-shadow: 0 0 3px rgba(255,56,92,0.3);
    }}
    .filter-buttons {{
      text-align: center;
      margin-bottom: 1.5rem;
    }}
    .filter-buttons button {{
      display: inline-block;
      margin: 0.2rem;
      padding: 0.5rem 1rem;
      font-size: 0.9rem;
      border: none;
      border-radius: 20px;
      background: #eee;
      cursor: pointer;
      transition: background 0.2s;
    }}
    .filter-buttons button:hover {{
      background: #ff385c;
      color: white;
    }}
    .articles {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }}
    .article-card {{
      background: #fff;
      border-radius: 10px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      padding: 1rem;
      transition: transform 0.2s ease;
    }}
    .article-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }}
    .article-title {{
      font-size: 1rem;
      margin-bottom: 0.5rem;
      color: #333;
      text-decoration: none;
      font-weight: 600;
      display: block;
      word-break: break-all;
    }}
    .article-title:hover {{
      color: #ff385c;
    }}
    .article-date {{
      font-size: 0.85rem;
      color: #555;
      margin-bottom: 1rem;
    }}
    @media (max-width: 600px) {{
      .articles {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <a href="#" class="logo">TCMTürkiye</a>
    <nav>
      <a href="#home">{nav_home}</a>
      <a href="#about">{nav_about}</a>
      <a href="#contact">{nav_contact}</a>
      <!-- Dil geçişi için basit link (bu, dil değişimini sağlamak üzere güncellenebilir) -->
      <a href="../{'en' if language=='tr' else 'tr'}/index-{'en' if language=='tr' else 'tr'}.html">{nav_toggle_lang}</a>
    </nav>
  </header>

  <div class="container">
    <h1>{heading_text}</h1>

    <!-- Arama Kutusu -->
    <div class="search-bar">
      <input
        type="text"
        id="searchInput"
        placeholder="{placeholder_search}"
        onkeyup="filterArticlesBySearch()"
      />
    </div>

    <!-- Kategori Butonları -->
    <div class="filter-buttons">
      <button onclick="filterByCat('all')">Tümü</button>
      <button onclick="filterByCat('Bilimsel')">Bilimsel</button>
      <button onclick="filterByCat('Mekanizma')">Mekanizma</button>
      <button onclick="filterByCat('Hastalık')">Hastalık</button>
      <button onclick="filterByCat('Teknik')">Teknik</button>
    </div>

    <!-- Makale Kartları -->
    <div class="articles" id="articleList">
"""

    def guess_category_from_filename(fname: str) -> str:
        lowerf = fname.lower()
        cats = []
        if "mechanistic" in lowerf or "theory" in lowerf:
            cats.append("Mekanizma")
        if "migraine" in lowerf or "fibromy" in lowerf:
            cats.append("Hastalık")
        if "improve" in lowerf or "meta" in lowerf or "study" in lowerf:
            cats.append("Bilimsel")
        if "tech" in lowerf or "electro" in lowerf:
            cats.append("Teknik")
        if not cats:
            cats.append("Bilimsel")
        return ",".join(cats)

    for md_file in md_files:
        filename = os.path.basename(md_file)
        date_str = filename.split("_")[0]
        try:
            formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %B %Y")
        except ValueError:
            formatted_date = date_str

        # Linki viewer.html üzerinden açmak için (NOT: index dosyası /output/tr/ olduğundan bir üst klasöre çıkmak için "../" kullanın)
        link = f"../viewer.html?file={language}/{filename}"
        cat_str = guess_category_from_filename(filename)

        html_content += f"""      <div class="article-card" data-cat="{cat_str}">
        <a href="{link}" class="article-title" target="_blank">{filename}</a>
        <div class="article-date">{formatted_date}</div>
      </div>
"""

    html_content += """
    </div>
  </div>

  <script>
    function filterArticlesBySearch() {
      var input = document.getElementById('searchInput').value.toUpperCase();
      var articleList = document.getElementById('articleList');
      var cards = articleList.getElementsByClassName('article-card');
      for (var i = 0; i < cards.length; i++) {
        var title = cards[i].getElementsByClassName('article-title')[0];
        var txtValue = title.textContent || title.innerText;
        if (txtValue.toUpperCase().indexOf(input) > -1) {
          cards[i].style.display = '';
        } else {
          cards[i].style.display = 'none';
        }
      }
    }

    function filterByCat(category) {
      var articleList = document.getElementById('articleList');
      var cards = articleList.getElementsByClassName('article-card');
      for (var i = 0; i < cards.length; i++) {
        var catVal = cards[i].getAttribute('data-cat') || '';
        if (category === 'all') {
          cards[i].style.display = '';
        } else {
          if (catVal.indexOf(category) > -1) {
            cards[i].style.display = '';
          } else {
            cards[i].style.display = 'none';
          }
        }
      }
    }
  </script>
</body>
</html>
"""

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ {index_file} başarıyla oluşturuldu.")

def generate_index_html():
    """
    Hem Türkçe (index-tr.html) hem de İngilizce (index-en.html) sayfalarını oluşturur.
    """
    generate_index("tr")
    generate_index("en")

if __name__ == "__main__":
    generate_index_html()