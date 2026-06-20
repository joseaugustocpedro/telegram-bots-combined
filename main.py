# Mudanças no `telegram-bots-combined/main.py`

O objetivo aqui é evitar loop de restart rápido. Se um bot falhar por limite de API, falta de banco ou erro temporário, ele não deve reiniciar a cada 10 segundos eternamente.

Procure no `main.py` a parte em que o processo filho é reiniciado, algo parecido com:

```python
logger.error("%s encerrou com código %s. Reiniciando em 10s.", name, exit_code)
stop_event.wait(10)
```

Troque por:

```python
restart_delay = int(os.environ.get("CHILD_RESTART_DELAY_SECONDS", "120"))
logger.error(
    "%s encerrou com código %s. Reiniciando em %ss.",
    name,
    exit_code,
    restart_delay,
)
stop_event.wait(restart_delay)
```

E no Render coloque:

```env
CHILD_RESTART_DELAY_SECONDS=120
```

Isso reduz tráfego, logs e consumo quando algo está errado.
