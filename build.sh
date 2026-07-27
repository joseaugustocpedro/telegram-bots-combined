#!/usr/bin/env bash
set -euo pipefail

SPY_REPO_URL="${SPY_REPO_URL:-https://github.com/joseaugustocpedro/polymarket-spy-bot.git}"
BANK_REPO_URL="${BANK_REPO_URL:-https://github.com/joseaugustocpedro/telegram-bet-bot.git}"
SPY_REPO_REF="${SPY_REPO_REF:-main}"
BANK_REPO_REF="${BANK_REPO_REF:-main}"

python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

rm -rf apps
mkdir -p apps
touch apps/__init__.py

echo "==> Baixando Spy Bot (${SPY_REPO_REF})"
git clone --depth 1 --branch "$SPY_REPO_REF" "$SPY_REPO_URL" apps/spy

echo "==> Baixando Gestor de Banca (${BANK_REPO_REF})"
git clone --depth 1 --branch "$BANK_REPO_REF" "$BANK_REPO_URL" apps/bank

# Garante que o projeto do Gestor possa ser importado como pacote Python.
touch apps/bank/__init__.py

pip install --no-cache-dir -r apps/spy/requirements.txt
pip install --no-cache-dir -r apps/bank/requirements.txt

python -m py_compile main.py
python -m py_compile apps/spy/bot.py
python -m py_compile apps/bank/bot.py
python -m py_compile apps/bank/config.py
python -m py_compile apps/bank/database.py
python -m py_compile apps/bank/dashboard.py
python -m py_compile apps/bank/security.py

echo "==> Build concluído"
