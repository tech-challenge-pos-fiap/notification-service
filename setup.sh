#!/bin/bash

# 🔧 Notification Service - Setup Script
# Este script configura o ambiente local para desenvolvimento

set -e

echo "🚀 Iniciando setup do Notification Service..."

# 1. Criar arquivo .env
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Edite com suas credenciais SMTP!"
else
    echo "✅ Arquivo .env já existe"
fi

# 2. Criar virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Criando virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment criado"
else
    echo "✅ Virtual environment já existe"
fi

# 3. Ativar virtual environment
echo "🔗 Ativando virtual environment..."
source venv/bin/activate

# 4. Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependências instaladas"

# 5. Rodar testes
echo "🧪 Executando testes..."
pytest tests/ -v --tb=short
echo "✅ Testes OK!"

echo ""
echo "✨ Setup completo!"
echo ""
echo "Próximos passos:"
echo "1. Edite .env com suas credenciais SMTP"
echo "2. Execute: docker-compose up"
echo "3. Em outro terminal: python -m app.main"
echo ""
echo "Para ajuda: make help"
