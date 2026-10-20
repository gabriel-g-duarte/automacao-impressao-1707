# Tutorial de downloads
* Instale o python em https://www.python.org/downloads/ na versão mais recente. Ao executar a instalação do .exe, baixe em PATH, esta opção aparece durante a instalação e confirme o mesmo em PATH.
* Instale o AutoHotkey em https://www.autohotkey.com/ na versão mais recente
* Baixe o arquivo automacao-impressao.zip em realeses, baixe a versão mais recente e siga os próximos passos

---

# Em caso de dúvidas ou problemas durante o uso 
* Entrar em contato pelo e-mail ou pelo microsoft teams: gabriel.duarte@dellys.com.br / D8059GD@dellys.com.br / gabrieldgad2007@gmail.com

---

# 🖨️ Automação de Impressão em Lote — WinThor (Rotina 1707)

* Sistema de automação inteligente desenvolvido para capturar códigos de produtos a partir de notas do **Google Keep** (via extensão de navegador) e realizar a impressão automática na **Rotina 1707 do ERP WinThor** utilizando **AutoHotkey v2.0** e **Python**.
* Aviso: cliques e digitação automatizados controlam o mouse e o teclado. Deixe o computador livre para evitar falhas no processo de automação.

---

# Função de relatório

* Agora o sistema possui uma função de relatório, salvando a lista de códigos impressos junto com horário e data. Esses são salvos em .csv podendo ser executador por excel para visualização da lista.
* É possível selecionar o local para salvar os mesmos, na função `Configurar Painel.exe`
* Ao selecionar uma pasta ele irá criar uma subpasta referente ao ano atual. Nessa subpasta ele irá criar um arquivo .csv para o mês atual, e cria para cada outro mês que estiver. A escolha do arquivo .csv é pela maior velocidade de salvamento, e esta função de relatório possibilita exportar os dados. Fazendo com que o usuário escolha como ele prefere usar estes dados.

---

# Como ultilizar?

* O uso recomendado é digitalizar a lista de codigos completa, ultilizando um aplicativo ou a própia câmera ex.: a câmera do iPhone tem essa digitalização própia: digitalize, copie o texto e cole na nota do keep (ele detecta automáticamento o código no início de cada linha, e para uso funcional o código precisa ficar no início de cada linha. Códigos fora de cada linhas pode acarretar em possíveis erros no envio dos códigos para os arquivos).
* Outros usos possíveis: modificar o a lista de códigos pela nota do keep, no computador. Modificar o arquivo codigos.txt mantendo cada código em cada linha.

---

## 📺 Vídeo Tutorial (Passo a Passo)

Assista ao vídeo abaixo para ver a demonstração prática do funcionamento e o guia de configuração de todo o ecossistema:

https://github.com/user-attachments/assets/e0f92657-8802-41ba-a04e-c22647c0be6b

---

## 🖱 Configuração de pontos

Assista ao vídeo abaixo para ver como configurar a localização dos pontos de cliques do mouse na automação

https://github.com/user-attachments/assets/fc80860b-efd2-4e37-90d8-339cef59c470

---

## 📐 Arquitetura do Sistema

1. **Extensão Web (Chrome/Edge):** Lê as notas do Google Keep e envia a lista de códigos para a API Python via requisição HTTP POST (`http://127.0.0.1:8000/update`).
2. **Servidor Python (`servidor_keep.py`):** Servidor HTTP leve em segundo plano que recebe os códigos e atualiza dinamicamente o arquivo `codigos.txt` na pasta configurada do projeto.
3. **Painel de Configuração (`painel_control.py`):** Interface gráfica em Python/Tkinter para gerenciamento de diretórios, escolha da impressora padrão e calibração das coordenadas da tela (1 a 9).
4. **Script do AutoHotkey (`impressao_1707.ahk`):** Robô de automação com janela nativa de monitoramento de status. Executa o ciclo de digitação, confirmação, envio de comandos para visualização e impressão em lote no WinThor.

---

##  Estrutura de Arquivos

* `impressao_1707.ahk` — Script principal do AutoHotkey (automação e interface nativa de status).
* `servidor_keep.py` — Servidor HTTP local sem dependências externas (biblioteca nativa `http.server`).
* `painel_control.py` — Interface gráfica para calibração de coordenadas e gerenciamento do projeto.
* `config.json` — Arquivo de configuração dinâmico (caminhos, parâmetros e coordenadas $X, Y$).
* `codigos.txt` — Arquivo de texto gerado automaticamente com a lista de códigos para processamento.
* `extension_winthor/` — Pasta contendo a extensão do Chrome (`manifest.json`, `background.js`, `content.js`).
* `Iniciar tudo.exe` — Atalho para execução diária rápida em segundo plano.
* `Configurar Painel.exe` — Atalho para abrir o painel de calibração do ponteiro e configurações.
* `Encerrar tudo.exe` — Utilitário para finalizar todas as instâncias em memória e resetar o sistema.

---

## Dia-a-Dia

### 1. Iniciar o Sistema
* Dê um duplo clique no arquivo **`Iniciar tudo.exe`**.
* O servidor Python será carregado silenciosamente em segundo plano (`pythonw`) e a janela de monitoramento do AutoHotkey surgirá na tela.
* Caso opcional: minimizar ou fechar a janela de monitoramento não intefere em como ele será executado. Esse ainda ficará ativo em segundo plano. Caso seja necessário finalizar o script: pressione F3

### 2. Sincronizar os Produtos pelo Google Keep
* Abra o [Google Keep](https://keep.google.com/) no navegador.
* Abra ou crie uma nota contendo a lista dos códigos de produto (ex: nota com o título **WinThor**).
* A extensão exibirá o indicador **`🟢 WinThor Sync: Ativo`** e atualizará o arquivo `codigos.txt` automaticamente.

### 3. Executar a Impressão em Lote
1. Deixe a **Rotina 1707** aberta no WinThor (preferencialmente maximizada).
2. Pressione a tecla **`F2`** no teclado.
3. Selecione o tipo de impressão no pop-up do AHK (**Impressão Direta** ou **Universal Printer**).

3.1. Impressão Direta: imprime de acordo com a sua impressora padrão, localizada na lista de impressoras da rotina 1707 ao imprimir (Processo mais rápido).

3.2. Universal Printer: imprime ultilizando a impressora universal que abre um software própio e seleciona automáticamente sua impressora padrão (Processo mais lento).

4. O robô assumirá o controle e processará todos os códigos da lista sequencialmente.

---

## ⌨️ Teclas de Atalho (Hotkeys)

| Tecla | Função |
| :---: | :--- |
| **`F1`** | **Pausar / Retomar** a automação em tempo real. |
| **`F2`** | **Iniciar** o processamento em lote dos códigos salvos. |
| **`F3`** | **Fechar / Encerrar** o script do AutoHotkey. |

---

##  Calibração de Coordenadas (Apenas se mudar de monitor/resolução)

Se você mudar a resolução da tela ou mover a janela do WinThor:
1. Feche os serviços correntes com o **`Encerrar tudo.exe`**.
2. Abra o **`Configurar Painel.exe`**.
3. Ao lado de cada localização do ponteiro basta clicar **Capturar** para ativar a opção de salvar o posicionamento. A janela do painel de controle é minimizada para captura.
4. Posicione o mouse no lugar desejado e clique com o botão direito, nesse momento o painel de controle volta e altera as coordenadas desejadas.
5. Clique em **💾 Salvar Configurações no Projeto**.

---

##  Solução de Problemas Rápidos

* **Extensão exibindo "Servidor Python desligado":** Execute o `Encerrar tudo.exe`, depois o `Iniciar tudo.exe` e pressione `F5` na aba do Google Keep.
* **Coordenadas clicando no lugar errado:** Certifique-se de que a janela do WinThor está maximizada no mesmo monitor onde as coordenadas foram salvas.
* **Processos presos em segundo plano:** Clique duas vezes em `Encerrar tudo.exe` para fechar todas as instâncias do Python e AutoHotkey presas na memória.

---

# Projeções
* O intuito é conseguir automatizar o processo sendo totalmente em 2° plano, de forma que não atrapalhe outras tarefas enquanto a impressão fique em segundo plano
* O problema: o WinThor é ultilizado de forma remota, ou seja, ele projeta um pc dentro do pc com apenas a função do WinThor. Isso dificulta a automação já que, não é possível ultilizar o pc remoto e apenas o WinThor, além disso ele precisaria de permissões de ADM para uso melhor e testes, e isso dentro da rede corporativa as vezes não é possível.
