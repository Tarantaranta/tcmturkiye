import os
import http.server
import socketserver

PORT = 8010
DIRECTORY = "output"

if __name__ == "__main__":
    # Burada sunucunun kök dizinini 'output' olarak ayarlıyoruz
    web_dir = os.path.join(os.path.dirname(__file__), "..", DIRECTORY)
    os.chdir(web_dir)
    print(f"Şu anki çalışma dizini: {os.getcwd()}")
    print(f"Sunucu dizini olarak ayarlandı: {web_dir}")

    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Yerel sunucu başlatıldı: http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Sunucu kapatılıyor...")
            httpd.server_close()