/**
 * config.js — Configuração central da aplicação NutriSocial
 *
 * Detecta automaticamente se está rodando em desenvolvimento (localhost)
 * ou em produção (Vercel). Sem precisar alterar código ao fazer deploy.
 *
 * Como usar em qualquer página HTML:
 *   <script src="config.js"></script>   ← ANTES do auth.js e dos outros scripts
 *
 * Depois, use simplesmente:
 *   fetch(`${API_BASE}/pacientes/`, { ... })
 * 
 * Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
 */

const API_BASE = (() => {
    const host = window.location.hostname;

    // Qualquer variação de localhost ou IP local → aponta para o backend local
    const isLocal =
        host === 'localhost'  ||
        host === '127.0.0.1'  ||
        host === '0.0.0.0'    ||
        host.startsWith('192.168.');

    return isLocal
        ? 'http://localhost:8000'           // backend rodando localmente
        : 'https://ntandm.onrender.com';    // backend em produção no Render
})();

// Exibe no console qual ambiente está ativo (facilita debug)
console.log(`[NutriSocial] Ambiente: ${API_BASE.includes('localhost') ? '🛠 LOCAL' : '🚀 PRODUÇÃO'} → ${API_BASE}`);
