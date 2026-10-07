import os
import json
import ctypes
import winsound
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class AppAutomacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Configuração - WinThor 1707")
        self.root.geometry("580x500")
        self.root.resizable(False, False)

        self.pasta_projeto = tk.StringVar(value=BASE_DIR)
        self.nome_impressora = tk.StringVar(value="WMS2")
        self.capturando_coordenada = False

        # Mapeamento completo dos 9 pontos de clique utilizados pelo AutoHotkey
        self.mapeamento_coords = {
            "1. Campo de Código do Produto": "CampoCodigo",
            "2. Botão Imprimir (Visualização)": "BotaoImprimir2",
            "3. Botão Trocar Impressora": "BotaoTrocarImpressora",
            "4. Seleção Impressora WMS 2": "ImpressoraWMS2",
            "5. Botão OK (Impressora)": "BotaoOK",
            "6. Botão OK (Pop-up Informação)": "BotaoOK_Informacao",
            "7. Botão OK (Pop-up Atenção)": "BotaoOK_Atencao",
            "8. Botão Imprimir (Universal)": "BotaoImprimirUniversal",
            "9. Botão Fechar (Visualização)": "BotaoFechar"
        }

        self.coords_atuais = {
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

        self.container = ttk.Frame(self.root, padding="15")
        self.container.pack(fill="both", expand=True)

        self.carregar_configuracao()
        self.criar_tela_configuracao()

    def criar_tela_configuracao(self):
        self.limpar_container()
        self.capturando_coordenada = False

        ttk.Label(self.container, text="⚙️ Configurações do Projeto", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        ttk.Label(self.container, text="Localização da Pasta do Projeto:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        frame_pasta = ttk.Frame(self.container)
        frame_pasta.pack(fill="x", pady=(2, 10))
        ttk.Entry(frame_pasta, textvariable=self.pasta_projeto, state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(frame_pasta, text="Selecionar Pasta...", command=self.selecionar_pasta).pack(side="right")

        ttk.Label(self.container, text="Nome da Impressora Padrão:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Entry(self.container, textvariable=self.nome_impressora).pack(fill="x", pady=(2, 15))

        btn_coords = ttk.Button(self.container, text="📍 Configurar Localização do Ponteiro (Coordenadas 1-9)", command=self.criar_tela_ponteiro)
        btn_coords.pack(fill="x", ipady=5, pady=(0, 15))

        btn_salvar = ttk.Button(self.container, text="💾 Salvar Configurações no Projeto", command=self.salvar_configuracoes)
        btn_salvar.pack(fill="x", ipady=8, side="bottom")

    def criar_tela_ponteiro(self):
        self.limpar_container()

        ttk.Label(self.container, text="🎯 Capturar Coordenadas do Ponteiro", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        ttk.Label(self.container, text="Selecione qual ponto deseja alterar (1 a 9):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        self.combo_coords = ttk.Combobox(self.container, values=list(self.mapeamento_coords.keys()), state="readonly", font=("Segoe UI", 10))
        self.combo_coords.current(0)
        self.combo_coords.pack(fill="x", pady=(5, 15))
        self.combo_coords.bind("<<ComboboxSelected>>", self.atualizar_label_coord_atual)

        self.lbl_coord_atual = ttk.Label(self.container, text="", font=("Segoe UI", 11, "bold"), foreground="#0056b3")
        self.lbl_coord_atual.pack(anchor="w", pady=5)
        self.atualizar_label_coord_atual()

        frame_instrucao = ttk.LabelFrame(self.container, text=" Modo de Captura Ativa ", padding="10")
        frame_instrucao.pack(fill="x", pady=15)

        ttk.Label(frame_instrucao, text="1. Clique no botão abaixo para ativar.\n2. Vá até a tela do WinThor.\n3. Clique com o BOTÃO DIREITO do mouse em cima do alvo.\n4. Um som confirmará o salvamento da posição X, Y.", justify="left", font=("Segoe UI", 9)).pack(anchor="w")

        self.lbl_status_captura = tk.Label(frame_instrucao, text="Aguardando ativação...", font=("Segoe UI", 10, "bold"), fg="gray")
        self.lbl_status_captura.pack(anchor="w", pady=(10, 0))

        self.btn_capturar = ttk.Button(frame_instrucao, text="🎯 Ativar Captura por Botão Direito", command=self.iniciar_captura)
        self.btn_capturar.pack(fill="x", pady=(10, 0), ipady=5)

        ttk.Button(self.container, text="⬅️ Voltar às Configurações", command=self.criar_tela_configuracao).pack(fill="x", side="bottom", ipady=5)

    def atualizar_label_coord_atual(self, event=None):
        item_sel = self.combo_coords.get()
        chave = self.mapeamento_coords[item_sel]
        x = self.coords_atuais.get(f"{chave}_X", 0)
        y = self.coords_atuais.get(f"{chave}_Y", 0)
        self.lbl_coord_atual.config(text=f"Posição Atual: X = {x} | Y = {y}")

    def iniciar_captura(self):
        self.capturando_coordenada = True
        self.btn_capturar.config(state="disabled")
        self.lbl_status_captura.config(text="🔴 MODO CAPTURA ATIVO! Clique com o BOTÃO DIREITO na tela...", fg="#cc0000")
        self.root.after(100, self.loop_captura_mouse)

    def loop_captura_mouse(self):
        if not self.capturando_coordenada:
            return

        state = ctypes.windll.user32.GetAsyncKeyState(0x02)
        if state & 0x8000:
            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            x, y = pt.x, pt.y

            winsound.Beep(1200, 150)

            item_sel = self.combo_coords.get()
            chave = self.mapeamento_coords[item_sel]

            self.coords_atuais[f"{chave}_X"] = x
            self.coords_atuais[f"{chave}_Y"] = y

            self.salvar_json_completo()

            self.lbl_status_captura.config(text=f"✅ Posição salva! X={x}, Y={y}", fg="#28a745")
            self.atualizar_label_coord_atual()
            self.capturando_coordenada = False
            self.btn_capturar.config(state="normal")
            return

        self.root.after(50, self.loop_captura_mouse)

    def salvar_json_completo(self):
        dados_config = {
            "PASTA_PROJETO": self.pasta_projeto.get(),
            "NOME_IMPRESSORA": self.nome_impressora.get().strip(),
            "TITULO_KEEP": "WinThor",
            "ARQUIVO_CODIGOS": "codigos.txt",
            "TIMEOUT": 15,
            "COORDENADAS": self.coords_atuais
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(dados_config, f, indent=4, ensure_ascii=False)

    def salvar_configuracoes(self):
        if not self.pasta_projeto.get():
            messagebox.showwarning("Aviso", "Selecione a pasta do projeto antes de continuar.")
            return
        self.salvar_json_completo()
        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso no config.json!\nAgora basta utilizar a tecla F2 no WinThor.")

    def selecionar_pasta(self):
        caminho = filedialog.askdirectory(title="Selecione a Pasta do Projeto")
        if caminho:
            self.pasta_projeto.set(os.path.normpath(caminho))

    def carregar_configuracao(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.pasta_projeto.set(dados.get("PASTA_PROJETO", BASE_DIR))
                    self.nome_impressora.set(dados.get("NOME_IMPRESSORA", "WMS2"))
                    if "COORDENADAS" in dados:
                        self.coords_atuais.update(dados["COORDENADAS"])
            except Exception:
                pass

    def limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppAutomacao(root)
    root.mainloop()