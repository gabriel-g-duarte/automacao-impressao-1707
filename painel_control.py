import json
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Caminho do arquivo de configuração local
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def carregar_config():
    """Carrega as configurações do config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler config.json: {e}")
    return {
        "PASTA_PROJETO": "C:\\OneDrive\\Relatorios",
        "NOME_IMPRESSORA": "WMS2",
        "AUTO_INICIAR_AO_MUDAR_TXT": True,
        "TIMEOUT": 15
    }

def salvar_config(config_data):
    """Salva o dicionário de configurações no config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível salvar as configurações:\n{e}")
        return False

class PainelControleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Painel de Controle - Automação WinThor 1707")
        self.geometry("520x380")
        self.resizable(False, False)

        self.config_data = carregar_config()

        # Configuração de Estilo
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.CriarWidgets()
        self.AtualizarStatusLoop()

    def CriarWidgets(self):
        # Frame da Pasta do OneDrive / Projeto
        frame_pasta = ttk.LabelFrame(self, text=" 📁 Diretório do OneDrive / Projeto ", padding=10)
        frame_pasta.pack(fill="x", padx=15, pady=10)

        self.var_pasta = tk.StringVar(value=self.config_data.get("PASTA_PROJETO", ""))
        
        lbl_pasta = ttk.Label(frame_pasta, text="Caminho dos Relatórios:")
        lbl_pasta.pack(anchor="w", pady=(0, 5))

        sub_frame = ttk.Frame(frame_pasta)
        sub_frame.pack(fill="x")

        entry_pasta = ttk.Entry(sub_frame, textvariable=self.var_pasta, font=("Segoe UI", 9))
        entry_pasta.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_procurar = ttk.Button(sub_frame, text="Procurar...", command=self.SelecionarPastaOneDrive)
        btn_procurar.pack(side="right")

        # Frame de Opções de Impressão
        frame_opcoes = ttk.LabelFrame(self, text=" 🖨️ Configuração de Impressão ", padding=10)
        frame_opcoes.pack(fill="x", padx=15, pady=5)

        ttk.Label(frame_opcoes, text="Modo Padrão:").grid(row=0, column=0, sticky="w", pady=5)
        
        self.var_impressora = tk.StringVar(value=self.config_data.get("NOME_IMPRESSORA", "WMS2"))
        combo_imp = ttk.Combobox(
            frame_opcoes, 
            textvariable=self.var_impressora, 
            values=["WMS2", "Universal"], 
            state="readonly", 
            width=15
        )
        combo_imp.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Frame do Monitor de Status
        frame_status = ttk.LabelFrame(self, text=" 📊 Monitor de Execução ", padding=10)
        frame_status.pack(fill="both", expand=True, padx=15, pady=10)

        self.lbl_status = ttk.Label(frame_status, text="Status: Aguardando...", font=("Segoe UI", 10, "bold"), foreground="#0056b3")
        self.lbl_status.pack(anchor="w")

        self.lbl_progresso = ttk.Label(frame_status, text="Códigos Processados: 0 / 0", font=("Segoe UI", 9))
        self.lbl_progresso.pack(anchor="w", pady=2)

        # Botão de Salvar
        btn_salvar = ttk.Button(self, text="💾 Salvar Configurações", command=self.SalvarAlteracoes)
        btn_salvar.pack(side="bottom", pady=10)

    def SelecionarPastaOneDrive(self):
        """Abre o diálogo de seleção de diretório."""
        pasta_inicial = self.var_pasta.get() if os.path.exists(self.var_pasta.get()) else "C:\\"
        pasta_selecionada = filedialog.askdirectory(
            title="Selecione a Pasta dos Relatórios (OneDrive)",
            initialdir=pasta_inicial
        )
        if pasta_selecionada:
            # Padroniza barras do Windows
            pasta_formatada = os.path.normpath(pasta_selecionada)
            self.var_pasta.set(pasta_formatada)

    def SalvarAlteracoes(self):
        """Atualiza a estrutura e grava no config.json."""
        caminho_pasta = os.path.normpath(self.var_pasta.get().strip())

        if not os.path.exists(caminho_pasta):
            messagebox.showwarning("Aviso", "A pasta selecionada não existe no computador!\nVerifique o caminho do OneDrive.")
            return

        self.config_data["PASTA_PROJETO"] = caminho_pasta
        self.config_data["NOME_IMPRESSORA"] = self.var_impressora.get()

        if salvar_config(self.config_data):
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!\nO AutoHotkey utilizará o novo caminho na próxima execução.")

    def AtualizarStatusLoop(self):
        """Lê o status.json presente na pasta do projeto configurada."""
        pasta_projeto = self.var_pasta.get().strip()
        status_file = os.path.join(pasta_projeto, "status.json") if pasta_projeto else ""

        if status_file and os.path.exists(status_file):
            try:
                with open(status_file, "r", encoding="utf-8") as f:
                    st = json.load(f)
                    
                st_nome = st.get("status", "-")
                cod_atual = st.get("codigo_atual", "-")
                total_proc = st.get("total_processados", 0)

                if st_nome == "imprimindo":
                    self.lbl_status.config(text=f"Status: Imprimindo código {cod_atual}", foreground="#0056b3")
                elif st_nome == "concluido":
                    self.lbl_status.config(text="Status: Impressão Finalizada!", foreground="#28a745")
                elif st_nome == "erro":
                    self.lbl_status.config(text=f"Status: ERRO no código {cod_atual}", foreground="#cc0000")
                else:
                    self.lbl_status.config(text=f"Status: {st_nome.capitalize()}", foreground="#333333")

                self.lbl_progresso.config(text=f"Processados: {total_proc}")
            except Exception:
                pass

        # Atualiza a cada 1.5 segundos
        self.after(1500, self.AtualizarStatusLoop)


if __name__ == "__main__":
    app = PainelControleApp()
    app.mainloop()