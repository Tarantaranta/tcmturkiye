import subprocess
import sys
import os

# index.html otomatik oluşturulsun
print("🔄 index.html güncelleniyor...")
os.system(f"{sys.executable} tcmturkiye/generate_index.py")

# HTTP sunucu başlatılsın
print("🚀 HTTP sunucusu başlatılıyor: http://localhost:8000")
subprocess.run([sys.executable, "-m", "http.server", "--directory", "output"])