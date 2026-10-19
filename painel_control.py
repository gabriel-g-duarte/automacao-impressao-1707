import json
import os
import sys
import time
import ctypes
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Estrutura para capturar posição global do mouse no Windows
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def obter_posicao_mouse():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

# Caminho da pasta local do script
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(DIRETORIO_ATUAL, "config.json")

# Configurações Padrão de Fábrica
DEFAULTS_CONFIG = {
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

def carregar_config():
    """Carrega o arquivo config.json mantendo dados gravados pelo usuário."""
    config = DEFAULTS_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                dados_arquivo = json.load(f)
                config.update(dados_arquivo)
        except Exception as e:
            print(f"Erro ao ler config.json: {e}")
            
    # Garante que se PASTA_PROJETO estiver vazia no JSON, utiliza o diretório atual
    if not config.get("PASTA_PROJETO"):
        config["PASTA_PROJETO"] = DIRETORIO_ATUAL
        
    return config

def salvar_config(config_data):
    """Grava as configurações no config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível salvar as configurações:\n{e}")
        return False

# ---------------------------------------------------------------------
# Componente de Botão Arredondado
# ---------------------------------------------------------------------
class BotaoArredondado(tk.Canvas):
    def __init__(self, parent, text, command=None, width=100, height=28, radius=10, 
                 bg_color="#f3f4f6", hover_color="#e5e7eb", text_color="#1f2937", 
                 border_color="#e5e7eb", font=("Segoe UI", 9, "normal"), **kwargs):
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
        pts = [
            r, 0,
            w - r, 0,
            w, 0,
            w, r,
            w, h - r,
            w, h,
            w - r, h,
            r, h,
            0, h,
            0, h - r,
            0, r,
            0, 0
        ]
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

# ---------------------------------------------------------------------
# Aplicação Principal
# ---------------------------------------------------------------------
class PainelControleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Painel de Controle - Automação WinThor 1707")
        self.geometry("650x840")
        self.resizable(False, False)
        self.configure(bg="#f8f9fa")

        self.config_data = carregar_config()

        # ÁREA MESTRE CONTAINER
        self.scroll_frame = tk.Frame(self, bg="#f8f9fa")
        self.scroll_frame.pack(fill="both", expand=True)

        self.CriarWidgets()

    def CriarCardEstiloFigma(self, parent, titulo_texto, subtitulo_texto):
        """Cria um card com cabeçalho limpo (sem caixa de ícone) e bordas suaves."""
        card_outer = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid", highlightbackground="#e2e8f0", highlightthickness=1)
        card_outer.pack(fill="x", padx=16, pady=6)

        # Cabeçalho com Gradiente suave
        header_h = 46
        canvas_header = tk.Canvas(card_outer, height=header_h, bg="#f1f3f5", highlightthickness=0)
        canvas_header.pack(fill="x", side="top")

        def desenhar_header(event=None):
            w = canvas_header.winfo_width()
            if w <= 1:
                w = 600
            canvas_header.delete("all")

            c1 = (241, 243, 245)
            c2 = (233, 236, 239)
            for i in range(header_h):
                ratio = i / header_h
                r_c = int(c1[0] + (c2[0] - c1[0]) * ratio)
                g_c = int(c1[1] + (c2[1] - c1[1]) * ratio)
                b_c = int(c1[2] + (c2[2] - c1[2]) * ratio)
                color = f"#{r_c:02x}{g_c:02x}{b_c:02x}"
                canvas_header.create_line(0, i, w, i, fill=color)

            # Título principal
            canvas_header.create_text(16, 16, anchor="w", text=titulo_texto, font=("Segoe UI", 10, "normal"), fill="#1f2937")

            # Subtítulo
            canvas_header.create_text(16, 31, anchor="w", text=subtitulo_texto, font=("Segoe UI", 8, "normal"), fill="#6b7280")

        canvas_header.bind("<Configure>", desenhar_header)

        # Corpo do Card
        body_frame = tk.Frame(card_outer, bg="#ffffff")
        body_frame.pack(fill="x", expand=True, padx=14, pady=10)

        return body_frame

    def CriarCampoTexto(self, parent, variable, width=None):
        """Cria um campo de entrada limpo com bordas cinza claras."""
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=("Segoe UI", 9, "normal"),
            bg="#ffffff",
            fg="#1f2937",
            bd=0,
            relief="flat",
            highlightbackground="#e2e8f0",
            highlightcolor="#0284c7",
            highlightthickness=1,
            width=width
        )
        return entry

    def CriarWidgets(self):
        # ---------------------------------------------------------------------
        # CARD 1: DIRETÓRIOS E CAMINHOS DO SISTEMA
        # ---------------------------------------------------------------------
        body_pastas = self.CriarCardEstiloFigma(
            self.scroll_frame, 
            titulo_texto="Informações gerais", 
            subtitulo_texto="Os detalhes que identificam os caminhos do seu sistema"
        )

        tk.Label(body_pastas, text="Pasta local da automação *", bg="#ffffff", fg="#374151", font=("Segoe UI", 8, "normal")).pack(anchor="w", pady=(0, 2))
        sub_local = tk.Frame(body_pastas, bg="#ffffff")
        sub_local.pack(fill="x", pady=(0, 8))
        
        self.var_pasta_local = tk.StringVar(value=self.config_data.get("PASTA_LOCAL_PROJETO", DIRETORIO_ATUAL))
        entry_local = self.CriarCampoTexto(sub_local, self.var_pasta_local)
        entry_local.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 8))
        
        btn_local = BotaoArredondado(
            sub_local, text="Procurar", width=85, height=26, radius=10,
            command=lambda: self.SelecionarDiretorio(self.var_pasta_local, "Selecione a Pasta da Automação")
        )
        btn_local.pack(side="right")

        tk.Label(body_pastas, text="Pasta de destino dos relatórios *", bg="#ffffff", fg="#374151", font=("Segoe UI", 8, "normal")).pack(anchor="w", pady=(0, 2))
        sub_relatorios = tk.Frame(body_pastas, bg="#ffffff")
        sub_relatorios.pack(fill="x", pady=(0, 2))
        
        val_relatorios = self.config_data.get("PASTA_PROJETO") or DIRETORIO_ATUAL
        self.var_pasta_relatorios = tk.StringVar(value=val_relatorios)
        entry_relatorios = self.CriarCampoTexto(sub_relatorios, self.var_pasta_relatorios)
        entry_relatorios.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 8))
        
        btn_relatorios = BotaoArredondado(
            sub_relatorios, text="Procurar", width=85, height=26, radius=10,
            command=lambda: self.SelecionarDiretorio(self.var_pasta_relatorios, "Selecione a Pasta de Destino dos Relatórios")
        )
        btn_relatorios.pack(side="right")

        # ---------------------------------------------------------------------
        # CARD 2: CONFIGURAÇÃO DE IMPRESSORA
        # ---------------------------------------------------------------------
        body_impressora = self.CriarCardEstiloFigma(
            self.scroll_frame, 
            titulo_texto="Configuração de impressão", 
            subtitulo_texto="Nome exato da impressora para seleção automática"
        )

        tk.Label(body_impressora, text="Nome da impressora padrão *", bg="#ffffff", fg="#374151", font=("Segoe UI", 8, "normal")).grid(row=0, column=0, sticky="w", pady=2)
        
        self.var_impressora = tk.StringVar(value=self.config_data.get("NOME_IMPRESSORA", "WMS2"))
        entry_imp = self.CriarCampoTexto(body_impressora, self.var_impressora, width=32)
        entry_imp.grid(row=0, column=1, sticky="w", padx=12, pady=2, ipady=3)

        # ---------------------------------------------------------------------
        # CARD 3: COORDENADAS DOS PONTOS DE CLIQUE (9 PONTOS)
        # ---------------------------------------------------------------------
        body_coords = self.CriarCardEstiloFigma(
            self.scroll_frame, 
            titulo_texto="Coordenadas dos pontos de clique", 
            subtitulo_texto="Mapeamento de posições X e Y da tela no WinThor"
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

        # Cabeçalho da Tabela
        tk.Label(body_coords, text="Ponto / Ação", font=("Segoe UI", 8, "normal"), bg="#ffffff", fg="#6b7280").grid(row=0, column=0, sticky="w", padx=2, pady=2)
        tk.Label(body_coords, text="X", font=("Segoe UI", 8, "normal"), bg="#ffffff", fg="#6b7280").grid(row=0, column=1, padx=6, pady=2)
        tk.Label(body_coords, text="Y", font=("Segoe UI", 8, "normal"), bg="#ffffff", fg="#6b7280").grid(row=0, column=2, padx=6, pady=2)
        tk.Label(body_coords, text="Captura Automática", font=("Segoe UI", 8, "normal"), bg="#ffffff", fg="#6b7280").grid(row=0, column=3, padx=6, pady=2)

        for idx, (chave_base, label_text) in enumerate(self.lista_pontos, start=1):
            tk.Label(body_coords, text=label_text, font=("Segoe UI", 8, "normal"), bg="#ffffff", fg="#374151").grid(row=idx, column=0, sticky="w", pady=2)

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
                radius=10,
                command=lambda cb=chave_base: self.IniciarCapturaMouse(cb)
            )
            btn_cap.grid(row=idx, column=3, padx=6, pady=2)

            self.entries_coords[f"{chave_base}_X"] = var_x
            self.entries_coords[f"{chave_base}_Y"] = var_y

        # ---------------------------------------------------------------------
        # BOTÃO PRINCIPAL DE SALVAR (RODAPÉ)
        # ---------------------------------------------------------------------
        frame_bottom = tk.Frame(self.scroll_frame, bg="#f8f9fa")
        frame_bottom.pack(fill="x", pady=12)

        btn_salvar = BotaoArredondado(
            frame_bottom,
            text="Salvar configurações",
            width=230,
            height=36,
            radius=12,
            bg_color="#f3f4f6",
            hover_color="#e5e7eb",
            text_color="#1f2937",
            border_color="#e5e7eb",
            font=("Segoe UI", 9, "normal"),
            command=self.SalvarAlteracoes
        )
        btn_salvar.pack(anchor="center")

        lbl_subtexto = tk.Label(
            frame_bottom, 
            text="Continue de onde parou, quando quiser.", 
            font=("Segoe UI", 8, "normal"), 
            bg="#f8f9fa", 
            fg="#9ca3af"
        )
        lbl_subtexto.pack(anchor="center", pady=(4, 0))

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
            messagebox.showwarning("Aviso", f"A pasta local selecionada não existe:\n{pasta_local}")
            return

        if not pasta_relatorios:
            messagebox.showwarning("Aviso", "Por favor, selecione ou informe o caminho da pasta de destino dos relatórios!")
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

        self.config_data["PASTA_LOCAL_PROJETO"] = pasta_local
        self.config_data["PASTA_PROJETO"] = pasta_relatorios
        self.config_data["NOME_IMPRESSORA"] = nome_impressora

        try:
            for chave_var, str_var in self.entries_coords.items():
                self.config_data[chave_var] = int(str_var.get().strip())
        except ValueError:
            messagebox.showerror("Erro de Validação", "Todas as coordenadas X e Y devem ser números inteiros válidos!")
            return

        if salvar_config(self.config_data):
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!\nOs parâmetros foram atualizados no arquivo config.json.")


if __name__ == "__main__":
    app = PainelControleApp()
    app.mainloop()