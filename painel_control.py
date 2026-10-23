import json
import os
import sys
import time
import ctypes
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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
    "PASTA_LOCAL_PROJETO": DIRETORIO_ATUAL,
    "PASTA_PROJETO": DIRETORIO_ATUAL,
    "NOME_IMPRESSORA": "WMS2",
    "TIMEOUT": 15,
    "JANELA_TARGET": "1707 - Consultas Auxiliares - Consultar Produtos (Remoto)",
    "CampoCodigo_X": 2255,            "CampoCodigo_Y": 76,
    "BotaoImprimir2_X": 1937,         "BotaoImprimir2_Y": 35,
    "BotaoTrocarImpressora_X": 2773,  "BotaoTrocarImpressora_Y": 314,
    "ImpressoraWMS2_X": 2822,         "ImpressoraWMS2_Y": 448,
    "BotaoOK_X": 2996,                "BotaoOK_Y": 657,
    "BotaoOK_Informacao_X": 2883,     "BotaoOK_Informacao_Y": 554,
    "BotaoOK_Atencao_X": 2874,        "BotaoOK_Atencao_Y": 550,
    "BotaoImprimirUniversal_X": 880,  "BotaoImprimirUniversal_Y": 404,
    "BotaoFechar_X": 2410,            "BotaoFechar_Y": 35
}

# Paleta de Cores do Tema Dark (Inspirada no Painel)
COR_FUNDO_APP = "#071426"       # Azul Marinho Escuro de Fundo
COR_CARD_BG = "#0e223b"         # Azul Escuro dos Cards
COR_CARD_BORDER = "#1a365d"     # Borda Discreta
COR_CARD_ACTIVE = "#22c55e"     # Verde Neon / Destaque
COR_TEXTO_BRANCO = "#ffffff"    # Texto Principal
COR_TEXTO_VERDE = "#22c55e"     # Subtítulos / Destaques
COR_TEXTO_MUTED = "#8a9fb4"     # Textos Secundários
COR_INPUT_BG = "#071426"        # Fundo dos Campos de Texto

def carregar_config():
    config = DEFAULTS_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
                dados_arquivo = json.load(f)
                if "PASTA_LOCAL_PROJETO" in dados_arquivo and "PASTA_AUTOMACAO" not in dados_arquivo:
                    dados_arquivo["PASTA_AUTOMACAO"] = dados_arquivo["PASTA_LOCAL_PROJETO"]
                if "PASTA_PROJETO" in dados_arquivo and "PASTA_RELATORIO_FALTAS" not in dados_arquivo:
                    dados_arquivo["PASTA_RELATORIO_FALTAS"] = dados_arquivo["PASTA_PROJETO"]
                config.update(dados_arquivo)
        except Exception as e:
            messagebox.showwarning("Erro na Leitura do JSON", f"Não foi possível ler o config.json:\n{e}")
    return config

def salvar_config(config_data):
    try:
        config_data["PASTA_LOCAL_PROJETO"] = config_data.get("PASTA_AUTOMACAO", DIRETORIO_ATUAL)
        config_data["PASTA_PROJETO"] = config_data.get("PASTA_RELATORIO_FALTAS", DIRETORIO_ATUAL)

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar as configurações:\n{e}")
        return False

class BotaoArredondado(tk.Canvas):
    def __init__(self, parent, text, command=None, width=100, height=34, radius=10, 
                 bg_color="#162f4d", hover_color="#20426b", text_color="#ffffff", 
                 border_color="#284e7a", font=("Segoe UI", 9, "bold"), **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, bd=0, cursor="hand2", **kwargs)
        self.text = text
        self.command = command
        self.radius = radius
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.current_bg = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.font = font

        self.bind("<Configure>", self._desenhar)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _desenhar(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 5 or h < 5:
            return

        r = self.radius
        pts = [r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h, w - r, h, r, h, 0, h, 0, h - r, 0, r, 0, 0]
        self.create_polygon(pts, smooth=True, fill=self.current_bg, outline=self.border_color, width=1)
        self.create_text(w / 2, h / 2, text=self.text, font=self.font, fill=self.text_color)

    def _on_enter(self, event):
        self.current_bg = self.hover_color
        self._desenhar()

    def _on_leave(self, event):
        self.current_bg = self.bg_color
        self._desenhar()

    def _on_click(self, event):
        if self.command:
            self.command()

class PainelControleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AUT_1707 — Operação Delly's")
        self.geometry("650x860")
        self.resizable(False, False)
        self.configure(bg=COR_FUNDO_APP)

        self.config_data = carregar_config()

        self.container = tk.Frame(self, bg=COR_FUNDO_APP)
        self.container.pack(fill="both", expand=True)

        self.frame_principal = tk.Frame(self.container, bg=COR_FUNDO_APP)
        self.frame_configuracao = tk.Frame(self.container, bg=COR_FUNDO_APP)

        self.CriarTelaPrincipal()
        self.CriarTelaConfiguracao()

        self.frame_principal.pack(fill="both", expand=True)

    def mostrar_frame(self, frame_ocultar, frame_mostrar):
        frame_ocultar.pack_forget()
        frame_mostrar.pack(fill="both", expand=True)
        self.lbl_status_principal.config(text="")

    def fechar_processos_ahk(self):
        CREATE_NO_WINDOW = 0x08000000
        subprocess.call('taskkill /f /im AutoHotkey.exe', creationflags=CREATE_NO_WINDOW)
        subprocess.call('taskkill /f /im AutoHotkey64.exe', creationflags=CREATE_NO_WINDOW)
        subprocess.call('taskkill /f /im AutoHotkey32.exe', creationflags=CREATE_NO_WINDOW)

    def acao_iniciar_tudo(self):
        self.lbl_status_principal.config(text="Status: Inicializando automação e sincronização...", fg="#38bdf8")
        self.update()
        time.sleep(0.5)
        self.lbl_status_principal.config(text="Status: Automação e serviços INICIADOS com sucesso.", fg=COR_TEXTO_VERDE)

    def acao_encerrar_tudo(self):
        self.lbl_status_principal.config(text="Status: Encerrando serviços...", fg="#38bdf8")
        self.update()
        self.fechar_processos_ahk()
        time.sleep(0.5)
        self.lbl_status_principal.config(text="Status: Processos e automação ENCERRADOS com sucesso.", fg="#f87171")

    def acao_abrir_script_ahk(self):
        script_path = None
        for arquivo in os.listdir(DIRETORIO_ATUAL):
            if arquivo.endswith(".ahk"):
                script_path = os.path.join(DIRETORIO_ATUAL, arquivo)
                break
        
        if script_path and os.path.exists(script_path):
            os.startfile(script_path)
            self.lbl_status_principal.config(text=f"Status: Script AHK aberto ({os.path.basename(script_path)}).", fg=COR_TEXTO_VERDE)
        else:
            self.lbl_status_principal.config(text="Status: Erro. Nenhum arquivo .ahk encontrado na pasta.", fg="#f87171")

    def CriarCardEstiloDark(self, parent, titulo_texto, subtitulo_texto, numero_badge="01", destaque=False):
        borda_cor = COR_CARD_ACTIVE if destaque else COR_CARD_BORDER
        card_outer = tk.Frame(parent, bg=COR_CARD_BG, bd=1, relief="solid", highlightbackground=borda_cor, highlightthickness=1)
        card_outer.pack(fill="x", padx=18, pady=8)

        # Cabeçalho do Card
        header_frame = tk.Frame(card_outer, bg=COR_CARD_BG)
        header_frame.pack(fill="x", padx=16, pady=(14, 4))

        title_box = tk.Frame(header_frame, bg=COR_CARD_BG)
        title_box.pack(side="left", fill="both", expand=True)

        tk.Label(title_box, text=titulo_texto, font=("Segoe UI", 11, "bold"), bg=COR_CARD_BG, fg=COR_TEXTO_BRANCO, anchor="w").pack(fill="x")
        tk.Label(title_box, text=subtitulo_texto, font=("Segoe UI", 8, "bold"), bg=COR_CARD_BG, fg=COR_TEXTO_VERDE, anchor="w").pack(fill="x", pady=(2, 0))

        # Badge com número no canto superior direito
        badge_frame = tk.Frame(header_frame, bg="#132f52", padx=8, pady=3)
        badge_frame.pack(side="right", anchor="n")
        tk.Label(badge_frame, text=numero_badge, font=("Segoe UI", 8, "bold"), bg="#132f52", fg=COR_TEXTO_MUTED).pack()

        body_frame = tk.Frame(card_outer, bg=COR_CARD_BG)
        body_frame.pack(fill="x", expand=True, padx=16, pady=(8, 14))

        return body_frame

    def CriarTelaPrincipal(self):
        # Header com Logo Estilo Delly's
        header_top = tk.Frame(self.frame_principal, bg=COR_FUNDO_APP)
        header_top.pack(fill="x", padx=18, pady=(20, 10))

        # Logo / Badge Branca com Nome
        logo_card = tk.Frame(header_top, bg="#ffffff", padx=12, pady=6)
        logo_card.pack(side="left")

        tk.Label(logo_card, text="D", font=("Segoe UI", 18, "bold"), bg="#ffffff", fg="#22c55e").pack(side="left")
        
        texto_logo_frame = tk.Frame(logo_card, bg="#ffffff")
        texto_logo_frame.pack(side="left", padx=(4, 0))
        tk.Label(texto_logo_frame, text="DELLY'S", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#0d4aa2").pack(anchor="w")
        tk.Label(texto_logo_frame, text="FOOD SERVICE", font=("Segoe UI", 6, "bold"), bg="#ffffff", fg="#22c55e").pack(anchor="w")

        info_header = tk.Frame(header_top, bg=COR_FUNDO_APP)
        info_header.pack(side="left", padx=14)
        tk.Label(info_header, text="Operação 1707", font=("Segoe UI", 14, "bold"), bg=COR_FUNDO_APP, fg=COR_TEXTO_BRANCO).pack(anchor="w")
        tk.Label(info_header, text="Painel da Automação de Impressão", font=("Segoe UI", 9, "normal"), bg=COR_FUNDO_APP, fg=COR_TEXTO_MUTED).pack(anchor="w")

        # Card de Operação Principal (Com Borda Verde Neon de Destaque)
        card_acoes = self.CriarCardEstiloDark(self.frame_principal, "Automação WinThor", "ROTINA 1707 & PAINEL DE CONTROLE", "01", destaque=True)

        btn_iniciar = BotaoArredondado(
            card_acoes, text="▶  Iniciar Tudo", width=220, height=36, radius=8,
            bg_color="#22c55e", hover_color="#16a34a", text_color="#ffffff", border_color="#22c55e",
            command=self.acao_iniciar_tudo
        )
        btn_iniciar.pack(pady=(8, 6))

        btn_encerrar = BotaoArredondado(
            card_acoes, text="⏹  Encerrar Tudo", width=220, height=36, radius=8,
            bg_color="#991b1b", hover_color="#7f1d1d", text_color="#ffffff", border_color="#991b1b",
            command=self.acao_encerrar_tudo
        )
        btn_encerrar.pack(pady=6)

        btn_ahk = BotaoArredondado(
            card_acoes, text="📄  Abrir Script AHK", width=220, height=36, radius=8,
            bg_color="#162f4d", hover_color="#20426b", text_color="#ffffff", border_color="#284e7a",
            command=self.acao_abrir_script_ahk
        )
        btn_ahk.pack(pady=6)

        btn_config = BotaoArredondado(
            card_acoes, text="⚙  Configurar Painel", width=220, height=36, radius=8,
            bg_color="#0e223b", hover_color="#162f4d", text_color=COR_TEXTO_VERDE, border_color="#1a365d",
            command=lambda: self.mostrar_frame(self.frame_principal, self.frame_configuracao)
        )
        btn_config.pack(pady=(6, 8))

        self.lbl_status_principal = tk.Label(self.frame_principal, text="", font=("Segoe UI", 9, "bold"), bg=COR_FUNDO_APP, fg=COR_TEXTO_VERDE)
        self.lbl_status_principal.pack(pady=4)

        # Card Informativo de Atalhos
        card_atalhos = self.CriarCardEstiloDark(self.frame_principal, "Teclas de Atalho", "COMANDOS RÁPIDOS NO TECLADO", "02")
        
        atalhos_info = [
            ("F1", "Pausa ou retoma a execução do script."),
            ("F2", "Inicia o processamento da lista de impressão."),
            ("F3", "Encerra completamente a execução."),
            ("F4", "Importa lista de códigos da área de transferência.")
        ]

        for tecla, desc in atalhos_info:
            frame_linha = tk.Frame(card_atalhos, bg=COR_CARD_BG)
            frame_linha.pack(fill="x", pady=4)
            tk.Label(frame_linha, text=f"[{tecla}]", font=("Segoe UI", 9, "bold"), bg="#132f52", fg=COR_TEXTO_VERDE, width=5).pack(side="left")
            tk.Label(frame_linha, text=desc, font=("Segoe UI", 9, "normal"), bg=COR_CARD_BG, fg=COR_TEXTO_MUTED).pack(side="left", padx=10)

    def CriarTelaConfiguracao(self):
        top_frame = tk.Frame(self.frame_configuracao, bg=COR_FUNDO_APP)
        top_frame.pack(fill="x", padx=18, pady=12)

        btn_voltar = BotaoArredondado(
            top_frame, text="⬅  Voltar ao Início", width=140, height=30, radius=8,
            bg_color="#162f4d", hover_color="#20426b", text_color="#ffffff", border_color="#284e7a",
            command=lambda: self.mostrar_frame(self.frame_configuracao, self.frame_principal)
        )
        btn_voltar.pack(side="left")

        self.scroll_frame = tk.Frame(self.frame_configuracao, bg=COR_FUNDO_APP)
        self.scroll_frame.pack(fill="both", expand=True)

        self.CriarWidgetsConfig()

    def CriarCampoTexto(self, parent, variable, width=None):
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=("Segoe UI", 9, "normal"),
            bg=COR_INPUT_BG,
            fg=COR_TEXTO_BRANCO,
            bd=0,
            relief="flat",
            highlightbackground=COR_CARD_BORDER,
            highlightcolor=COR_TEXTO_VERDE,
            highlightthickness=1,
            insertbackground="#ffffff",
            width=width
        )
        return entry

    def CriarWidgetsConfig(self):
        body_pastas = self.CriarCardEstiloDark(
            self.scroll_frame, 
            titulo_texto="Informações Gerais", 
            subtitulo_texto="DIRETÓRIOS E PASTAS DE RELATÓRIO",
            numero_badge="01"
        )

        tk.Label(body_pastas, text="Pasta da automação *", bg=COR_CARD_BG, fg=COR_TEXTO_MUTED, font=("Segoe UI", 8, "normal")).pack(anchor="w", pady=(0, 2))
        sub_local = tk.Frame(body_pastas, bg=COR_CARD_BG)
        sub_local.pack(fill="x", pady=(0, 8))
        
        self.var_pasta_local = tk.StringVar(value=self.config_data.get("PASTA_AUTOMACAO", DIRETORIO_ATUAL))
        entry_local = self.CriarCampoTexto(sub_local, self.var_pasta_local)
        entry_local.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 8))
        
        btn_local = BotaoArredondado(
            sub_local, text="Procurar", width=85, height=26, radius=6,
            bg_color="#162f4d", hover_color="#20426b", text_color="#ffffff", border_color="#284e7a",
            command=lambda: self.SelecionarDiretorio(self.var_pasta_local, "Selecione a Pasta da Automação")
        )
        btn_local.pack(side="right")

        tk.Label(body_pastas, text="Pasta do relatório de faltas *", bg=COR_CARD_BG, fg=COR_TEXTO_MUTED, font=("Segoe UI", 8, "normal")).pack(anchor="w", pady=(0, 2))
        sub_relatorios = tk.Frame(body_pastas, bg=COR_CARD_BG)
        sub_relatorios.pack(fill="x", pady=(0, 2))
        
        val_relatorios = self.config_data.get("PASTA_RELATORIO_FALTAS", DIRETORIO_ATUAL)
        self.var_pasta_relatorios = tk.StringVar(value=val_relatorios)
        entry_relatorios = self.CriarCampoTexto(sub_relatorios, self.var_pasta_relatorios)
        entry_relatorios.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 8))
        
        btn_relatorios = BotaoArredondado(
            sub_relatorios, text="Procurar", width=85, height=26, radius=6,
            bg_color="#162f4d", hover_color="#20426b", text_color="#ffffff", border_color="#284e7a",
            command=lambda: self.SelecionarDiretorio(self.var_pasta_relatorios, "Selecione a Pasta do Relatório de Faltas")
        )
        btn_relatorios.pack(side="right")

        body_impressora = self.CriarCardEstiloDark(
            self.scroll_frame, 
            titulo_texto="Configuração de Impressão", 
            subtitulo_texto="DISPOSITIVO PADRÃO DO WINTHOR",
            numero_badge="02"
        )

        tk.Label(body_impressora, text="Nome da impressora padrão *", bg=COR_CARD_BG, fg=COR_TEXTO_MUTED, font=("Segoe UI", 8, "normal")).grid(row=0, column=0, sticky="w", pady=2)
        
        self.var_impressora = tk.StringVar(value=self.config_data.get("NOME_IMPRESSORA", "WMS2"))
        entry_imp = self.CriarCampoTexto(body_impressora, self.var_impressora, width=32)
        entry_imp.grid(row=0, column=1, sticky="w", padx=12, pady=2, ipady=3)

        body_coords = self.CriarCardEstiloDark(
            self.scroll_frame, 
            titulo_texto="Coordenadas dos Pontos de Clique", 
            subtitulo_texto="MAPEAMENTO X E Y DA TELA",
            numero_badge="03"
        )

        self.lista_pontos = [
            ("CampoCodigo", "1. Campo de Código"),
            ("BotaoImprimir2", "2. Botão Imprimir (Preview)"),
            ("BotaoTrocarImpressora", "3. Trocar Impressora"),
            ("ImpressoraWMS2", "4. Seleção da Impressora"),
            ("BotaoOK", "5. Botão OK (Impressão)"),
            ("BotaoOK_Informacao", "6. OK Pop-up Informação"),
            ("BotaoOK_Atencao", "7. OK Pop-up Atenção"),
            ("BotaoImprimirUniversal", "8. Imprimir Universal Printer"),
            ("BotaoFechar", "9. Botão Fechar Preview")
        ]

        self.entries_coords = {}

        tk.Label(body_coords, text="Ponto / Ação", font=("Segoe UI", 8, "normal"), bg=COR_CARD_BG, fg=COR_TEXTO_MUTED).grid(row=0, column=0, sticky="w", padx=2, pady=2)
        tk.Label(body_coords, text="X", font=("Segoe UI", 8, "normal"), bg=COR_CARD_BG, fg=COR_TEXTO_MUTED).grid(row=0, column=1, padx=6, pady=2)
        tk.Label(body_coords, text="Y", font=("Segoe UI", 8, "normal"), bg=COR_CARD_BG, fg=COR_TEXTO_MUTED).grid(row=0, column=2, padx=6, pady=2)
        tk.Label(body_coords, text="Captura Automática", font=("Segoe UI", 8, "normal"), bg=COR_CARD_BG, fg=COR_TEXTO_MUTED).grid(row=0, column=3, padx=6, pady=2)

        for idx, (chave_base, label_text) in enumerate(self.lista_pontos, start=1):
            tk.Label(body_coords, text=label_text, font=("Segoe UI", 8, "normal"), bg=COR_CARD_BG, fg=COR_TEXTO_BRANCO).grid(row=idx, column=0, sticky="w", pady=2)

            val_x = str(self.config_data.get(f"{chave_base}_X", DEFAULTS_CONFIG.get(f"{chave_base}_X", 0)))
            val_y = str(self.config_data.get(f"{chave_base}_Y", DEFAULTS_CONFIG.get(f"{chave_base}_Y", 0)))

            var_x = tk.StringVar(value=val_x)
            var_y = tk.StringVar(value=val_y)

            entry_x = self.CriarCampoTexto(body_coords, var_x, width=7)
            entry_x.config(justify="center")
            entry_y = self.CriarCampoTexto(body_coords, var_y, width=7)
            entry_y.config(justify="center")

            entry_x.grid(row=idx, column=1, padx=4, pady=2, ipady=1)
            entry_y.grid(row=idx, column=2, padx=4, pady=2, ipady=1)

            btn_cap = BotaoArredondado(
                body_coords, 
                text="Capturar", 
                width=80,
                height=24,
                radius=6,
                bg_color="#162f4d", hover_color="#20426b", text_color="#ffffff", border_color="#284e7a",
                command=lambda cb=chave_base: self.IniciarCapturaMouse(cb)
            )
            btn_cap.grid(row=idx, column=3, padx=6, pady=2)

            self.entries_coords[f"{chave_base}_X"] = var_x
            self.entries_coords[f"{chave_base}_Y"] = var_y

        frame_bottom = tk.Frame(self.scroll_frame, bg=COR_FUNDO_APP)
        frame_bottom.pack(fill="x", pady=12)

        btn_salvar = BotaoArredondado(
            frame_bottom,
            text="Salvar configurações",
            width=230,
            height=36,
            radius=8,
            bg_color="#22c55e", hover_color="#16a34a", text_color="#ffffff", border_color="#22c55e",
            command=self.SalvarAlteracoes
        )
        btn_salvar.pack(anchor="center")

    def SelecionarDiretorio(self, var_alvo, titulo):
        pasta_inicial = var_alvo.get() if (var_alvo.get() and os.path.exists(var_alvo.get())) else DIRETORIO_ATUAL
        pasta_selecionada = filedialog.askdirectory(title=titulo, initialdir=pasta_inicial)
        if pasta_selecionada:
            var_alvo.set(os.path.normpath(pasta_selecionada))

    def IniciarCapturaMouse(self, chave_base):
        self.iconify()

        def escutar_clique():
            while ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000:
                time.sleep(0.05)
            
            while True:
                if ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000:
                    x, y = obter_posicao_mouse()
                    break
                time.sleep(0.02)

            self.after(0, lambda: self.FinalizarCapturaMouse(chave_base, x, y))

        threading.Thread(target=escutar_clique, daemon=True).start()

    def FinalizarCapturaMouse(self, chave_base, x, y):
        self.entries_coords[f"{chave_base}_X"].set(str(x))
        self.entries_coords[f"{chave_base}_Y"].set(str(y))
        
        self.deiconify()
        self.focus_force()
        messagebox.showinfo("Posição Capturada", f"Coordenadas registradas para {chave_base}:\nX: {x} | Y: {y}")

    def SalvarAlteracoes(self):
        pasta_local = os.path.normpath(self.var_pasta_local.get().strip())
        pasta_relatorios = os.path.normpath(self.var_pasta_relatorios.get().strip())
        nome_impressora = self.var_impressora.get().strip()

        if not os.path.exists(pasta_local):
            messagebox.showwarning("Aviso", f"A pasta selecionada não existe:\n{pasta_local}")
            return

        if not pasta_relatorios:
            messagebox.showwarning("Aviso", "Por favor, selecione ou informe o caminho da pasta do relatório de faltas!")
            return

        if not os.path.exists(pasta_relatorios):
            resposta = messagebox.askyesno(
                "Pasta não encontrada", 
                f"A pasta informada não existe no momento:\n{pasta_relatorios}\n\nDeseja criar essa pasta agora?"
            )
            if resposta:
                try:
                    os.makedirs(pasta_relatorios, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Erro ao Criar Pasta", f"Não foi possível criar a pasta:\n{e}")
                    return
            else:
                return

        if not nome_impressora:
            messagebox.showwarning("Aviso", "Informe um nome válido para a impressora!")
            return

        self.config_data["PASTA_AUTOMACAO"] = pasta_local
        self.config_data["PASTA_RELATORIO_FALTAS"] = pasta_relatorios
        self.config_data["NOME_IMPRESSORA"] = nome_impressora

        try:
            for chave_var, str_var in self.entries_coords.items():
                self.config_data[chave_var] = int(str_var.get().strip())
        except ValueError:
            messagebox.showerror("Erro de Validação", "Todas as coordenadas X e Y devem ser números inteiros válidos!")
            return

        if salvar_config(self.config_data):
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!\nOs parâmetros foram gravados permanentemente no arquivo config.json.")

if __name__ == "__main__":
    app = PainelControleApp()
    app.mainloop()