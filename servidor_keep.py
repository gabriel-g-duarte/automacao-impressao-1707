import os
import sys
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

def obter_diretorio_real():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    if "temp" in caminho_script.lower() or "appdata" in caminho_script.lower():
        return os.getcwd()
    return caminho_script

DIRETORIO_ATUAL = obter_diretorio_real()

@app.after_request
def aplicar_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/codigos", methods=["POST", "OPTIONS"])
def receber_codigos():
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200

    try:
        dados = request.get_json(force=True, silent=True) or {}
        texto = dados.get("texto", "").strip()

        if texto:
            # Obtém a pasta configurada do config.json
            caminho_config = os.path.join(DIRETORIO_ATUAL, "config.json")
            pasta_destino = DIRETORIO_ATUAL
            
            if os.path.exists(caminho_config):
                try:
                    with open(caminho_config, "r", encoding="utf-8-sig") as f:
                        cfg = json.load(f)
                        pasta_destino = cfg.get("PASTA_AUTOMACAO", DIRETORIO_ATUAL)
                except Exception:
                    pass

            caminho_csv = os.path.join(pasta_destino, "codigos.csv")

            # Escreve o arquivo codigos.csv na pasta
            with open(caminho_csv, "w", encoding="utf-8") as f:
                f.write(texto + "\n")

            return jsonify({"status": "SUCCESS", "mensagem": "Códigos salvos com sucesso!"}), 200
        else:
            return jsonify({"status": "ERROR", "mensagem": "Nenhum texto recebido."}), 400

    except Exception as e:
        return jsonify({"status": "ERROR", "mensagem": str(e)}), 500

@app.route("/shutdown", methods=["POST"])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()
    return jsonify({"status": "desligado"}), 200

def iniciar():
    # Executa o servidor Flask na porta 5000 sem logs excessivos no terminal
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    iniciar()