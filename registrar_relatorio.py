import os
import json
import time
from datetime import datetime

try:
    import openpyxl
except ImportError:
    print("⚠️ A instalar biblioteca openpyxl...")
    os.system("pip install openpyxl")
    import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = os.path.join(BASE_DIR, "status.json")
ONEDRIVE_PATH = r"C:\Users\D8059GD\OneDrive - DFS Holding\Relatório Faltas 1707"

MESES = {
    "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
    "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
    "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
}

def salvar_log_excel(codigo, status_texto="Concluido"):
    agora = datetime.now()
    ano = agora.strftime("%Y")
    mes_num = agora.strftime("%m")
    nome_aba = MESES.get(mes_num, f"Mês {mes_num}")
    
    # 1. Pasta apenas com o ANO
    pasta_ano = os.path.join(ONEDRIVE_PATH, ano)
    os.makedirs(pasta_ano, exist_ok=True)
    
    # 2. Ficheiro Excel do Ano (.xlsx)
    caminho_excel = os.path.join(pasta_ano, f"Relatorio_Faltas_{ano}.xlsx")
    
    try:
        # Carrega o ficheiro se já existir ou cria um novo
        if os.path.exists(caminho_excel):
            wb = openpyxl.load_workbook(caminho_excel)
        else:
            wb = openpyxl.Workbook()
            # Remove a aba genérica "Sheet" criada por padrão
            if "Sheet" in wb.sheetnames:
                wb.remove(wb["Sheet"])
        
        # 3. Obtém ou cria a aba do MÊS atual
        if nome_aba in wb.sheetnames:
            ws = wb[nome_aba]
        else:
            ws = wb.create_sheet(title=nome_aba)
            # Adiciona o cabeçalho na primeira linha da nova aba
            ws.append(["Data", "Hora", "Codigo_Produto", "Status"])
        
        # 4. Adiciona a linha com os dados
        data_str = agora.strftime("%d/%m/%Y")
        hora_str = agora.strftime("%H:%M:%S")
        ws.append([data_str, hora_str, codigo, status_texto])
        
        # Guarda as alterações no ficheiro
        wb.save(caminho_excel)
        print(f"✅ [LOG REGISTADO] Código {codigo} gravado na aba '{nome_aba}' em: {caminho_excel}")

    except PermissionError:
        print(f"⚠️ [AVISO] Feche o ficheiro Excel '{caminho_excel}' para permitir a gravação do log!")
    except Exception as e:
        print(f"❌ [ERRO AO GRAVAR EXCEL] {e}")

def monitorar_status():
    print(f"🔍 Monitorizando status.json em: {STATUS_FILE}")
    print(f"📂 Destino OneDrive: {ONEDRIVE_PATH}\n")
    
    processados = set()
    ultimo_mtime = 0
    
    while True:
        time.sleep(0.3)
        if not os.path.exists(STATUS_FILE):
            continue
            
        try:
            mtime = os.path.getmtime(STATUS_FILE)
            if mtime != ultimo_mtime:
                ultimo_mtime = mtime
                with open(STATUS_FILE, "r", encoding="utf-8-sig") as f:
                    dados = json.load(f)
                
                codigo = str(dados.get("codigo_atual", "")).strip()
                
                if codigo and codigo not in ("-", "Concluído", "") and codigo not in processados:
                    salvar_log_excel(codigo, "Concluido")
                    processados.add(codigo)
        except Exception:
            pass

if __name__ == "__main__":
    monitorar_status()