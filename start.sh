#!/bin/bash
# =============================================================================
# start.sh — Sobe o backend local com um único comando (Mac/Linux)
# =============================================================================
# USO: chmod +x start.sh   (uma única vez)
#      ./start.sh
# =============================================================================

# Move para a pasta onde este script está (raiz do projeto)
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "❌ Ambiente virtual (.venv) não encontrado."
    echo "Rode primeiro: python3 -m venv .venv"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado na raiz do projeto."
    echo "Copie o .env.example para .env e preencha os valores."
    exit 1
fi

source .venv/bin/activate

echo "✅ Ambiente virtual ativado."
echo "🚀 Subindo o backend em http://127.0.0.1:8000 ..."
echo "   Documentação Swagger: http://127.0.0.1:8000/docs"
echo ""

cd app
uvicorn main:app --reload --port 8000
