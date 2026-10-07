; =====================================================================
;  AUTOMAÇÃO DE IMPRESSÃO EM LOTE - WinThor 1707 (COM RETRY DE ATENÇÃO)
; =====================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force
SetTitleMatchMode(2)

; --------------------- CONFIGURAÇÕES DE JANELAS E RDP ---------------------

global JanelaTarget          := "1707 - Consultas Auxiliares - Consultar Produtos" 
global TituloPrincipal       := "1707" 

global TitulosVisualizacao   := ["Visualizando Impressão", "View Print", "Print Preview", "Preview", "Visualizando Impressão (Remoto)"]     
global TitulosImpressora     := ["Imprimir", "Print", "Imprimir (Remoto)"]                    
global TitulosUniversal      := ["Imprimir", "Print"]                    
global TitulosInformacao     := ["Informação", "Information", "Inform", "Informação (Remoto)"]
global TitulosAtencao        := ["Atenção", "Attention", "Atenção (Remoto)"]
global TitulosProgresso      := ["Imprimindo", "Printing", "Imprimindo (Remoto)"]

; --------------------- COORDENADAS PADRÃO ---------------------

global CampoCodigo_X            := 2255
global CampoCodigo_Y            := 76
global BotaoImprimir2_X         := 1937           
global BotaoImprimir2_Y         := 35
global BotaoTrocarImpressora_X  := 2773        
global BotaoTrocarImpressora_Y  := 314
global ImpressoraWMS2_X         := 2822           
global ImpressoraWMS2_Y         := 448
global BotaoOK_X                := 2996           
global BotaoOK_Y                := 657
global BotaoOK_Informacao_X     := 2883
global BotaoOK_Informacao_Y     := 554
global BotaoOK_Atencao_X        := 2874
global BotaoOK_Atencao_Y        := 550

global BotaoImprimirUniversal_X := 880
global BotaoImprimirUniversal_Y := 404
global BotaoFechar_X            := 2410
global BotaoFechar_Y            := 35

global Timeout                  := 15
global AutoIniciarAoMudar       := true
global ArquivoCodigos           := A_ScriptDir "\codigos.txt"
global impressoraPadrao         := "WMS2"
global PastaProjetoGlobal       := ""
global UltimaModificacao        := ""

; Variáveis da Janela de Monitoramento
global MonitorGui := ""
global TextStatus := ""
global TextProgresso := ""
global TextErro := ""

CriarJanelaMonitorAHK()
CarregarConfiguracao()
SetTimer(MonitorarArquivoCodigos, 2000)

; --------------------- TECLAS DE ATALHO ---------------------
F1::AlternarPausa()             
F2::IniciarProcessamento(false) 
F3::ExitApp()                    
F4::ProcessarTextoClipboard()  

; =====================================================================
;  FUNÇÕES AUXILIARES
; =====================================================================

ExisteAlgumaJanela(listaTitulos) {
    for t in listaTitulos {
        if WinExist(t)
            return true
    }
    return false
}

ObterJanelaTop() {
    global JanelaTarget, TitulosAtencao, TitulosInformacao, TitulosImpressora, TitulosUniversal, TitulosVisualizacao, TitulosProgresso

    for t in TitulosAtencao {
        if WinExist(t)
            return t
    }
    for t in TitulosInformacao {
        if WinExist(t)
            return t
    }
    for t in TitulosProgresso {
        if WinExist(t)
            return t
    }
    for t in TitulosImpressora {
        if WinExist(t)
            return t
    }
    for t in TitulosUniversal {
        if WinExist(t)
            return t
    }
    for t in TitulosVisualizacao {
        if WinExist(t)
            return t
    }
    if WinExist(JanelaTarget)
        return JanelaTarget

    return "A"
}

FocarEclicar(screenX, screenY, quantidadeCliques := 1) {
    targetWin := ObterJanelaTop()
    if WinExist(targetWin) {
        WinActivate(targetWin)
        CoordMode("Mouse", "Screen")
        Click(screenX, screenY, quantidadeCliques)
    }
}

EnviarTextoDireto(texto) {
    targetWin := ObterJanelaTop()
    if WinExist(targetWin) {
        WinActivate(targetWin)
        Send("{Text}" . texto)
    }
}

EnviarTeclaDireta(tecla) {
    targetWin := ObterJanelaTop()
    if WinExist(targetWin) {
        WinActivate(targetWin)
        Send(tecla)
    }
}

MonitorarArquivoCodigos() {
    global ArquivoCodigos, UltimaModificacao, AutoIniciarAoMudar
    if (!AutoIniciarAoMudar || !FileExist(ArquivoCodigos))
        return
    mTime := FileGetTime(ArquivoCodigos, "M")
    if (UltimaModificacao == "") {
        UltimaModificacao := mTime
        return
    }
    if (mTime != UltimaModificacao) {
        UltimaModificacao := mTime
        IniciarProcessamento(true)
    }
}

CriarJanelaMonitorAHK() {
    global MonitorGui, TextStatus, TextProgresso, TextErro
    MonitorGui := Gui("+Resize", "Painel de Monitoramento - WinThor 1707")
    MonitorGui.SetFont("s10 bold", "Segoe UI")
    MonitorGui.Add("Text", "cGray", "🖨️ Status da Impressão (Modo Direto F5):")
    TextStatus := MonitorGui.Add("Text", "w360 r2 c0056b3", "Aguardando sincronização do Keep ou tecla F2...")
    MonitorGui.SetFont("s9 norm", "Segoe UI")
    TextProgresso := MonitorGui.Add("Text", "w360", "Códigos Processados: 0 / 0")
    MonitorGui.SetFont("s9 bold", "Segoe UI")
    TextErro := MonitorGui.Add("Text", "w360 r2 cRed Hidden", "")
    MonitorGui.Show("x10 y10 w390 h160 NoActivate")
}

AtualizarMonitorAHK(status, codigoAtual:="-", contador:=0, total:=0, msgErro:="") {
    global TextStatus, TextProgresso, TextErro
    if (status = "imprimindo") {
        TextStatus.Value := "Imprimindo Código: " codigoAtual
        TextStatus.Opt("c0056b3")
        TextProgresso.Value := "Progresso: " contador " de " total " processados"
        TextErro.Visible := false
    } else if (status = "aviso") {
        TextStatus.Value := "⚠️ Código juntou/duplicou! Reenviando: " codigoAtual
        TextStatus.Opt("cCa8a04")
        TextProgresso.Value := "Limpando campo e repetindo código " contador " de " total
        TextErro.Visible := false
    } else if (status = "concluido") {
        TextStatus.Value := "✅ Impressão Finalizada!"
        TextStatus.Opt("c28a745")
        TextProgresso.Value := "Total Processado: " total " de " total " códigos"
        TextErro.Visible := false
    } else if (status = "erro") {
        TextStatus.Value := "⚠️ OCORREU UM ERRO!"
        TextStatus.Opt("cCc0000")
        TextProgresso.Value := "Parado no código " contador " de " total
        TextErro.Value := "Erro no Código: " codigoAtual "`nDetalhe: " msgErro
        TextErro.Visible := true
    }
}

CarregarConfiguracao() {
    global ArquivoCodigos, Timeout, PastaProjetoGlobal, JanelaTarget, AutoIniciarAoMudar, impressoraPadrao
    global CampoCodigo_X, CampoCodigo_Y, BotaoImprimir2_X, BotaoImprimir2_Y
    global BotaoTrocarImpressora_X, BotaoTrocarImpressora_Y, ImpressoraWMS2_X, ImpressoraWMS2_Y
    global BotaoOK_X, BotaoOK_Y, BotaoOK_Informacao_X, BotaoOK_Informacao_Y, BotaoOK_Atencao_X, BotaoOK_Atencao_Y
    global BotaoImprimirUniversal_X, BotaoImprimirUniversal_Y, BotaoFechar_X, BotaoFechar_Y

    caminhoConfig := A_ScriptDir "\config.json"
    if FileExist(caminhoConfig) {
        try {
            txt := FileRead(caminhoConfig, "UTF-8")
            GetCoord(chave, valorPadrao) {
                if RegExMatch(txt, '"' chave '"\s*:\s*(\d+)', &m)
                    return Integer(m[1])
                return valorPadrao
            }
            CampoCodigo_X            := GetCoord("CampoCodigo_X", CampoCodigo_X)
            CampoCodigo_Y            := GetCoord("CampoCodigo_Y", CampoCodigo_Y)
            BotaoImprimir2_X         := GetCoord("BotaoImprimir2_X", BotaoImprimir2_X)
            BotaoImprimir2_Y         := GetCoord("BotaoImprimir2_Y", BotaoImprimir2_Y)
            BotaoTrocarImpressora_X  := GetCoord("BotaoTrocarImpressora_X", BotaoTrocarImpressora_X)
            BotaoTrocarImpressora_Y  := GetCoord("BotaoTrocarImpressora_Y", BotaoTrocarImpressora_Y)
            ImpressoraWMS2_X         := GetCoord("ImpressoraWMS2_X", ImpressoraWMS2_X)
            ImpressoraWMS2_Y         := GetCoord("ImpressoraWMS2_Y", ImpressoraWMS2_Y)
            BotaoOK_X                := GetCoord("BotaoOK_X", BotaoOK_X)
            BotaoOK_Y                := GetCoord("BotaoOK_Y", BotaoOK_Y)
            BotaoOK_Informacao_X     := GetCoord("BotaoOK_Informacao_X", BotaoOK_Informacao_X)
            BotaoOK_Informacao_Y     := GetCoord("BotaoOK_Informacao_Y", BotaoOK_Informacao_Y)
            BotaoOK_Atencao_X        := GetCoord("BotaoOK_Atencao_X", BotaoOK_Atencao_X)
            BotaoOK_Atencao_Y        := GetCoord("BotaoOK_Atencao_Y", BotaoOK_Atencao_Y)
            BotaoImprimirUniversal_X := GetCoord("BotaoImprimirUniversal_X", BotaoImprimirUniversal_X)
            BotaoImprimirUniversal_Y := GetCoord("BotaoImprimirUniversal_Y", BotaoImprimirUniversal_Y)
            BotaoFechar_X            := GetCoord("BotaoFechar_X", BotaoFechar_X)
            BotaoFechar_Y            := GetCoord("BotaoFechar_Y", BotaoFechar_Y)

            if RegExMatch(txt, '"PASTA_PROJETO"\s*:\s*"([^"]+)"', &m) {
                PastaProjetoGlobal := StrReplace(m[1], "\\", "\")
                ArquivoCodigos := PastaProjetoGlobal "\codigos.txt"
            }
            if RegExMatch(txt, '"JANELA_TARGET"\s*:\s*"([^"]+)"', &m)
                JanelaTarget := m[1]
            if RegExMatch(txt, '"NOME_IMPRESSORA"\s*:\s*"([^"]+)"', &m)
                impressoraPadrao := m[1]
            if RegExMatch(txt, '"AUTO_INICIAR_AO_MUDAR_TXT"\s*:\s*(true|false)', &m)
                AutoIniciarAoMudar := (m[1] = "true")
            if RegExMatch(txt, '"TIMEOUT"\s*:\s*(\d+)', &m)
                Timeout := Integer(m[1])
        }
    }
}

AtualizarStatus(status, codigoAtual:="-", totalProc:=0, temErro:=false, codErro:="", msgErro:="") {
    global PastaProjetoGlobal
    totalProcessadosVal := Number(totalProc)
    txtJson := '{"status": "' status '", "codigo_atual": "' codigoAtual '", "total_processados": ' totalProcessadosVal ', "erro": ' (temErro ? "true" : "false") ', "codigo_erro": "' codErro '", "mensagem_erro": "' msgErro '"}'
    EscreverArquivoJSON(A_ScriptDir "\status.json", txtJson)
    if (PastaProjetoGlobal != "" && DirExist(PastaProjetoGlobal) && PastaProjetoGlobal != A_ScriptDir) {
        EscreverArquivoJSON(PastaProjetoGlobal "\status.json", txtJson)
    }
}

EscreverArquivoJSON(caminho, conteudo) {
    try {
        fileObj := FileOpen(caminho, "w", "UTF-8")
        if IsObject(fileObj) {
            fileObj.Write(conteudo)
            fileObj.Close()
        }
    }
}

AlternarPausa() {
    static pausado := false
    pausado := !pausado
    Pause(pausado)
    ToolTip(pausado ? "Script PAUSADO" : "Script ATIVO")
    SetTimer(() => ToolTip(), -2000)
}

ProcessarTextoClipboard() {
    global ArquivoCodigos
    textoBruto := A_Clipboard
    if (Trim(textoBruto) = "")
        return
    codigosUnicos := Map()
    resultado := ""
    loop parse, textoBruto, "`n", "`r" {
        if RegExMatch(A_LoopField, "^\s*(\d+)", &match) {
            codigo := match[1]
            if !codigosUnicos.Has(codigo) {
                codigosUnicos[codigo] := true
                resultado .= codigo "`n"
            }
        }
    }
    resultadoLimpo := Trim(resultado, "`n`r")
    if (resultadoLimpo != "") {
        if FileExist(ArquivoCodigos)
            FileDelete(ArquivoCodigos)
        FileAppend(resultadoLimpo, ArquivoCodigos, "UTF-8")
    }
}

; =====================================================================
;  ROTINA PRINCIPAL DE IMPRESSÃO
; =====================================================================

IniciarProcessamento(ehAutomatico := false) {
    global impressoraPadrao, ArquivoCodigos, JanelaTarget
    CarregarConfiguracao()

    if !WinExist(JanelaTarget) {
        if (!ehAutomatico)
            MsgBox("A janela do WinThor não foi encontrada!")
        return
    }

    if !FileExist(ArquivoCodigos)
        return

    conteudo := FileRead(ArquivoCodigos)
    codigos := StrSplit(conteudo, "`n", "`r")

    total := 0
    for codigo in codigos {
        if (Trim(codigo) != "")
            total++
    }

    if (total == 0)
        return

    contador := 0
    for codigo in codigos {
        codigo := Trim(codigo)
        if (codigo = "")
            continue

        contador++
        AtualizarStatus("imprimindo", codigo, contador - 1)
        AtualizarMonitorAHK("imprimindo", codigo, contador, total)

        if !ProcessarCodigoDireto(codigo, contador, total) {
            AtualizarStatus("erro", codigo, contador - 1, true, codigo, "Falha durante o ciclo de impressao.")
            AtualizarMonitorAHK("erro", codigo, contador - 1, total, "Falha durante o ciclo de impressao.")
            return
        }

        AtualizarStatus("imprimindo", codigo, contador)
        Sleep(50)
    }

    AtualizarStatus("concluido", "Concluído", contador)
    AtualizarMonitorAHK("concluido", "-", contador, total)
}

; =====================================================================
;  PROCESSA UM CÓDIGO (COM REPETIÇÃO EM CASO DE ATENÇÃO)
; =====================================================================

ProcessarCodigoDireto(codigo, contador := 1, total := 1) {
    global impressoraPadrao, JanelaTarget, TitulosVisualizacao, TitulosImpressora, TitulosInformacao, TitulosAtencao, TitulosUniversal, TitulosProgresso
    global CampoCodigo_X, CampoCodigo_Y, BotaoImprimir2_X, BotaoImprimir2_Y
    global BotaoTrocarImpressora_X, BotaoTrocarImpressora_Y, ImpressoraWMS2_X, ImpressoraWMS2_Y
    global BotaoOK_X, BotaoOK_Y, BotaoOK_Informacao_X, BotaoOK_Informacao_Y, BotaoOK_Atencao_X, BotaoOK_Atencao_Y
    global BotaoImprimirUniversal_X, BotaoImprimirUniversal_Y, BotaoFechar_X, BotaoFechar_Y
    global Timeout

    loop 2 {
        deuAtencao := false

        ; 1. Foca o campo de código e limpa com Ctrl+A e BackSpace
        FocarEclicar(CampoCodigo_X, CampoCodigo_Y, 2)
        Sleep(50)
        EnviarTeclaDireta("^a")
        Sleep(30)
        EnviarTeclaDireta("{BackSpace}")
        Sleep(30)

        ; 2. Envia o código e chama o F5 diretamente
        EnviarTextoDireto(codigo)
        Sleep(50)
        EnviarTeclaDireta("{F5}")

        ; 3. Aguarda a visualização ou pop-ups abrirem
        tempoEsperado := 0
        loop {
            tempoEsperado++
            if (tempoEsperado > Timeout * 20)
                return false

            if ExisteAlgumaJanela(TitulosAtencao) {
                ; Avisa no painel que o código duplicou/juntou e vai repetir
                AtualizarMonitorAHK("aviso", codigo, contador, total)
                
                ; Clica no botão OK da janela de Atenção (9º clique)
                FocarEclicar(BotaoOK_Atencao_X, BotaoOK_Atencao_Y)
                Sleep(200)
                deuAtencao := true
                break
            }

            if ExisteAlgumaJanela(TitulosInformacao) {
                try {
                    textoPopup := WinGetText(ObterJanelaTop())
                    if InStr(textoPopup, "Informe o código") || InStr(textoPopup, "Enter code") {
                        FocarEclicar(BotaoOK_Informacao_X, BotaoOK_Informacao_Y)
                        Sleep(100)
                        return false
                    }
                }
                FocarEclicar(BotaoOK_Informacao_X, BotaoOK_Informacao_Y)
                Sleep(100)
                return true 
            }

            if ExisteAlgumaJanela(TitulosVisualizacao) {
                break
            }
            Sleep(50)
        }

        ; Se deu janela de Atenção, reinicia o loop para limpar do zero e colar novamente
        if (deuAtencao) {
            Sleep(150)
            continue
        }

        Sleep(50)

        ; 4. Loop do botão Imprimir (0,4s / 400ms)
        tempoImp := 0
        while !ExisteAlgumaJanela(TitulosImpressora) && !ExisteAlgumaJanela(TitulosUniversal) && (tempoImp < 25) {
            tempoImp++
            FocarEclicar(BotaoImprimir2_X, BotaoImprimir2_Y)
            Sleep(400)
        }

        Sleep(50)

        ; 5. Confirmação da impressora
        if (impressoraPadrao = "WMS2" || impressoraPadrao = "WMS 2") {
            FocarEclicar(BotaoTrocarImpressora_X, BotaoTrocarImpressora_Y)
            Sleep(100)
            FocarEclicar(ImpressoraWMS2_X, ImpressoraWMS2_Y)
            Sleep(80)
            FocarEclicar(BotaoOK_X, BotaoOK_Y)
        } else {
            FocarEclicar(BotaoOK_X, BotaoOK_Y)
            Sleep(200)
            if ExisteAlgumaJanela(TitulosUniversal) {
                FocarEclicar(BotaoImprimirUniversal_X, BotaoImprimirUniversal_Y)
            }
        }

        ; 6. Aguarda a janela "Imprimindo" sumir
        tempoProg := 0
        while !ExisteAlgumaJanela(TitulosProgresso) && (tempoProg < 40) {
            tempoProg++
            Sleep(30)
        }

        while ExisteAlgumaJanela(TitulosProgresso) {
            Sleep(30)
        }

        ; 7. Fecha a visualização imediatamente
        FocarEclicar(BotaoFechar_X, BotaoFechar_Y)
        Sleep(100)

        if ExisteAlgumaJanela(TitulosVisualizacao) {
            FocarEclicar(BotaoFechar_X, BotaoFechar_Y)
            Sleep(100)
        }

        return true
    }

    return false
}