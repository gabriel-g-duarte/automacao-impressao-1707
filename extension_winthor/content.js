console.log("WinThor Keep AutoSync v12.0 - Conexão Direta (Sem Background Service Worker)");

function criarIndicador() {
    if (document.getElementById("winthor-status-badge")) return;
    const badge = document.createElement("div");
    badge.id = "winthor-status-badge";
    badge.style.position = "fixed";
    badge.style.bottom = "12px";
    badge.style.left = "12px";
    badge.style.padding = "6px 14px";
    badge.style.background = "#1e293b";
    badge.style.color = "#38bdf8";
    badge.style.borderRadius = "20px";
    badge.style.fontSize = "12px";
    badge.style.fontWeight = "bold";
    badge.style.zIndex = "99999";
    badge.style.boxShadow = "0 2px 8px rgba(0,0,0,0.3)";
    badge.style.fontFamily = "sans-serif";
    badge.innerText = "🟢 WinThor Sync: Ativo";
    document.body.appendChild(badge);
}

function atualizarStatus(texto, corBg, corTexto) {
    const badge = document.getElementById("winthor-status-badge");
    if (badge) {
        badge.innerText = texto;
        badge.style.background = corBg;
        badge.style.color = corTexto;
    }
}

window.ultimosCodigosEnviados = "";
window.mostrarSucesso = false;

function obterTextoCorpoNota() {
    let container = document.querySelector('div[role="dialog"]') || document.body;
    let editaveis = Array.from(container.querySelectorAll('div[contenteditable="true"]'));
    let textoTotal = "";
    
    editaveis.forEach(el => {
        let label = el.getAttribute('aria-label') || "";
        if (label.includes('Pesquisar') || label.includes('Search')) return;
        textoTotal += (el.innerText || "") + "\n"; 
    });

    return textoTotal;
}

async function enviarParaServidorPython(textoCodigos) {
    try {
        const response = await fetch("http://localhost:5000/api/codigos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ texto: textoCodigos })
        });

        if (response.ok) {
            return true;
        } else {
            return false;
        }
    } catch (err) {
        // Se o servidor Python estiver desligado, captura o erro sem estourar no Chrome
        return false;
    }
}

async function verificarKeep() {
    if (document.visibilityState !== "visible") {
        return; 
    }

    criarIndicador();
    let textoCorpo = obterTextoCorpoNota();

    if (!textoCorpo || textoCorpo.trim() === "") {
        if (!window.mostrarSucesso) atualizarStatus("🟡 Abra uma nota no Keep", "#ca8a04", "#ffffff");
        return;
    }

    let linhas = textoCorpo.split('\n');
    let codigosEncontrados = [];

    linhas.forEach(linha => {
        let linhaLimpa = linha.replace(/[\u200B-\u200D\uFEFF]/g, '').trim();
        if (/editad|modificad|criad|edited|created|\b\d{1,2}:\d{2}\b/i.test(linhaLimpa)) return;

        let match = linhaLimpa.match(/^[-*•☑☐\s]*(\d{2,6})(?!\d)/);
        if (match) {
            codigosEncontrados.push(match[1]);
        }
    });

    codigosEncontrados = [...new Set(codigosEncontrados)];

    if (codigosEncontrados.length > 0) {
        let chaveCodigos = codigosEncontrados.join(",");

        // Se os códigos forem iguais aos últimos, apenas mostra "Lendo" e não envia nada
        if (chaveCodigos === window.ultimosCodigosEnviados) {
            if (!window.mostrarSucesso) {
                atualizarStatus(`🟢 Lendo: ${codigosEncontrados.length} códigos`, "#1e293b", "#38bdf8");
            }
            return;
        }

        let textoParaPython = codigosEncontrados.join("\n");

        // Envio direto via fetch do content script para o Flask/Python
        let sucesso = await enviarParaServidorPython(textoParaPython);

        if (sucesso) {
            window.ultimosCodigosEnviados = chaveCodigos;
            window.mostrarSucesso = true;
            atualizarStatus(`✅ Enviados ${codigosEncontrados.length} códigos p/ TXT`, "#15803d", "#ffffff");
            setTimeout(() => { window.mostrarSucesso = false; }, 2500);
        } else {
            atualizarStatus("🔴 Servidor Python desligado!", "#991b1b", "#ffffff");
        }
    } else {
        if (!window.mostrarSucesso) atualizarStatus("🟡 Nenhum código detectado", "#ca8a04", "#ffffff");
    }
}

setInterval(verificarKeep, 1000);