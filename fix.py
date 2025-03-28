import os

# GitHub Actions workflow içeriği
workflow_content = """name: Günlük İçerik Üretimi

on:
  schedule:
    - cron: '0 6 * * *'  # UTC 06:00 = Türkiye saatiyle 09:00
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Kodları çek
      uses: actions/checkout@v3

    - name: Python ortamını kur
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Bağımlılıkları yükle
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: İçerik üretimini çalıştır
      run: python -m tcmturkiye.tcmturkiye
"""

# Dosya yolu
workflow_dir = ".github/workflows"
workflow_file = os.path.join(workflow_dir, "daily-content.yml")

# Klasörleri oluştur
os.makedirs(workflow_dir, exist_ok=True)

# Dosyayı yaz
with open(workflow_file, "w", encoding="utf-8") as f:
    f.write(workflow_content)

print(f"{workflow_file} başarıyla oluşturuldu.")
