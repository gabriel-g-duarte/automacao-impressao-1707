import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def obter_caminho_codigos():
    """Lê dinamicamente a PASTA_AUTOMACAO no config.json"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                pasta = cfg.get("PASTA_AUTOMACAO", BASE_DIR)
                return os.path.join(pasta, "codigos.txt")
        except Exception:
            pass
    return os.path.join(BASE_DIR, "codigos.txt")

class KeepHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            codigos = data.get("texto", "")

            caminho_destino = obter_caminho_codigos()

            # Escreve o arquivo codigos.txt exclusivamente na PASTA_AUTOMACAO
            with open(caminho_destino, "w", encoding="utf-8") as f:
                f.write(codigos)

            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            res = json.dumps({"status": "SUCCESS", "arquivo": caminho_destino})
            self.wfile.write(res.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            res = json.dumps({"status": "ERROR", "error": str(e)})
            self.wfile.write(res.encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "online"}).encode('utf-8'))

    def log_message(self, format, *args):
        return

def run(port=8000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, KeepHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run()