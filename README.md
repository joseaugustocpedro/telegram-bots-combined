# Telegram Bots Combined — Resource-Efficient Deployment

Serviço em Python que consolida múltiplos bots e um dashboard web em uma única aplicação, projetado para execução em ambientes com memória e CPU limitadas.

O objetivo técnico é explorar **integração de serviços, arquitetura orientada a webhooks, gerenciamento de subprocessos e otimização de infraestrutura**. Esta documentação descreve a configuração pretendida; não representa evidência de deploy público, segurança ou disponibilidade contínua.

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

## Pré-requisitos e limitações

O script `build.sh` clona os repositórios públicos [`polymarket-spy-bot`](https://github.com/joseaugustocpedro/polymarket-spy-bot) e [`telegram-bet-bot`](https://github.com/joseaugustocpedro/telegram-bet-bot) para a pasta local `apps/`. Portanto, **este repositório não é autocontido**: o build depende desses códigos e de acesso à internet. Por padrão, usa os ramos `main`; para tornar uma execução reproduzível, fixe `SPY_REPO_REF` e `BANK_REPO_REF` em referências estáveis verificadas.

Não publique variáveis secretas e não considere o dashboard pronto para exposição pública sem revisão específica de autenticação, deploy e dados.

## Decisões de engenharia

- uma única porta HTTP pública;
- Flask como processo principal;
- recebimento de atualizações por webhook;
- processo separado apenas quando necessário;
- sem Matplotlib para reduzir consumo de memória;
- gráficos SVG renderizados no navegador;
- configuração por variáveis de ambiente;
- endpoint `/health` para monitoramento da aplicação.

## Configuração para Render (não validada nesta revisão)

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
