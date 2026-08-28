# =============================================================================
# start.ps1 — Sobe o backend local com um único comando
# =============================================================================
# USO: clique com o botão direito neste arquivo no VS Code Terminal, ou digite:
#   .\start.ps1
#
# O que este script faz:
#   1. Garante que está rodando a partir da pasta raiz do projeto
#      (não importa de onde você chamou o script)
#   2. Ativa o ambiente virtual (.venv) se existir
#   3. Sobe o servidor uvicorn com reload automático
#
# A variável DATABASE_URL/SECRET_KEY NÃO precisa ser digitada aqui —
# o database.py já carrega o .env sozinho via python-dotenv.
# =============================================================================

# Move para a pasta onde este script está (raiz do projeto)
Set-Location -Path $PSScriptRoot

# Verifica se o ambiente virtual existe
if (-Not (Test-Path ".venv")) {
    Write-Host "❌ Ambiente virtual (.venv) não encontrado." -ForegroundColor Red
    Write-Host "Rode primeiro: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Verifica se o .env existe
if (-Not (Test-Path ".env")) {
    Write-Host "❌ Arquivo .env não encontrado na raiz do projeto." -ForegroundColor Red
    Write-Host "Copie o .env.example para .env e preencha os valores." -ForegroundColor Yellow
    exit 1
}

# Ativa o ambiente virtual
& ".venv\Scripts\Activate.ps1"

Write-Host "✅ Ambiente virtual ativado." -ForegroundColor Green
Write-Host "🚀 Subindo o backend em http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Write-Host "   Documentação Swagger: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Sobe o servidor (o .env é carregado automaticamente pelo database.py)
Set-Location -Path "app"
uvicorn main:app --reload --port 8000
