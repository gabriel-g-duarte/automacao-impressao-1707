; =====================================================================
;  AUTOMAÇÃO DE IMPRESSÃO EM LOTE - WinThor 1707 (COM REGISTRO EM CSV)
; =====================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force
SetTitleMatchMode(2) ; Modo Parcial por padrão

; --------------------- CONFIGURAÇÕES DE JANELAS ---------------------

global JanelaTarget            := "1707 - Consultas Auxiliares - Consultar Produtos (Remoto)" 
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
global impressoraPadrao         := "WMS2"
global PastaRelatorioFaltasGlobal := ""
global PastaAutomacaoGlobal     := A_ScriptDir
global UltimaModificacao        := ""
global PrimeiraExecucao         := true

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
;  GERADOR DE DEGRADÊ CINZA PARA O CABEÇALHO
; =====================================================================

CriarDegradeBMP(caminho, h := 48) {
    if FileExist(caminho)
        return
    bufSize := 54 + (h * 4)
    buf := Buffer(bufSize, 0)
    
    NumPut("UShort", 0x4D42, buf, 0)
    NumPut("UInt", bufSize, buf, 2)
    NumPut("UInt", 54, buf, 10)
    
    NumPut("UInt", 40, buf, 14)
    NumPut("Int", 1, buf, 18)
    NumPut("Int", -h, buf, 22)
    NumPut("UShort", 1, buf, 26)
    NumPut("UShort", 24, buf, 28)
    NumPut("UInt", h * 4, buf, 34)
    
    c1 := [241, 243, 245]
    c2 := [233, 236, 239]
    offset := 54
    Loop h {
        i := A_Index - 1
        ratio := i / (h - 1)
        r := Round(c1[1] + (c2[1] - c1[1]) * ratio)
        g := Round(c1[2] + (c2[2] - c1[2]) * ratio)
        b := Round(c1[3] + (c2[3] - c1[3]) * ratio)
        
        NumPut("UChar", b, buf, offset)
        NumPut("UChar", g, buf, offset + 1)
        NumPut("UChar", r, buf, offset + 2)
        NumPut("UChar", 0, buf, offset + 3)
        offset += 4
    }
    
    f := FileOpen(caminho, "w")
    f.RawWrite(buf)
    f.Close()
}

; =====================================================================
;  JANELA DE MONITORAMENTO COM DUAS SEÇÕES CENTRALIZADAS
; =====================================================================

CriarJanelaMonitorAHK() {
    global MonitorGui, TextStatus, TextProgresso, TextErro
    
    caminhoBmp := A_ScriptDir "\degrade_header.bmp"
    CriarDegradeBMP(caminhoBmp, 52)

    MonitorGui := Gui("+AlwaysOnTop -MaximizeBox", "Painel de Monitoramento - WinThor 1707")
    MonitorGui.BackColor := "F8F9FA"
    
    MonitorGui.Add("Text", "x14 y14 w416 h195 BackgroundFFFFFF +Border", "")

    if FileExist(caminhoBmp) {
        MonitorGui.Add("Pic", "x15 y15 w414 h50", caminhoBmp)
    } else {
        MonitorGui.Add("Text", "x15 y15 w414 h50 BackgroundF1F3F5", "")
    }

    MonitorGui.SetFont("s11 norm", "Segoe UI")
    MonitorGui.Add("Text", "x28 y21 w388 Center BackgroundTrans c1F2937", "Status da execução")
    
    MonitorGui.SetFont("s9 norm", "Segoe UI")
    MonitorGui.Add("Text", "x28 y43 w388 Center BackgroundTrans c6B7280", "Acompanhamento do processamento em tempo real")

    MonitorGui.Add("Text", "x15 y65 w414 h1 BackgroundE2E8F0", "")

    MonitorGui.SetFont("s10 norm", "Segoe UI")
    TextStatus := MonitorGui.Add("Text", "x28 y76 w388 r2 Center BackgroundFFFFFF c0284C7", "Aguardando início (Pressione F2)...")
    
    MonitorGui.Add("Text", "x28 y122 w388 h1 BackgroundE2E8F0", "")

    MonitorGui.SetFont("s9 norm", "Segoe UI")
    TextProgresso := MonitorGui.Add("Text", "x28 y132 w388 Center BackgroundFFFFFF c4B5563", "Códigos processados: 0 de 0")
    
    TextErro := MonitorGui.Add("Text", "x28 y156 w388 r2 Center BackgroundFFFFFF cDC2626 Hidden", "")

    MonitorGui.Show("x20 y20 w444 h223 NoActivate")
}

AtualizarMonitorAHK(status, codigoAtual:="-", contador:=0, total:=0, msgErro:="") {
    global TextStatus, TextProgresso, TextErro
    if (status = "imprimindo") {
        TextStatus.Value := "Imprimindo código: " codigoAtual
        TextStatus.Opt("c0284C7 Center")
        TextProgresso.Value := "Progresso: " contador " de " total " processados"
        TextErro.Visible := false
    } else if (status = "aviso") {
        TextStatus.Value := "Atenção: Código duplicado ou junta de campo! Reenviando: " codigoAtual
        TextStatus.Opt("cD97706 Center")
        TextProgresso.Value := "Limpando campo e repetindo código " contador " de " total
        TextErro.Visible := false
    } else if (status = "concluido") {
        TextStatus.Value := "Impressão finalizada com sucesso!"
        TextStatus.Opt("c16A34A Center")
        TextProgresso.Value := "Total processado: " total " de " total " códigos"
        TextErro.Visible := false
    } else if (status = "erro") {
        TextStatus.Value := "Ocorreu uma falha na execução"
        TextStatus.Opt("cDC2626 Center")
        TextProgresso.Value := "Parado no código " contador " de " total
        TextErro.Value := "Código com erro: " codigoAtual "`nDetalhe: " msgErro
        TextErro.Visible := true
    }
}

; =====================================================================
;  FUNÇÕES DE DETECÇÃO (MODO EXATO PARA IMPRESSORAS)
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

AguardarJanelaFechar(hwnd, timeoutSegundos := 10) {
    if (!hwnd)
        return
    inicio := A_TickCount
    limiteMs := timeoutSegundos * 1000

    while (WinExist("ahk_id " . hwnd) && (A_TickCount - inicio) < limiteMs) {
        Sleep(100)
    }
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

; =====================================================================
;  FUNÇÕES DE ARQUIVO E INTERFACE DE SELEÇÃO DE IMPRESSORA
; =====================================================================

SalvarImpressoraConfig(modo) {
    caminhoConfig := A_ScriptDir "\config.json"
    if FileExist(caminhoConfig) {
        txt := FileRead(caminhoConfig, "UTF-8")
        txt := RegExReplace(txt, '("NOME_IMPRESSORA"\s*:\s*)"[^"]+"', '$1"' modo '"')
        try {
            fileObj := FileOpen(caminhoConfig, "w", "UTF-8")
            fileObj.Write(txt)
            fileObj.Close()
        }
    }
}

PedirImpressora() {
    global impressoraPadrao
    escolha := ""
    
    dlg := Gui("+AlwaysOnTop -MinimizeBox -MaximizeBox +ToolWindow", "Modo de Impressão")
    dlg.BackColor := "F8F9FA"
    dlg.SetFont("s10 norm", "Segoe UI")
    dlg.Add("Text", "w220 Center c1F2937", "Selecione o modo de impressão:")
    
    btn1 := dlg.Add("Button", "w220 h35", "1 - Impressão direta")
    btn1.OnEvent("Click", (*) => (escolha := "WMS2", dlg.Destroy()))
    
    btn2 := dlg.Add("Button", "w220 h35", "2 - Universal Printer")
    btn2.OnEvent("Click", (*) => (escolha := "Universal", dlg.Destroy()))
    
    dlg.Show("AutoSize Center")
    WinWaitClose(dlg)
    
    if (escolha != "") {
        impressoraPadrao := escolha
        SalvarImpressoraConfig(escolha) 
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

AtualizarStatus(status, codigoAtual:="-", totalProc:=0, temErro:=false, codErro:="", msgErro:="") {
    global PastaAutomacaoGlobal
    pastaLocal := (PastaAutomacaoGlobal != "" && DirExist(PastaAutomacaoGlobal)) ? PastaAutomacaoGlobal : A_ScriptDir
    totalProcessadosVal := Number(totalProc)
    txtJson := '{"status": "' status '", "codigo_atual": "' codigoAtual '", "total_processados": ' totalProcessadosVal ', "erro": ' (temErro ? "true" : "false") ', "codigo_erro": "' codErro '", "mensagem_erro": "' msgErro '"}'
    EscreverArquivoJSON(pastaLocal "\status.json", txtJson)
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

; =====================================================================
;  FUNÇÃO PARA REGISTRAR O RELATÓRIO EM ARQUIVO CSV
; =====================================================================

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
        AtualizarStatus("imprimindo", codigo, contador - 1)
        AtualizarMonitorAHK("imprimindo", codigo, contador, total)

        if !ProcessarCodigoDireto(codigo, contador, total) {
            AtualizarStatus("erro", codigo, contador - 1, true, codigo, "Falha durante o ciclo de impressao.")
            AtualizarMonitorAHK("erro", codigo, contador - 1, total, "Falha durante o ciclo de impressao.")
            return
        }

        RegistrarEmCSV(codigo)

        AtualizarStatus("imprimindo", codigo, contador)
        Sleep(50)
    }

    AtualizarStatus("concluido", "Concluído", contador)
    AtualizarMonitorAHK("concluido", "-", contador, total)
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
                AtualizarMonitorAHK("aviso", codigo, contador, total)
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

        while (tempoImp < 50) {
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

        if (impressoraPadrao = "WMS2" || impressoraPadrao = "WMS 2") {
            FocarEclicar(BotaoTrocarImpressora_X, BotaoTrocarImpressora_Y)
            Sleep(70) 
            FocarEclicar(ImpressoraWMS2_X, ImpressoraWMS2_Y)
            Sleep(70) 
            FocarEclicar(BotaoOK_X, BotaoOK_Y)
            AguardarJanelaFecharRapido(hwndSelecao, 8)
        } else {
            FocarEclicar(BotaoOK_X, BotaoOK_Y)
            AguardarJanelaFechar(hwndSelecao, 5)

            hwndUniv := 0
            loop {
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
                AguardarJanelaFecharRapido(hwndUniv, 8)
            }
        }

        tempoProg := 0
        while !ExisteAlgumaJanela(TitulosProgresso) && (tempoProg < 200) {
            tempoProg++
            Sleep(70)
        }

        while ExisteAlgumaJanela(TitulosProgresso) {
            Sleep(70)
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