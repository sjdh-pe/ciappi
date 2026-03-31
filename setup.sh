#!/bin/bash
# ============================================
# 🚀 Script de Setup Automatizado - CIAPPI
# ============================================
# Use: ./setup.sh
# Este script configura o ambiente completo

set -e  # Para em caso de erro

echo "╔════════════════════════════════════════╗"
echo "║  🚀 CIAPPI - Setup Automatizado        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# 1. Verificar pré-requisitos
echo "📋 Verificando pré-requisitos..."

PYTHON_CMD="python3.12"

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "⚠️  $PYTHON_CMD não encontrado. Tentando python3..."
    PYTHON_CMD="python3"
    if ! command -v $PYTHON_CMD &> /dev/null; then
        echo "❌ Python não encontrado. Instale Python 3.12"
        exit 1
    fi
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale Docker Desktop"
    exit 1
fi

echo "✅ Python $($PYTHON_CMD --version | awk '{print $2}')"
echo "✅ Docker $(docker --version | awk '{print $3}' | tr -d ',')"
echo ""

# 2. Copiar arquivo de ambiente
echo "📄 Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    if [ -f EXEMPLO.env ]; then
        cp EXEMPLO.env .env
        echo "✅ .env criado a partir de EXEMPLO.env"
        echo "⚠️  IMPORTANTE: Edite .env com suas credenciais!"
    else
        echo "❌ EXEMPLO.env não encontrado"
        exit 1
    fi
else
    echo "✅ .env já existe"
fi
echo ""

# 3. Criar ambientes virtuais
echo "🐍 Criando ambientes virtuais..."

if [ ! -d "venv-backend" ]; then
    echo "  → Backend venv..."
    $PYTHON_CMD -m venv venv-backend
    echo "  ✅ venv-backend criado"
else
    echo "  ℹ️  venv-backend já existe"
fi

if [ ! -d "venv-frontend" ]; then
    echo "  → Frontend venv..."
    $PYTHON_CMD -m venv venv-frontend
    echo "  ✅ venv-frontend criado"
else
    echo "  ℹ️  venv-frontend já existe"
fi
echo ""

# 4. Instalar dependências
echo "📦 Instalando dependências Python..."

echo "  → Backend..."
source venv-backend/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt > /dev/null 2>&1
echo "  ✅ Backend dependencies instaladas"
deactivate

echo "  → Frontend..."
source venv-frontend/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r frontend/requirements.txt > /dev/null 2>&1
echo "  ✅ Frontend dependencies instaladas"
deactivate
echo ""

# 5. Subir Docker
echo "🐳 Iniciando Docker..."
docker compose up -d > /dev/null 2>&1
sleep 3
echo "✅ Containers iniciados"
echo ""

# 6. Verificar status
echo "🔍 Verificando status..."
docker ps --filter "name=db-ciappi" --format "table {{.Names}}\t{{.Status}}"
echo ""

# 7. Resumo
echo "╔════════════════════════════════════════╗"
echo "║  ✨ Setup Completo!                    ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo ""
echo "1️⃣  Edite .env com suas credenciais (se não fez)"
echo ""
echo "2️⃣  Backend (Terminal 1):"
echo "    source venv-backend/bin/activate"
echo "    uvicorn backend.app.main:app --reload --port 8000"
echo ""
echo "3️⃣  Frontend (Terminal 2):"
echo "    source venv-frontend/bin/activate"
echo "    streamlit run frontend/app.py"
echo ""
echo "📖 Leia QUICKSTART.md para mais informações"
echo ""

