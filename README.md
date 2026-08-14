# Telegram Bots Combined — Resource-Efficient Deployment

Serviço em Python que consolida múltiplos bots e um dashboard web em uma única aplicação, projetado para execução em ambientes com memória e CPU limitadas.

O objetivo técnico é demonstrar **integração de serviços, arquitetura orientada a webhooks, gerenciamento de subprocessos e otimização de infraestrutura**.

## Arquitetura

```text
Internet
   ↓
Flask / única porta pública
   ├── Health check
   ├── Dashboard
   └── Webhook Telegram
          ↓
   Gestor principal
          ↓
      PostgreSQL

Subprocesso separado
   └── Polymarket Spy
```

## Decisões de engenharia

- uma única porta HTTP pública;
- Flask como processo principal;
- recebimento de atualizações por webhook;
- processo separado apenas quando necessário;
- sem Matplotlib para reduzir consumo de memória;
- gráficos SVG renderizados no navegador;
- configuração por variáveis de ambiente;
- endpoint `/health` para monitoramento da aplicação.

## Deploy no Render

### Build

```bash
bash build.sh
```

### Start

```bash
python main.py
```

### Health check

```text
/health
```

Copie as chaves necessárias de `.env.example` para a área **Environment** do serviço. Nunca versionar tokens, senhas ou strings de conexão reais.

## Competências demonstradas

- Python;
- Flask;
- webhooks;
- integração de serviços;
- deploy em nuvem;
- otimização de recursos;
- organização de processos;
- monitoramento de aplicação.

## Autor

**José Augusto Cevidanes Pedro**  
Estudante de Engenharia de Controle e Automação — IFSP
