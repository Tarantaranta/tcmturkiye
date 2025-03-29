import os

def generate_homepage_html():
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    index_file = os.path.join(output_dir, "index.html")

    html = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <title>TCMTürkiye Ana Sayfa</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #f9f9f9; color: #333; }
    header { background: #fff; padding: 1rem 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
    .logo { font-size: 1.5rem; font-weight: bold; color: #e63946; text-decoration: none; }
    nav a { margin-left: 1rem; color: #333; text-decoration: none; font-weight: 500; }
    nav a:hover { color: #e63946; }
    .hero { text-align: center; padding: 4rem 2rem; background: #fff0f0; }
    .hero h1 { font-size: 2.5rem; margin-bottom: 1rem; }
    .hero p { font-size: 1.2rem; margin-bottom: 2rem; }
    .lang-buttons a {
      display: inline-block; margin: 0 0.5rem; padding: 0.8rem 1.5rem; border-radius: 8px;
      background: #e63946; color: white; font-weight: bold; text-decoration: none;
    }
    .lang-buttons a:hover { background: #d62828; }
    footer { text-align: center; padding: 2rem; color: #888; font-size: 0.9rem; }
  </style>
</head>
<body>
  <header>
    <a class="logo" href="#">TCMTürkiye</a>
    <nav>
      <a href="#about">Hakkında</a>
      <a href="#contact">İletişim</a>
    </nav>
  </header>
  <section class="hero">
    <h1>Akupunktur ve TCM Bilgi Merkezi</h1>
    <p>Bilimsel araştırmalar, vaka sunumları ve teorik içerikler ile zenginleştirilmiş dijital arşiv</p>
    <div class="lang-buttons">
      <a href="tr/index-tr.html">Türkçe</a>
      <a href="en/index-en.html">English</a>
    </div>
  </section>
  <footer>
    &copy; 2025 TCMTürkiye. Tüm hakları saklıdır.
  </footer>
</body>
</html>
"""
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Ana sayfa index.html başarıyla oluşturuldu.")