// ==========================================
// js/app.js - Motor do Jogo BioQuest PWA
// ==========================================

let estadoJogo = {
    casoAtualIndex: 0,
    pontuacao: 0,
    tempoRestante: 2400,
    timerInterval: null,
    errosNoCaso: 0
};

// 1. SISTEMA DE ÁUDIO
const AUDIO = {
    success: new Audio('audio/success.mp3'),
    error: new Audio('audio/error.mp3'),
    click: new Audio('audio/click.mp3'),
    ambience: new Audio('audio/ambience.mp3')
};

AUDIO.ambience.loop = true;
AUDIO.ambience.volume = 0.15;

function tocarSom(som) {
    if (AUDIO[som]) {
        AUDIO[som].currentTime = 0;
        AUDIO[som].play().catch(() => {});
    }
}

// 2. REFERÊNCIAS DA DOM (Declarado uma única vez)
const DOM = {
    timer: document.getElementById('timer'),
    container: document.getElementById('game-container'),
    btnStart: document.getElementById('btn-start'),
    welcomeScreen: document.getElementById('welcome-screen')
};

// 3. FUNÇÕES DE APOIO
function embaralhar(array) {
    return array.sort(() => Math.random() - 0.5);
}

// 4. INICIALIZAÇÃO
document.addEventListener('DOMContentLoaded', () => {
    if (DOM.btnStart) {
        DOM.btnStart.onclick = iniciarConsultoria;
    }
});

function iniciarConsultoria() {
    tocarSom('click');
    AUDIO.ambience.play();
    if (DOM.welcomeScreen) DOM.welcomeScreen.classList.add('hidden');
    iniciarTimerGlobal();
    carregarEstagioDoCaso('diagnostico');
}

function iniciarTimerGlobal() {
    if (DOM.timer) DOM.timer.classList.remove('hidden');
    estadoJogo.timerInterval = setInterval(() => {
        estadoJogo.tempoRestante--;
        atualizarDisplayTimer();
        if (estadoJogo.tempoRestante <= 0) finalizarConsultoria("Tempo Esgotado!");
    }, 1000);
}

function atualizarDisplayTimer() {
    if (!DOM.timer) return;
    const min = Math.floor(estadoJogo.tempoRestante / 60);
    const seg = estadoJogo.tempoRestante % 60;
    DOM.timer.textContent = `${min.toString().padStart(2, '0')}:${seg.toString().padStart(2, '0')}`;
}

// 5. MOTOR DE RENDERIZAÇÃO
function carregarEstagioDoCaso(estagio) {
    const caso = CASOS_CLINICOS[estadoJogo.casoAtualIndex];
    if (!caso) return;

    // Embaralha as opções apenas quando entra no estágio (e não errou ainda)
    if (estagio === 'diagnostico' && estadoJogo.errosNoCaso === 0) {
        embaralhar(caso.opcoes);
    }
    if (estagio === 'conduta') {
        embaralhar(caso.conduta.opcoes);
    }

    let imagemFundo = (caso.id <= 4) ? 'images/vertical_farming.png' : 'images/cyberpunk_agriculture.png';
    DOM.container.style.backgroundImage = `linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.95)), url('${imagemFundo}')`;

    let htmlContent = '';
    switch (estagio) {
        case 'diagnostico':
            htmlContent = `
                <div class="caso-card estagio-entrada">
                    <p class="setor-tag">${caso.setor}</p>
                    <h3>Caso #${caso.id}: ${caso.titulo}</h3>
                    <p class="descricao">${caso.descricao}</p>
                    <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:15px 0;">
                    <p class="pergunta"><strong>[ANÁLISE]:</strong> ${caso.perguntaDiagnostico}</p>
                    <div class="opcoes-container">
                        ${caso.opcoes.map((opt, i) => `
                            <button onclick="tocarSom('click'); processarRespostaDiagnostico(${i})">${opt.texto}</button>
                        `).join('')}
                    </div>
                </div>`;
            break;

        case 'bioquimica':
            htmlContent = `
                <div class="caso-card estagio-entrada">
                    <h3>⚡ Mecanismo Bioquímico</h3>
                    <div style="background:rgba(0,230,118,0.1); padding:20px; border-radius:8px; margin:20px 0; border:1px solid var(--primary-green);">
                        <p style="color:var(--primary-green); font-size:1.4rem; font-weight:bold; margin:0;">${caso.formaAtiva}</p>
                    </div>
                    <p><strong>Impacto:</strong> ${caso.consequencia}</p>
                    <button class="btn-acao" onclick="tocarSom('click'); carregarEstagioDoCaso('conduta')">Definir Conduta ➡️</button>
                </div>`;
            break;

        case 'conduta':
            htmlContent = `
                <div class="caso-card estagio-entrada">
                    <h3>🚀 Intervenção Técnica</h3>
                    <p class="pergunta">Escolha o manejo adequado:</p>
                    <div class="opcoes-container">
                        ${caso.conduta.opcoes.map((opt, i) => `
                            <button onclick="tocarSom('click'); processarRespostaConduta(${i})">${opt.texto}</button>
                        `).join('')}
                    </div>
                </div>`;
            break;
    }
    DOM.container.innerHTML = htmlContent;
}

// 6. PROCESSAMENTO (SEM TIMERS AUTOMÁTICOS)
function processarRespostaDiagnostico(idx) {
    const caso = CASOS_CLINICOS[estadoJogo.casoAtualIndex];
    const escolha = caso.opcoes[idx];
    const container = document.querySelector('.opcoes-container');

    if (escolha.correta) {
        tocarSom('success');
        let pts = Math.max(10, 100 - (estadoJogo.errosNoCaso * 20));
        estadoJogo.pontuacao += pts;
        container.innerHTML = `
            <div class="feedback-msg feedback-correto">${escolha.feedback}<br><strong>+${pts} pts</strong></div>
            <button class="btn-acao" onclick="carregarEstagioDoCaso('bioquimica')">Continuar</button>
        `;
    } else {
        tocarSom('error');
        estadoJogo.errosNoCaso++;
        container.innerHTML = `
            <div class="feedback-msg feedback-errado">${escolha.feedback}</div>
            <div class="dica-box" style="margin:15px 0; font-size:0.9rem; color:#ffeb3b; border:1px dashed #ffeb3b; padding:12px; background:rgba(255,235,59,0.05);">
                💡 <strong>Dica Técnica:</strong> ${caso.dica || "Analise os cofatores enzimáticos mencionados."}
            </div>
            <button class="btn-acao btn-voltar" onclick="carregarEstagioDoCaso('diagnostico')">⬅️ Voltar e Tentar Novamente</button>
        `;
    }
}

function processarRespostaConduta(idx) {
    const caso = CASOS_CLINICOS[estadoJogo.casoAtualIndex];
    const escolha = caso.conduta.opcoes[idx];
    const container = document.querySelector('.opcoes-container');

    if (escolha.correta) {
        tocarSom('success');
        estadoJogo.pontuacao += 50;
        container.innerHTML = `
            <div class="feedback-msg feedback-correto">${escolha.feedback}</div>
            <button class="btn-acao" onclick="proximoCaso()">Próximo Caso ➡️</button>
        `;
    } else {
        tocarSom('error');
        container.innerHTML = `
            <div class="feedback-msg feedback-errado">${escolha.feedback}</div>
            <button class="btn-acao btn-voltar" onclick="carregarEstagioDoCaso('conduta')">⬅️ Revisar Estratégia</button>
        `;
    }
}

function proximoCaso() {
    estadoJogo.casoAtualIndex++;
    if (estadoJogo.casoAtualIndex < CASOS_CLINICOS.length) {
        carregarEstagioDoCaso('diagnostico');
    } else {
        finalizarConsultoria("Simulação Concluída!");
    }
}

function finalizarConsultoria(msg) {
    clearInterval(estadoJogo.timerInterval);
    if (DOM.timer) DOM.timer.classList.add('hidden');

    let rank = estadoJogo.pontuacao >= 800 ? 'Especialista Sênior' :
               estadoJogo.pontuacao >= 500 ? 'Consultor Pleno' : 'Técnico Residente';

    DOM.container.innerHTML = `
        <div class="caso-card estagio-entrada">
            <h2>${msg}</h2>
            <p style="font-size: 2.2rem; color: var(--primary-green); font-weight: bold; margin: 15px 0;">${estadoJogo.pontuacao} PTS</p>
            <p>Rank: <strong>${rank}</strong></p>
            <hr style="margin: 20px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);">
            <button class="btn-acao" onclick="location.reload()">Reiniciar Sistema</button>
        </div>`;
}