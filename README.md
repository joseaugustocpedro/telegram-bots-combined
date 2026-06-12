# Dois bots Telegram em um único Web Service do Render

Este repositório mestre inicia, no mesmo serviço:

- Polymarket Spy Bot
- Gestor de Banca Pro

Os códigos originais continuam nos repositórios existentes. Durante cada build,
o Render baixa as versões mais recentes dos dois projetos.

## Build Command

```bash
bash build.sh
```

## Start Command

```bash
python main.py
```

## Variáveis obrigatórias

```text
SPY_BOT_TOKEN
SPY_DATABASE_URL
BANK_BOT_TOKEN
BANK_DATABASE_URL
```

## Variáveis recomendadas do Spy Bot

```text
POLL_INTERVAL=60
MIN_ALERT_USD=1000
LARGE_ALERT_USD=5000
WHALE_ALERT_USD=20000
SETTLE_SECONDS=60
SMALL_BATCH_MAX_AGE_SECONDS=900
FETCH_LIMIT=100
BOT_TIMEZONE=America/Sao_Paulo
DAILY_SUMMARY_HOUR=21
DAILY_SUMMARY_MINUTE=0
SEND_BOOTSTRAP_ALERTS=false
```

## Variáveis recomendadas do Gestor Pro

```text
INITIAL_BANKROLL=1000
CURRENCY=R$
```

## Importante

Os dois serviços antigos precisam permanecer suspensos. Caso uma versão antiga
use o mesmo token ao mesmo tempo, o Telegram responderá com conflito de
`getUpdates`.
