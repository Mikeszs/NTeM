/**
 * auth.js — Módulo central de autenticação do NutriSocial
 *
 * POR QUE sessionStorage em vez de localStorage?
 * ─────────────────────────────────────────────
 * • localStorage persiste para sempre no disco — qualquer extensão
 *   maliciosa ou script injetado (XSS) pode ler o token dias depois.
 * • sessionStorage existe apenas enquanto a aba está aberta.
 *   Fechar a aba ou o browser limpa tudo automaticamente.
 * • O token ainda é legível por JS (inevitável em SPA sem backend de cookie),
 *   mas a janela de exposição cai drasticamente.
 *
 * O que fica armazenado:
 * ─────────────────────
 * • _ns_tk  → JWT (necessário para as chamadas autenticadas)
 * • _ns_ctx → JSON { nome, role } codificado em base64
 *             (dificulta leitura casual; não é criptografia)
 *
 * Como usar nas páginas:
 * ──────────────────────
 * <script src="auth.js"></script>   ← antes de qualquer outro script
 *
 * auth.salvar(token, role, nome)  — chamado no login
 * auth.token()                    — retorna o JWT para o fetch
 * auth.role()                     — retorna 'profissional' | 'paciente'
 * auth.nome()                     — retorna o nome do usuário
 * auth.limpar()                   — logout: apaga tudo
 * auth.exigir('profissional')     — guarda de rota; redireciona se não bater
 */

const auth = (() => {
    const KEY_TOKEN = '_ns_tk';
    const KEY_CTX   = '_ns_ctx';

    /** Salva sessão após login bem-sucedido. */
    function salvar(token, role, nome) {
        // Token: sessionStorage puro (precisa ser lido pelo fetch)
        sessionStorage.setItem(KEY_TOKEN, token);

        // Contexto: codificado em base64 para não ficar em texto puro
        const ctx = btoa(JSON.stringify({ role, nome }));
        sessionStorage.setItem(KEY_CTX, ctx);
    }

    /** Retorna o JWT ou null se não houver sessão. */
    function token() {
        return sessionStorage.getItem(KEY_TOKEN);
    }

    /** Decodifica e retorna o contexto { role, nome } ou null. */
    function _ctx() {
        try {
            const raw = sessionStorage.getItem(KEY_CTX);
            if (!raw) return null;
            return JSON.parse(atob(raw));
        } catch {
            return null;
        }
    }

    /** Retorna o role do usuário logado ('profissional' | 'paciente'). */
    function role() {
        return _ctx()?.role ?? null;
    }

    /** Retorna o nome do usuário logado. */
    function nome() {
        return _ctx()?.nome ?? null;
    }

    /** Apaga a sessão inteira (logout). */
    function limpar() {
        sessionStorage.removeItem(KEY_TOKEN);
        sessionStorage.removeItem(KEY_CTX);

        // Limpeza de segurança: remove chaves antigas do localStorage
        // (caso o usuário ainda tenha dados da versão anterior)
        ['token_nutrisocial', 'role_nutrisocial', 'nome_nutrisocial']
            .forEach(k => localStorage.removeItem(k));
    }

    /**
     * Guarda de rota: verifica se o usuário está autenticado e tem o role
     * esperado. Redireciona para login.html se não estiver.
     *
     * @param {'profissional'|'paciente'|null} roleEsperado
     *        Passe null para exigir apenas autenticação, sem checar o role.
     */
    function exigir(roleEsperado = null) {
        const tk = token();
        const rl = role();

        if (!tk) {
            window.location.href = 'login.html';
            return;
        }

        if (roleEsperado && rl !== roleEsperado) {
            // Autenticado, mas sem permissão — volta para o login
            limpar();
            window.location.href = 'login.html';
        }
    }

    // API pública
    return { salvar, token, role, nome, limpar, exigir };
})();