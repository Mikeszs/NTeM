/**
 * theme.js — Alternância de tema claro/escuro
 *
 * Carregar este script no <head>, ANTES do CSS terminar de aplicar,
 * para evitar o "flash" de tela clara antes de escurecer.
 *
 * Como usar em cada página:
 *   1. No <head>, logo após o <link> do style.css:
 *      <script src="theme.js"></script>
 *
 *   2. Em algum lugar do HTML (normalmente no header/navbar):
 *      <button class="theme-toggle" id="themeToggle" aria-label="Alternar tema">
 *          <i class="fas fa-moon"></i>
 *      </button>
 *
 *   3. Nada mais é necessário — este script encontra o botão sozinho
 *      (se existir) e liga o evento de clique automaticamente.
 */

(() => {
    const CHAVE_TEMA = '_ns_tema';

    /** Aplica o tema salvo (ou claro, por padrão) imediatamente. */
    function aplicarTemaSalvo() {
        const salvo = localStorage.getItem(CHAVE_TEMA);
        // Preferência salva > preferência do sistema operacional > claro
        const preferido = salvo || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', preferido);
        return preferido;
    }

    // Aplica IMEDIATAMENTE — antes do resto do HTML renderizar,
    // para não haver flash de tela clara em modo escuro.
    let temaAtual = aplicarTemaSalvo();

    function atualizarIconeBotao(botao) {
        if (!botao) return;
        const icone = botao.querySelector('i');
        if (!icone) return;
        icone.className = temaAtual === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    function alternarTema() {
        temaAtual = temaAtual === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', temaAtual);
        localStorage.setItem(CHAVE_TEMA, temaAtual);
        atualizarIconeBotao(document.getElementById('themeToggle'));
    }

    // Liga o botão assim que o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', () => {
        const botao = document.getElementById('themeToggle');
        if (botao) {
            atualizarIconeBotao(botao);
            botao.addEventListener('click', alternarTema);
        }
    });
})();
