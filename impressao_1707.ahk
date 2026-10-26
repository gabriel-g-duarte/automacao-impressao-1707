; =====================================================================
;  AUTOMAÇÃO DE IMPRESSÃO EM LOTE - WinThor 1707 (COM JANELA OCULTA DE IPC)
; =====================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force
SetTitleMatchMode(2)

; --------------------- JANELA INVISÍVEL DE DADOS ---------------------
global JanelaOcultaStatus := Gui("-Caption +ToolWindow", "AUT1707_DATA|aguardando|0|-|none")
JanelaOcultaStatus.Hide()

; --------------------- CONFIGURAÇÕES DE JANELAS ---------------------
global JanelaTarget             := "1707 - Consultas Auxiliares - Consultar Produtos (Remoto)" 
global TitulosVisualizacao     := ["Visualizando Impressão (Remoto)", "Visualizando Impressão"]     
global TitulosInformacao       := ["Informação (Remoto)", "Informação", "Information"]
global TitulosAtencao          := ["Atenção (Remoto)", "Atenção", "Attention"]
global TitulosProgresso        := ["Imprimindo (Remoto)", "Imprimindo", "Printing"]

; --------------------- COORDENADAS PADRÃO ---------------------
global CampoCodigo_X            := 2255
global CampoCodigo_Y            := 76
global BotaoImprimir2_X         := 1937           
global BotaoImprimir2_Y         := 35
global BotaoTrocarImpressora_X  := 2773        
global BotaoTrocarImpressora_Y  := 314
global ImpressoraWMS2_X         := 2785
global ImpressoraWMS2_Y         := 444
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
global ArquivoCodigos           := A_ScriptDir "\codigos.csv"
global impressoraPadrao         := ""
global PastaRelatorioFaltasGlobal := ""
global PastaAutomacaoGlobal     := A_ScriptDir
global UltimaModificacao        := ""
global PrimeiraExecucao         := true

CarregarConfiguracao()
SetTimer(MonitorarArquivoCodigos, 2000)

; --------------------- TECLAS DE ATALHO ---------------------
F1::AlternarPausa()             
F2::IniciarProcessamento(false) 
F3::ExitApp()                    
F4::ProcessarTextoClipboard()  

; =====================================================================
;  FUNÇÃO DE ATUALIZAÇÃO VIA MEMÓRIA (JANELA OCULTA)
; =====================================================================

AtualizarStatus(status, codigoAtual:="-", totalProc:=0, temErro:=false, codErro:="", msgErro:="") {
    global JanelaOcultaStatus
    totalVal := Number(totalProc)
    codClean := StrReplace(codigoAtual, "|", "-")
    msgClean := StrReplace(msgErro, "|", "-")
    if (msgClean = "")
        msgClean := "none"
    
    ; Formato transmitido: AUT1707_DATA|status|total|codigo|mensagem
    tituloPayload := "AUT1707_DATA|" . status . "|" . totalVal . "|" . codClean . "|" . msgClean
    
    if IsObject(JanelaOcultaStatus) {
        WinSetTitle(tituloPayload, JanelaOcultaStatus.Hwnd)
    }
}

; =====================================================================
;  FUNÇÕES DE DETECÇÃO
; =====================================================================

VerificarJanelaExata(listaTitulosExatos) {
    prevMode := A_TitleMatchMode
    SetTitleMatchMode(3)
    hwndEncontrado := 0
    for t in listaTitulosExatos {
        if (WinExist(t)) {
            hwndEncontrado := WinExist(t)
            break
        }
    }
    SetTitleMatchMode(prevMode)
    return hwndEncontrado
}

ExisteAlgumaJanela(listaTitulos) {
    for t in listaTitulos {
        if WinExist(t)
            return true
    }
    return false
}

AguardarJanelaFecharRapido(hwnd, timeoutSegundos := 10) {
    if (!hwnd)
        return
    inicio := A_TickCount
    limiteMs := timeoutSegundos * 1000
    while (WinExist("ahk_id " . hwnd) && (A_TickCount - inicio) < limiteMs) {
        Sleep(10)
    }
}

ObterJanelaTop() {
    global JanelaTarget, TitulosAtencao, TitulosInformacao, TitulosVisualizacao, TitulosProgresso

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
    
    hwndUniv := VerificarJanelaExata(["Imprimir", "Print", "Universal Printer"])
    if (hwndUniv)
        return "ahk_id " . hwndUniv

    hwndImp := VerificarJanelaExata(["Imprimir (Remoto)", "Print (Remoto)"])
    if (hwndImp)
        return "ahk_id " . hwndImp

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

PedirImpressora() {
    global impressoraPadrao
    CarregarConfiguracao()
    
    escolha := ""
    nomeImpressoraConfigurada := (impressoraPadrao != "" && impressoraPadrao != "Universal") ? impressoraPadrao : "Direta"
    
    dlg := Gui("+AlwaysOnTop -MinimizeBox -MaximizeBox +ToolWindow", "Modo de Impressão")
    dlg.BackColor := "0D2130"
    dlg.SetFont("s10 bold", "Segoe UI")
    dlg.Add("Text", "w280 Center cFFFFFF", "Selecione o modo de impressão:")
    
    dlg.SetFont("s9 bold", "Segoe UI")
    btn1 := dlg.Add("Button", "w280 h35", "1 - Impressão Direta (" . nomeImpressoraConfigurada . ")")
    btn1.OnEvent("Click", (*) => (escolha := nomeImpressoraConfigurada, dlg.Destroy()))
    
    btn2 := dlg.Add("Button", "w280 h35", "2 - Universal Printer")
    btn2.OnEvent("Click", (*) => (escolha := "Universal", dlg.Destroy()))
    
    dlg.Show("AutoSize Center")
    WinWaitClose(dlg)
    
    if (escolha != "") {
        impressoraPadrao := escolha
        return true
    }
    return false
}

MonitorarArquivoCodigos() {
    global ArquivoCodigos, UltimaModificacao, AutoIniciarAoMudar, PastaAutomacaoGlobal
    pastaLocal := (PastaAutomacaoGlobal != "" && DirExist(PastaAutomacaoGlobal)) ? PastaAutomacaoGlobal : A_ScriptDir
    
    if FileExist(pastaLocal "\codigos.csv")
        caminhoAlvo := pastaLocal "\codigos.csv"
    else if FileExist(pastaLocal "\codigos.txt")
        caminhoAlvo := pastaLocal "\codigos.txt"
    else
        caminhoAlvo := pastaLocal "\codigos.csv"

    if (!AutoIniciarAoMudar || !FileExist(caminhoAlvo))
        return

    mTime := FileGetTime(caminhoAlvo, "M")
    if (UltimaModificacao == "") {
        UltimaModificacao := mTime
        return
    }
    if (mTime != UltimaModificacao) {
        UltimaModificacao := mTime
        ArquivoCodigos := caminhoAlvo
        IniciarProcessamento(true)
    }
}

CarregarConfiguracao() {
    global ArquivoCodigos, Timeout, PastaRelatorioFaltasGlobal, PastaAutomacaoGlobal, JanelaTarget, AutoIniciarAoMudar, impressoraPadrao
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

            if RegExMatch(txt, '"PASTA_AUTOMACAO"\s*:\s*"([^"]+)"', &m)
                PastaAutomacaoGlobal := StrReplace(m[1], "\\", "\")
            if RegExMatch(txt, '"PASTA_RELATORIO_FALTAS"\s*:\s*"([^"]+)"', &m)
                PastaRelatorioFaltasGlobal := StrReplace(m[1], "\\", "\")
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

    pastaLocal := (PastaAutomacaoGlobal != "" && DirExist(PastaAutomacaoGlobal)) ? PastaAutomacaoGlobal : A_ScriptDir
    if FileExist(pastaLocal "\codigos.csv")
        ArquivoCodigos := pastaLocal "\codigos.csv"
    else if FileExist(pastaLocal "\codigos.txt")
        ArquivoCodigos := pastaLocal "\codigos.txt"
    else
        ArquivoCodigos := pastaLocal "\codigos.csv"
}

AlternarPausa() {
    static pausado := false
    pausado := !pausado
    Pause(pausado)
    ToolTip(pausado ? "Script Pausado" : "Script Ativo")
    SetTimer(() => ToolTip(), -2000)
}

ProcessarTextoClipboard() {
    global ArquivoCodigos, PastaAutomacaoGlobal
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
        pastaLocal := (PastaAutomacaoGlobal != "" && DirExist(PastaAutomacaoGlobal)) ? PastaAutomacaoGlobal : A_ScriptDir
        caminhoDestino := pastaLocal "\codigos.csv"
        if FileExist(caminhoDestino)
            FileDelete(caminhoDestino)
        FileAppend(resultadoLimpo, caminhoDestino, "UTF-8")
        ArquivoCodigos := caminhoDestino
    }
}

RegistrarEmCSV(codigo) {
    global PastaRelatorioFaltasGlobal, PastaAutomacaoGlobal
    
    dataAtual := FormatTime(, "dd/MM/yyyy")
    horaAtual := FormatTime(, "HH:mm:ss")
    anoAtual  := FormatTime(, "yyyy")
    mesAtual  := FormatTime(, "MM")
    
    pastaBase := (PastaRelatorioFaltasGlobal != "" && DirExist(PastaRelatorioFaltasGlobal)) ? PastaRelatorioFaltasGlobal : PastaAutomacaoGlobal
    pastaAno  := pastaBase "\Relatorios_" . anoAtual
    
    if !DirExist(pastaAno)
        DirCreate(pastaAno)
        
    arquivoCSV := pastaAno "\Relatorio_" . mesAtual . "_" . anoAtual . ".csv"
    
    if !FileExist(arquivoCSV) {
        FileAppend("CODIGO;DATA;HORARIO`n", arquivoCSV, "UTF-8")
    }
    
    linha := codigo . ";" . dataAtual . ";" . horaAtual . "`n"
    FileAppend(linha, arquivoCSV, "UTF-8")
}

; =====================================================================
;  ROTINA PRINCIPAL DE IMPRESSÃO
; =====================================================================

IniciarProcessamento(ehAutomatico := false) {
    global impressoraPadrao, ArquivoCodigos, JanelaTarget, PrimeiraExecucao
    CarregarConfiguracao()

    if !WinExist(JanelaTarget) {
        if (!ehAutomatico)
            MsgBox("A janela do WinThor não foi encontrada!")
        return
    }

    if (!ehAutomatico || PrimeiraExecucao) {
        if (!PedirImpressora())
            return
        PrimeiraExecucao := false
    }

    if !FileExist(ArquivoCodigos) {
        if (!ehAutomatico)
            MsgBox("O arquivo de códigos não foi encontrado na pasta local (`codigos.csv` ou `codigos.txt`)!")
        return
    }

    try {
        conteudo := FileRead(ArquivoCodigos, "UTF-8")
    } catch {
        conteudo := FileRead(ArquivoCodigos)
    }

    linhas := StrSplit(conteudo, "`n", "`r")
    listaCodigos := []

    for linha in linhas {
        linhaLimpa := Trim(linha)
        if (linhaLimpa == "" || RegExMatch(linhaLimpa, "i)^cód|^codigo|^code"))
            continue

        partes := StrSplit(linhaLimpa, [";", ","])
        codigo := Trim(partes[1], " `t`r`n`"")

        if (codigo != "")
            listaCodigos.Push(codigo)
    }

    total := listaCodigos.Length
    if (total == 0) {
        if (!ehAutomatico)
            MsgBox("Nenhum código válido foi encontrado no arquivo!")
        return
    }

    contador := 0
    for codigo in listaCodigos {
        contador++
        AtualizarStatus("imprimindo", codigo, contador)

        if !ProcessarCodigoDireto(codigo, contador, total) {
            AtualizarStatus("erro", codigo, contador - 1, true, codigo, "Falha durante o ciclo de impressao.")
            return
        }

        RegistrarEmCSV(codigo)

        AtualizarStatus("imprimindo", codigo, contador)
        Sleep(50)
    }

    AtualizarStatus("concluido", "Concluído", contador)
}

; =====================================================================
;  PROCESSA UM CÓDIGO
; =====================================================================

ProcessarCodigoDireto(codigo, contador := 1, total := 1) {
    global impressoraPadrao, JanelaTarget, TitulosVisualizacao, TitulosInformacao, TitulosAtencao, TitulosProgresso
    global CampoCodigo_X, CampoCodigo_Y, BotaoImprimir2_X, BotaoImprimir2_Y
    global BotaoTrocarImpressora_X, BotaoTrocarImpressora_Y, ImpressoraWMS2_X, ImpressoraWMS2_Y
    global BotaoOK_X, BotaoOK_Y, BotaoOK_Informacao_X, BotaoOK_Informacao_Y, BotaoOK_Atencao_X, BotaoOK_Atencao_Y
    global BotaoImprimirUniversal_X, BotaoImprimirUniversal_Y, BotaoFechar_X, BotaoFechar_Y
    global Timeout

    loop 2 {
        deuAtencao := false

        if ExisteAlgumaJanela(TitulosVisualizacao) {
            FocarEclicar(BotaoFechar_X, BotaoFechar_Y)
            Sleep(150)
            for t in TitulosVisualizacao {
                if WinExist(t) {
                    WinActivate(t)
                    Send("{Esc}")
                    Sleep(150)
                }
            }
        }

        if !WinExist(JanelaTarget)
            return false

        WinActivate(JanelaTarget)
        Sleep(100)

        CoordMode("Mouse", "Screen")
        Click(CampoCodigo_X, CampoCodigo_Y, 2)
        Sleep(60)
        Send("^a")
        Sleep(40)
        Send("{BackSpace}")
        Sleep(40)

        SendText(codigo)
        Sleep(60)
        Send("{F5}")

        tempoEsperado := 0
        loop {
            tempoEsperado++
            if (tempoEsperado > Timeout * 20)
                return false

            if ExisteAlgumaJanela(TitulosAtencao) {
                AtualizarStatus("aviso", codigo, contador - 1)
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

        if (deuAtencao) {
            Sleep(10)
            continue
        }

        Sleep(50)

        tempoImp := 0
        hwndSelecao := 0

        while (tempoImp < 350) {
            hwndSelecao := VerificarJanelaExata(["Imprimir (Remoto)", "Print (Remoto)"])
            if (hwndSelecao)
                break

            FocarEclicar(BotaoImprimir2_X, BotaoImprimir2_Y)
            Sleep(400)
            tempoImp++
        }

        if (!hwndSelecao) {
            return false
        }

        WinActivate("ahk_id " . hwndSelecao)
        Sleep(100) 

        if (impressoraPadrao != "Universal") {
            FocarEclicar(BotaoTrocarImpressora_X, BotaoTrocarImpressora_Y)
            Sleep(70) 
            FocarEclicar(ImpressoraWMS2_X, ImpressoraWMS2_Y)
            Sleep(70) 
            FocarEclicar(BotaoOK_X, BotaoOK_Y)
            AguardarJanelaFecharRapido(hwndSelecao, 8)

            tempoProg := 0
            while !ExisteAlgumaJanela(TitulosProgresso) && (tempoProg < 200) {
                tempoProg++
                Sleep(70)
            }

            while ExisteAlgumaJanela(TitulosProgresso) {
                Sleep(70)
            }
        } else {
            FocarEclicar(BotaoOK_X, BotaoOK_Y)
            
            hwndUniv := 0
            loop 40 {
                hwndEncontrado := VerificarJanelaExata(["Imprimir", "Print", "Universal Printer"])
                if (hwndEncontrado && hwndEncontrado != hwndSelecao) {
                    hwndUniv := hwndEncontrado
                    break
                }
                Sleep(50)
            }

            if (hwndUniv) {
                WinActivate("ahk_id " . hwndUniv)
                Sleep(70)
                FocarEclicar(BotaoImprimirUniversal_X, BotaoImprimirUniversal_Y)
                Sleep(150)
            }
        }

        FocarEclicar(BotaoFechar_X, BotaoFechar_Y)
        Sleep(70)

        if ExisteAlgumaJanela(TitulosVisualizacao) {
            FocarEclicar(BotaoFechar_X, BotaoFechar_Y)
            Sleep(70)
        }

        return true
    }

    return false
}