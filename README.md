# Tutorial de downloads
* Instale o python em https://www.python.org/downloads/ na versão mais recente. Ao executar a instalação do .exe, baixe em PATH, esta opção aparece durante a instalação e confirme o mesmo em PATH.
* Instale o AutoHotkey em https://www.autohotkey.com/ na versão mais recente
* Baixe o arquivo .zip em realeses e siga os próximos passos

---

# Em caso de dúvidas ou problemas durante o uso 
* Entrar em contato pelo e-mail ou pelo microsoft teams: gabriel.duarte@dellys.com.br ou D8059GD@dellys.com.br

---

# 🖨️ Automação de Impressão em Lote — WinThor (Rotina 1707)

Sistema de automação inteligente desenvolvido para capturar códigos de produtos a partir de notas do **Google Keep** (via extensão de navegador) e realizar a impressão automática na **Rotina 1707 do ERP WinThor** utilizando **AutoHotkey v2.0** e **Python**.

---

# Como ultilizar?

* O uso recomendado é digitalizar a lista de codigos completa, ultilizando algum aplicativo ou a própia câmera ex.: a câmera do iPhone tem essa digitalização própia, copiar e enviar junto ao produto (ele detecta automáticamento o código no início de cada linha, e para uso funcional o código precisa ficar no início de cada linha). Colar na nota desejada do keep e fazer o uso como no tutorial de vídeo.
* Outro uso recomendado é usar pelo computador que também é possivel, apenas colar a lista na nota e seguir o processo.

---

## 📺 Vídeo Tutorial (Passo a Passo)

Assista ao vídeo abaixo para ver a demonstração prática do funcionamento e o guia de configuração de todo o ecossistema:

https://github.com/user-attachments/assets/3d3e7d96-d014-47f8-8b0b-566c9c1dfbe0

---

## 🖱 Configuração de pontos

Assista ao vídeo abaixo para ver como configurar a localização dos pontos de cliques do mouse na automação

https://github.com/user-attachments/assets/f71c4b0b-e39f-4b9d-b266-e798db05aa3c

---

## 📐 Arquitetura do Sistema

1. **Extensão Web (Chrome/Edge):** Lê as notas do Google Keep e envia a lista de códigos para a API Python via requisição HTTP POST (`http://127.0.0.1:8000/update`).
2. **Servidor Python (`servidor_keep.py`):** Servidor HTTP leve em segundo plano que recebe os códigos e atualiza dinamicamente o arquivo `codigos.txt` na pasta configurada do projeto.
3. **Painel de Configuração (`painel_control.py`):** Interface gráfica em Python/Tkinter para gerenciamento de diretórios, escolha da impressora padrão e calibração das coordenadas da tela (1 a 8).
4. **Script do AutoHotkey (`impressao_1707.ahk`):** Robô de automação com janela nativa de monitoramento de status. Executa o ciclo de digitação, confirmação, envio de comandos para visualização e impressão em lote no WinThor.

---

##  Estrutura de Arquivos

* `impressao_1707.ahk` — Script principal do AutoHotkey (automação e interface nativa de status).
* `servidor_keep.py` — Servidor HTTP local sem dependências externas (biblioteca nativa `http.server`).
* `painel_control.py` — Interface gráfica para calibração de coordenadas e gerenciamento do projeto.
* `config.json` — Arquivo de configuração dinâmico (caminhos, parâmetros e coordenadas $X, Y$).
* `codigos.txt` — Arquivo de texto gerado automaticamente com a lista de códigos para processamento.
* `extension_winthor/` — Pasta contendo a extensão do Chrome (`manifest.json`, `background.js`, `content.js`).
* `Iniciar tudo.bat` — Atalho para execução diária rápida em segundo plano.
* `Configurar Painel.bat` — Atalho para abrir o painel de calibração do ponteiro e configurações.
* `Encerrar tudo.bat` — Utilitário para finalizar todas as instâncias em memória e resetar o sistema.

---

##  Como Usar no Dia a Dia

### 1. Iniciar o Sistema
* Dê um duplo clique no arquivo **`Iniciar tudo.bat`**.
* O servidor Python será carregado silenciosamente em segundo plano (`pythonw`) e a janela de monitoramento do AutoHotkey surgirá na tela.

### 2. Sincronizar os Produtos pelo Google Keep
* Abra o [Google Keep](https://keep.google.com/) no navegador.
* Abra ou crie uma nota contendo a lista dos códigos de produto (ex: nota com o título **WinThor**).
* A extensão exibirá o indicador **`🟢 WinThor Sync: Ativo`** e atualizará o arquivo `codigos.txt` automaticamente.

### 3. Executar a Impressão em Lote
1. Deixe a **Rotina 1707** aberta no WinThor (preferencialmente maximizada).
2. Pressione a tecla **`F2`** no teclado.
3. Selecione o tipo de impressora no pop-up do AHK (**WMS 2** ou **Universal Printer**).
4. O robô assumirá o controle e processará todos os códigos da lista sequencialmente.

---

## ⌨️ Teclas de Atalho (Hotkeys)

| Tecla | Função |
| :---: | :--- |
| **`F1`** | **Pausar / Retomar** a automação em tempo real. |
| **`F2`** | **Iniciar** o processamento em lote dos códigos salvos. |
| **`F3`** | **Fechar / Encerrar** o script do AutoHotkey. |
| **`F4`** | **Processar texto da área de transferência** (Clipboard) manualmente para `codigos.txt`. |

---

##  Calibração de Coordenadas (Apenas se mudar de monitor/resolução)

Se você mudar a resolução da tela ou mover a janela do WinThor:
1. Feche os serviços correntes com o **`Encerrar tudo.bat`**.
2. Abra o **`Configurar Painel.bat`**.
3. Selecione a pasta do projeto atualizada e clique em **Configurar Localização do Ponteiro**.
4. Escolha o ponto desejado (1 a 8), clique em **Ativar Captura** e clique com o **botão direito do mouse** sobre o alvo na tela do WinThor. Um sinal sonoro confirmará a gravação.
5. Clique em **💾 Salvar Configurações no Projeto**.

---

##  Solução de Problemas Rápidos

* **Extensão exibindo "Servidor Python desligado":** Execute o `Encerrar tudo.bat`, depois o `Iniciar tudo.bat` e pressione `F5` na aba do Google Keep.
* **Coordenadas clicando no lugar errado:** Certifique-se de que a janela do WinThor está maximizada no mesmo monitor onde as coordenadas foram salvas.
* **Processos presos em segundo plano:** Clique duas vezes em `Encerrar tudo.bat` para fechar todas as instâncias do Python e AutoHotkey presas na memória.

---

# Projeções
* O intuito é conseguir automatizar o processo sendo totalmente em 2° plano, de forma que não atrapalhe outras tarefas enquanto a impressão fique em segundo plano
* O problema: o WinThor é ultilizado de forma remota, ou seja, ele projeta um pc dentro do pc com apenas a função do WinThor. Isso dificulta a automação já que, não é possível ultilizar o pc remoto e apenas o WinThor, além disso ele precisaria de permissões de ADM para uso melhor e testes, e isso dentro da rede corporativa as vezes não é possível.
