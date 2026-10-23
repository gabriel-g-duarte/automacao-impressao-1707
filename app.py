import json
import os
import sys
import time
import ctypes
import threading
import subprocess
import webview

# Importa o seu módulo do servidor Keep
try:
    import servidor_keep
except ImportError:
    servidor_keep = None

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def obter_posicao_mouse():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def obter_diretorio_real():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    if "temp" in caminho_script.lower() or "appdata" in caminho_script.lower():
        return os.getcwd()
    return caminho_script

DIRETORIO_ATUAL = obter_diretorio_real()
CONFIG_FILE = os.path.join(DIRETORIO_ATUAL, "config.json")

DEFAULTS_CONFIG = {
    "PASTA_AUTOMACAO": DIRETORIO_ATUAL,
    "PASTA_RELATORIO_FALTAS": DIRETORIO_ATUAL,
    "NOME_IMPRESSORA": "WMS2",
    "CampoCodigo_X": 2255, "CampoCodigo_Y": 76,
    "BotaoImprimir2_X": 1937, "BotaoImprimir2_Y": 35,
    "BotaoTrocarImpressora_X": 2773, "BotaoTrocarImpressora_Y": 314,
    "ImpressoraWMS2_X": 2822, "ImpressoraWMS2_Y": 448,
    "BotaoOK_X": 2996, "BotaoOK_Y": 657,
    "BotaoOK_Informacao_X": 2883, "BotaoOK_Informacao_Y": 554,
    "BotaoOK_Atencao_X": 2874, "BotaoOK_Atencao_Y": 550,
    "BotaoImprimirUniversal_X": 880, "BotaoImprimirUniversal_Y": 404,
    "BotaoFechar_X": 2410, "BotaoFechar_Y": 35
}

class ApiBridge:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def selecionar_pasta(self):
        if self._window:
            result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
            if result and len(result) > 0:
                return result[0]
        return ""

    def carregar_config(self):
        config = DEFAULTS_CONFIG.copy()
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
                    config.update(json.load(f))
            except Exception as e:
                print(f"Erro ao ler JSON: {e}")
        return config

    def salvar_config(self, config_data):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return {"ok": True, "msg": "Configurações salvas permanentemente!"}
        except Exception as e:
            return {"ok": False, "msg": f"Erro ao salvar: {e}"}

    def iniciar_tudo(self):
        if servidor_keep and hasattr(servidor_keep, 'iniciar'):
            # Roda a função de início do servidor Keep em uma thread separada
            threading.Thread(target=servidor_keep.iniciar, daemon=True).start()
            return {"ok": True, "msg": "Servidor Keep INICIADO com sucesso!"}
        elif servidor_keep:
            return {"ok": True, "msg": "Módulo servidor_keep carregado."}
        return {"ok": False, "msg": "Arquivo servidor_keep.py não encontrado no projeto."}

    def encerrar_tudo(self):
        CREATE_NO_WINDOW = 0x08000000
        subprocess.call('taskkill /f /im AutoHotkey.exe', creationflags=CREATE_NO_WINDOW)
        subprocess.call('taskkill /f /im AutoHotkey64.exe', creationflags=CREATE_NO_WINDOW)
        subprocess.call('taskkill /f /im AutoHotkey32.exe', creationflags=CREATE_NO_WINDOW)
        return {"ok": True, "msg": "Processos ENCERRADOS com sucesso."}

    def abrir_script_ahk(self):
        script_path = None
        for arquivo in os.listdir(DIRETORIO_ATUAL):
            if arquivo.endswith(".ahk"):
                script_path = os.path.join(DIRETORIO_ATUAL, arquivo)
                break
        
        if script_path and os.path.exists(script_path):
            os.startfile(script_path)
            return {"ok": True, "msg": f"Script {os.path.basename(script_path)} aberto."}
            
        return {"ok": False, "msg": "Nenhum arquivo .ahk encontrado na pasta."}

    def capturar_coordenada(self, chave_base):
        if self._window:
            self._window.minimize()

        def escutar():
            while ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000:
                time.sleep(0.05)
            while True:
                if ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000:
                    x, y = obter_posicao_mouse()
                    break
                time.sleep(0.02)
            
            if self._window:
                self._window.restore()
                self._window.evaluate_js(f"atualizarCoordenadaCapturada('{chave_base}', {x}, {y})")

        threading.Thread(target=escutar, daemon=True).start()
        return {"ok": True}

if __name__ == "__main__":
    api = ApiBridge()
    window = webview.create_window(
        title="AUT_1707",
        url="index.html",
        width=950,
        height=800,
        resizable=False,
        js_api=api
    )
    api.set_window(window)
    webview.start()