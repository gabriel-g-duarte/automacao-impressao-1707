import json
import os
import sys
import time
import ctypes
import threading
import subprocess
import importlib
import urllib.request
import webview

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

if DIRETORIO_ATUAL not in sys.path:
    sys.path.insert(0, DIRETORIO_ATUAL)

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

def fechar_script_ahk_especifico(script_nome="impressao_1707.ahk"):
    """Encerra apenas as janelas do AutoHotkey cujo título/caminho contenha o nome do script especificado."""
    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    
    def enum_win_cb(hwnd, lparam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            if script_nome.lower() in buff.value.lower():
                # Envia mensagem WM_CLOSE (0x0010) para fechar o script AHK específico
                user32.PostMessageW(hwnd, 0x0010, 0, 0)
        return True

    user32.EnumWindows(WNDENUMPROC(enum_win_cb), 0)

class ApiBridge:
    def __init__(self):
        self._window = None
        self._monitor_window = None
        self._servidor_iniciado = False
        self._ultimo_status_valido = {"status": "aguardando", "total_processados": 0, "codigo_atual": "-"}

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

    def ler_status(self):
        user32 = ctypes.windll.user32
        data_encontrada = None

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def enum_win_cb(hwnd, lparam):
            nonlocal data_encontrada
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                val = buff.value
                if val.startswith("AUT1707_DATA|"):
                    data_encontrada = val
                    return False
            return True

        user32.EnumWindows(WNDENUMPROC(enum_win_cb), 0)

        if data_encontrada:
            try:
                partes = data_encontrada.split("|")
                st = partes[1]
                tot = int(partes[2]) if partes[2].isdigit() else 0
                cod = partes[3]
                msg = partes[4] if len(partes) > 4 else "none"
                tem_erro = (st == "erro" or msg != "none")

                res = {
                    "status": st,
                    "total_processados": tot,
                    "codigo_atual": cod,
                    "erro": tem_erro,
                    "codigo_erro": cod if tem_erro else "",
                    "mensagem_erro": msg if tem_erro and msg != "none" else ""
                }
                self._ultimo_status_valido = res
                return res
            except Exception:
                pass

        return self._ultimo_status_valido

    def ahk_esta_rodando(self, script_nome="impressao_1707.ahk"):
        user32 = ctypes.windll.user32
        rodando = False

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def enum_win_cb(hwnd, lparam):
            nonlocal rodando
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                if script_nome.lower() in buff.value.lower():
                    rodando = True
                    return False
            return True

        user32.EnumWindows(WNDENUMPROC(enum_win_cb), 0)
        return rodando

    def abrir_janela_monitor(self):
        if self._monitor_window:
            try:
                self._monitor_window.destroy()
            except Exception:
                pass
            self._monitor_window = None

        caminho_monitor_html = os.path.join(DIRETORIO_ATUAL, "monitor.html")

        monitor_win = webview.create_window(
            title="AUT_1707 - Monitor",
            url=caminho_monitor_html,
            width=420,
            height=280,
            resizable=False,
            on_top=True,
            background_color='#0D2130',
            js_api=self
        )
        self._monitor_window = monitor_win

        def monitorar_processo_ahk():
            time.sleep(2)
            while True:
                time.sleep(1.0)
                if not self.ahk_esta_rodando("impressao_1707.ahk"):
                    try:
                        monitor_win.destroy()
                    except Exception:
                        pass
                    self._monitor_window = None
                    break

        threading.Thread(target=monitorar_processo_ahk, daemon=True).start()

    def iniciar_tudo(self):
        if self._servidor_iniciado:
            return {"ok": True, "msg": "Servidor Keep JÁ ESTÁ EM EXECUÇÃO!"}

        try:
            if "servidor_keep" in sys.modules:
                servidor_keep = importlib.reload(sys.modules["servidor_keep"])
            else:
                servidor_keep = importlib.import_module("servidor_keep")

            if hasattr(servidor_keep, 'iniciar'):
                threading.Thread(target=servidor_keep.iniciar, daemon=True).start()
                self._servidor_iniciado = True
                return {"ok": True, "msg": "Servidor Keep INICIADO com sucesso!"}
            else:
                return {"ok": False, "msg": "Função 'iniciar' não encontrada em servidor_keep.py"}
        except Exception as e:
            return {"ok": False, "msg": f"Erro ao carregar servidor_keep: {e}"}

    def encerrar_tudo(self):
        # 1. Encerra apenas o script AHK impressao_1707.ahk
        fechar_script_ahk_especifico("impressao_1707.ahk")

        # 2. Chama o encerramento do servidor_keep se houver método no módulo
        if "servidor_keep" in sys.modules:
            servidor_keep = sys.modules["servidor_keep"]
            if hasattr(servidor_keep, 'parar'):
                try:
                    servidor_keep.parar()
                except Exception:
                    pass

        # Tenta enviar requisição de shutdown para a API local (se configurada)
        try:
            req = urllib.request.Request("http://127.0.0.1:5000/shutdown", method="POST")
            urllib.request.urlopen(req, timeout=1)
        except Exception:
            pass

        self._servidor_iniciado = False

        # 3. Fecha a janela do monitor se aberta
        if self._monitor_window:
            try:
                self._monitor_window.destroy()
            except Exception:
                pass
            self._monitor_window = None

        return {"ok": True, "msg": "Processo impressao_1707.ahk e Servidor Keep ENCERRADOS."}

    def abrir_script_ahk(self):
        script_path = None
        for arquivo in os.listdir(DIRETORIO_ATUAL):
            if arquivo.endswith(".ahk"):
                script_path = os.path.join(DIRETORIO_ATUAL, arquivo)
                break
        
        if script_path and os.path.exists(script_path):
            os.startfile(script_path)
            threading.Thread(target=self.abrir_janela_monitor, daemon=True).start()
            return {"ok": True, "msg": f"Script {os.path.basename(script_path)} e Monitor HTML iniciados."}
            
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
    caminho_index_html = os.path.join(DIRETORIO_ATUAL, "index.html")
    window = webview.create_window(
        title="AUT_1707",
        url=caminho_index_html,
        width=950,
        height=800,
        resizable=False,
        background_color='#0D2130',
        js_api=api
    )
    api.set_window(window)
    webview.start(debug=False)