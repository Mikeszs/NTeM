/**
 * theme.js — Alternância de tema claro/escuro
 *
 * Carregar este script no <head>, ANTES do CSS terminar de aplicar,
 * para evitar o "flash" de tela clara antes de escurecer.
 *
 * IMPORTANTE: este script ativa DOIS atributos ao mesmo tempo:
 *   - data-theme="dark"     → nosso sistema de cores customizado
 *   - data-bs-theme="dark"  → o modo escuro NATIVO do Bootstrap 5.3
 *
 * Sem o segundo atributo, o Bootstrap nunca ativa suas próprias
 * variáveis internas de dark mode (--bs-heading-color,
 * --bs-form-label-color, --bs-card-color, e várias outras que não
 * dá pra prever todas manualmente). Isso causava o bug de títulos,
 * labels e números aparecerem em preto fixo mesmo no modo escuro,
 * pois cada correção pontual só resolvia UM componente por vez.
 * Ativando o data-bs-theme junto, o Bootstrap corrige TODOS os
 * seus próprios componentes de uma vez, de forma nativa.
 */

(() => {
    const CHAVE_TEMA = '_ns_tema';

    /** Aplica o tema salvo (ou claro, por padrão) imediatamente. */
    function aplicarTemaSalvo() {
        const salvo = localStorage.getItem(CHAVE_TEMA);
        const preferido = salvo || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        aplicarAtributos(preferido);
        return preferido;
    }

    /** Seta os dois atributos de tema ao mesmo tempo (nosso + nativo do Bootstrap). */
    function aplicarAtributos(tema) {
        document.documentElement.setAttribute('data-theme', tema);
        document.documentElement.setAttribute('data-bs-theme', tema);
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
        aplicarAtributos(temaAtual);
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
