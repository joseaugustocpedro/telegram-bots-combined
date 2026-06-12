#!/usr/bin/env bash
set -euo pipefail

echo "==> Atualizando pip"
python -m pip install --upgrade pip

echo "==> Instalando dependências do serviço mestre"
pip install -r requirements.txt

echo "==> Baixando as versões mais recentes dos dois bots"
rm -rf apps
mkdir -p apps

git clone --depth 1 \
  https://github.com/joseaugustocpedro/polymarket-spy-bot.git \
  apps/spy

git clone --depth 1 \
  https://github.com/joseaugustocpedro/telegram-bet-bot.git \
  apps/bank

echo "==> Instalando dependências do Spy Bot"
pip install -r apps/spy/requirements.txt

echo "==> Instalando dependências do Gestor de Banca Pro"
pip install -r apps/bank/requirements.txt

echo "==> Validando sintaxe"
python -m py_compile main.py
python -m py_compile apps/spy/bot.py
python -m py_compile apps/bank/bot.py

echo "==> Build concluído"
