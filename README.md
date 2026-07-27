# Telegram Bots Combined — v3 Lite

Arquitetura econômica para o Render Free:

- processo principal: Flask + dashboard + Gestor de Banca por webhook;
- subprocesso separado: Polymarket Spy;
- sem processo separado para o Gestor;
- sem Matplotlib;
- somente uma porta pública;
- gráficos em SVG executados no navegador.

## Render

Build command:

```bash
bash build.sh
```

Start command:

```bash
python main.py
```

Health check:

```text
/health
```

Copie as variáveis do arquivo `.env.example` para a área **Environment** do Render.
