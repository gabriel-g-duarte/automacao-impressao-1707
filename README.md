# AUT_1707 — Automação de Impressão em Lote (WinThor 1707) <img width="1024" height="1024" alt="icone" src="https://github.com/user-attachments/assets/e299755d-1fe5-47c3-83e5-92a05cde71a8" />


Sistema de automação inteligente desenvolvido para capturar códigos de produtos a partir de notas do **Google Keep** (via extensão de navegador), sincronizá-los com um servidor local e realizar a impressão automática em lote na **Rotina 1707 do ERP WinThor** (Ambiente Remoto) utilizando **AutoHotkey v2.0** e **Python (pywebview + Flask)**.

> ⚠️ **Aviso Importante:** A automação assume o controle do mouse e teclado durante o ciclo de impressão. Deixe o computador livre enquanto o robô estiver em execução para evitar falhas.

---

## 📥 Downloads e Instalação

1. **AutoHotkey v2.0:** Faça o download e instale a versão mais recente em [autohotkey.com](https://www.autohotkey.com/).
2. **Pacote da Automação:** Baixe o arquivo `automacao-impressao.zip` na seção de **Releases** mais recente do repositório e extraia na pasta desejada.

---

## 📐 Arquitetura do Sistema

```
[Google Keep] ──(HTTP POST)──> [Servidor Flask Python] ──(Salva)──> [codigos.csv]
                                       │                                  │
                                (Executa em Thread)               (Lido pelo AHK)
                                       │                                  │
                                [AUT_1707.exe] ──(IPC Memória)──> [impressao_1707.ahk] ──> [WinThor 1707]

```

1. **Extensão Web (`extension_winthor`):** Extensão leve para Chrome/Edge que captura sequências numéricas de produtos do Google Keep e envia diretamente via HTTP POST para `http://localhost:5000/api/codigos` (sem Service Workers intermediários para evitar instabilidades).
2. **Servidor Local Python (`servidor_keep.py`):** Servidor Flask em segundo plano integrado ao aplicativo principal, responsável por receber os códigos e atualizar o arquivo `codigos.csv`.
3. **Painel de Controle e Monitor (`AUT_1707.exe`):** Aplicativo gráfico (`pywebview`) para gerenciamento do sistema, inicialização de processos, calibração de coordenadas $X, Y$ e exibição do painel de monitoramento de status em tempo real.
4. **Robô AutoHotkey (`impressao_1707.ahk`):** Script responsável pela automação de cliques, digitação, troca de impressora e tratamento de pop-ups no WinThor. Transmite o status para o painel via janela oculta em memória (IPC).

---

## 📂 Estrutura de Arquivos

```
AUT_1707/
├── AUT_1707.exe           # Aplicativo principal de controle e gerenciamento
├── _internal/             # Módulos compilados e dependências (PyInstaller --onedir)
├── impressao_1707.ahk     # Script robô do AutoHotkey v2
├── servidor_keep.py       # Servidor Flask local para recebimento do Keep
├── config.json            # Configurações de coordenadas, caminhos e impressora
├── codigos.csv            # Lista de códigos atualizada para processamento
├── index.html             # Interface gráfica do painel de controle
├── monitor.html           # Janela de status em tempo real
└── extension_winthor/     # Extensão para o navegador (manifest.json, content.js)

```
---

## 📺 Vídeo Tutorial (Passo a Passo)

Assista ao vídeo abaixo para ver a demonstração prática do funcionamento e o guia de configuração de todo o ecossistema:

https://github.com/user-attachments/assets/e0f92657-8802-41ba-a04e-c22647c0be6b

---

## 🖱 Configuração de pontos

Assista ao vídeo abaixo para ver como configurar a localização dos pontos de cliques do mouse na automação

https://github.com/user-attachments/assets/fc80860b-efd2-4e37-90d8-339cef59c470

---

## Exemplo de digitalização pro keep

Assista ao vídeo para ver um exemplo de como se pode digitalizar e enviar para o google keep

https://github.com/user-attachments/assets/0f0cfbe4-fb7c-4957-9b37-68f85356d64c

---

## 🚀 Como Utilizar (Passo a Passo)

### 1. Inicialização do Sistema

1. Abra a pasta do projeto e execute o **`AUT_1707.exe`**.
2. Clique no botão **`Iniciar Tudo`** para ativar o servidor de sincronização do Keep.
3. Clique em **`Abrir Script AHK`** para carregar o robô e abrir a janela flutuante do **Monitor de Impressão**.

### 2. Sincronização via Google Keep

1. Acesse o [Google Keep](https://keep.google.com/) no navegador.
2. Abra ou crie uma nota contendo a lista dos códigos dos produtos.
* *Dica:* Cada código deve ficar no início de uma linha. Exemplo de digitalização pela câmera do iPhone/Android: copie o texto digitalizado e cole diretamente na nota do Keep.


3. O indicador **`🟢 WinThor Sync: Ativo`** surgirá no canto inferior da página, sincronizando os códigos diretamente com o arquivo `codigos.csv`.

### 3. Executando a Impressão em Lote

1. Deixe a **Rotina 1707** aberta no WinThor (preferencialmente maximizada no monitor configurado).
2. Pressione a tecla **`F2`** no teclado.
3. Selecione o modo de impressão no pop-up:
* **Impressão Direta:** Envia direto para a impressora padrão configurada na rotina (método mais rápido).
* **Universal Printer:** Utiliza o fluxo com o software da impressora universal (método mais lento).


4. O robô assumirá o controle do teclado/mouse e processará cada código sequencialmente.

---

## 📊 Relatórios Automáticos de Faltas/Impressão

* Toda impressão concluída é registrada automaticamente em um relatório `.csv`.
* O caminho base pode ser definido no painel em **Configurar Painel**.
* O sistema cria automaticamente uma estrutura organizada de pastas:
`.../Relatorios_ANO/Relatorio_MES_ANO.csv` (Exemplo: `Relatorios_2026/Relatorio_10_2026.csv`).
* Contém as colunas: **`CODIGO;DATA;HORARIO`**, pronto para abertura no Microsoft Excel ou Google Planilhas.

---

## ⌨️ Teclas de Atalho (Hotkeys)

| Tecla | Função |
| --- | --- |
| **`F1`** | **Pausar / Retomar** a automação em tempo real. |
| **`F2`** | **Iniciar** o processamento em lote dos códigos sincronizados. |
| **`F3`** | **Fechar / Encerrar** o script do AutoHotkey. |
| **`F4`** | **Importar Códigos do Clipboard:** Converte qualquer texto copiado com números em `codigos.csv`. |

---

## 📐 Calibração de Coordenadas (Mudança de Monitor/Resolução)

Se alterar a resolução do monitor ou mover a janela do WinThor:

1. No **`AUT_1707.exe`**, clique em **Configurar Painel**.
2. Clique no botão **Capturar** ao lado do campo que deseja recalibrar (a janela será minimizada).
3. Posicione o cursor do mouse sobre o campo/botão desejado na tela do WinThor e **clique com o Botão Direito**.
4. As coordenadas $X, Y$ serão atualizadas automaticamente.
5. Clique em **💾 Salvar Configurações no Projeto**.

---

## 🛠️ Solução de Problemas Rápidos

* **Extensão indicando "Servidor Python desligado!":** Abra o `AUT_1707.exe` e confirme se clicou em **Iniciar Tudo**. Se necessário, clique em **Encerrar Tudo** e em seguida em **Iniciar Tudo**.
* **Extensão com mensagem "Extensão recarregada! Pressione F5":** Pressione a tecla `F5` na aba do Google Keep para atualizar a conexão do script na página.
* **Cliques fora do alvo no WinThor:** Verifique se a janela da Rotina 1707 está maximizada na mesma resolução de tela onde a calibração foi efetuada.
* **Processo AHK preso:** O botão **Encerrar Tudo** no aplicativo fecha especificamente o script `impressao_1707.ahk` sem afetar outros scripts AHK em execução no computador.

---

## 🔮 Projeções de Desenvolvimento

* **Execução em Segundo Plano Ativa:** Pesquisa de soluções para interação via envio de mensagens diretas de controle (`ControlClick` / `ControlSend`) nas janelas do ambiente remoto do WinThor, permitindo que o operador continue utilizando o computador durante a impressão.
* **Tratamento Avançado de Exceções:** Identificação e desvio automático de bloqueios cadastrais ou de estoque na rotina 1707 sem interromper a fila de impressão.

---

## 📞 Suporte e Contato

Em caso de dúvidas, sugestões ou problemas na operação:

* **E-mail Corporativo:** gabriel.duarte@dellys.com.br
* **Microsoft Teams:** D8059GD@dellys.com.br / gabriel.duarte@dellys.com.br
* **E-mail Pessoal:** gabrieldgad2007@gmail.com
