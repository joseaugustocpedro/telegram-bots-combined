from __future__ import annotations

import asyncio
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from telegram import Update

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from apps.bank.bot import build_application  # noqa: E402
from apps.bank.dashboard import dashboard_bp, initialize_dashboard_database  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("combined-telegram-bots-v3-lite")

web_app = Flask(__name__)
web_app.register_blueprint(dashboard_bp)
stop_event = threading.Event()
process_lock = threading.Lock()
spy_process: subprocess.Popen | None = None
spy_last_exit_code: int | None = None
spy_restart_count = 0


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def validate_configuration() -> None:
    required = [
        "SPY_BOT_TOKEN",
        "SPY_DATABASE_URL",
        "BANK_BOT_TOKEN",
        "BANK_DATABASE_URL",
        "DASHBOARD_BASE_URL",
        "DASHBOARD_SECRET",
        "BANK_WEBHOOK_SECRET",
    ]
    missing = [name for name in required if not env(name)]
    if missing:
        raise RuntimeError("Variáveis ausentes: " + ", ".join(missing))
    if len(env("DASHBOARD_SECRET")) < 32:
        raise RuntimeError("DASHBOARD_SECRET precisa ter pelo menos 32 caracteres.")
    if not env("DASHBOARD_BASE_URL").startswith("https://"):
        raise RuntimeError("DASHBOARD_BASE_URL precisa começar com https://")
    if not (ROOT / "apps" / "spy" / "bot.py").exists():
        raise RuntimeError("apps/spy/bot.py não encontrado. Execute o build.sh.")


def _spy_environment() -> dict[str, str]:
    child = os.environ.copy()
    child["BOT_TOKEN"] = env("SPY_BOT_TOKEN")
    child["DATABASE_URL"] = env("SPY_DATABASE_URL")
    child["PORT"] = env("SPY_INTERNAL_PORT", "10001")
    child["PYTHONUNBUFFERED"] = "1"
    # O Spy não precisa enxergar os segredos do Gestor.
    for key in ("BANK_BOT_TOKEN", "BANK_DATABASE_URL", "DASHBOARD_SECRET", "BANK_WEBHOOK_SECRET"):
        child.pop(key, None)
    return child


def launch_spy() -> subprocess.Popen:
    script = ROOT / "apps" / "spy" / "bot.py"
    logger.info("Iniciando Spy Bot em subprocesso isolado.")
    return subprocess.Popen(
        [sys.executable, "-u", str(script)],
        cwd=str(script.parent),
        env=_spy_environment(),
    )


def monitor_spy() -> None:
    global spy_process, spy_last_exit_code, spy_restart_count
    delay = max(30, int(env("CHILD_RESTART_DELAY_SECONDS", "120")))
    while not stop_event.is_set():
        try:
            process = launch_spy()
            with process_lock:
                spy_process = process
            exit_code = process.wait()
            with process_lock:
                spy_process = None
                spy_last_exit_code = exit_code
                spy_restart_count += 1
            if stop_event.is_set():
                return
            logger.error("Spy Bot encerrou com código %s. Reinício em %ss.", exit_code, delay)
            stop_event.wait(delay)
        except Exception:
            logger.exception("Falha ao iniciar/monitorar Spy Bot.")
            stop_event.wait(delay)


class BankWebhookRuntime:
    def __init__(self) -> None:
        self.loop: asyncio.AbstractEventLoop | None = None
        self.application = None
        self.thread: threading.Thread | None = None
        self.ready = threading.Event()
        self.failed: Exception | None = None

    def start(self) -> None:
        self.thread = threading.Thread(target=self._thread_main, daemon=True, name="bank-webhook-runtime")
        self.thread.start()
        if not self.ready.wait(timeout=45):
            raise RuntimeError("Timeout ao iniciar o Gestor de Banca.")
        if self.failed:
            raise RuntimeError("Falha ao iniciar o Gestor de Banca.") from self.failed

    def _thread_main(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._async_start())
            self.ready.set()
            self.loop.run_forever()
        except Exception as exc:
            self.failed = exc
            logger.exception("Runtime do Gestor falhou.")
            self.ready.set()
        finally:
            if self.loop and not self.loop.is_closed():
                self.loop.run_until_complete(self._async_stop())
                self.loop.close()

    async def _async_start(self) -> None:
        self.application = build_application(env("BANK_BOT_TOKEN"))
        await self.application.initialize()
        await self.application.start()
        webhook_url = env("DASHBOARD_BASE_URL").rstrip("/") + "/telegram/bank"
        await self.application.bot.set_webhook(
            url=webhook_url,
            secret_token=env("BANK_WEBHOOK_SECRET"),
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=False,
            max_connections=2,
        )
        logger.info("Webhook do Gestor configurado em %s", webhook_url)

    def submit(self, payload: dict[str, Any]) -> bool:
        if not self.loop or not self.application or not self.ready.is_set() or self.failed:
            return False
        update = Update.de_json(payload, self.application.bot)
        future = asyncio.run_coroutine_threadsafe(self.application.update_queue.put(update), self.loop)
        try:
            future.result(timeout=1.5)
            return True
        except Exception:
            future.cancel()
            logger.exception("Fila do webhook indisponível.")
            return False

    async def _async_stop(self) -> None:
        if self.application:
            try:
                await self.application.stop()
            finally:
                await self.application.shutdown()

    def stop(self) -> None:
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread:
            self.thread.join(timeout=15)


bank_runtime = BankWebhookRuntime()


@web_app.get("/")
def index():
    return {
        "status": "online",
        "service": "telegram-bots-combined-v3-lite",
        "dashboard": "/dashboard/<link-gerado-pelo-bot>",
    }, 200


@web_app.get("/health")
def health():
    with process_lock:
        process = spy_process
        spy_running = bool(process and process.poll() is None)
    payload = {
        "status": "online" if bank_runtime.ready.is_set() and not bank_runtime.failed else "degraded",
        "bank": {
            "webhook_runtime": bank_runtime.ready.is_set() and bank_runtime.failed is None,
            "queue_size": bank_runtime.application.update_queue.qsize() if bank_runtime.application else None,
        },
        "spy": {
            "running": spy_running,
            "last_exit_code": spy_last_exit_code,
            "restart_count": spy_restart_count,
        },
    }
    return jsonify(payload), 200 if payload["status"] == "online" else 503


@web_app.post("/telegram/bank")
def telegram_bank_webhook():
    supplied_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if supplied_secret != env("BANK_WEBHOOK_SECRET"):
        return jsonify({"error": "forbidden"}), 403
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json"}), 400
    if not bank_runtime.submit(payload):
        return jsonify({"error": "runtime_unavailable"}), 503
    return "", 200


def shutdown(signum=None, frame=None) -> None:
    if stop_event.is_set():
        return
    logger.info("Encerrando serviço combinado...")
    stop_event.set()
    with process_lock:
        process = spy_process
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
    bank_runtime.stop()
    if signum is not None:
        raise SystemExit(0)


def main() -> None:
    validate_configuration()
    initialize_dashboard_database()
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    bank_runtime.start()
    threading.Thread(target=monitor_spy, daemon=True, name="spy-monitor").start()
    port = int(env("PORT", "10000"))
    logger.info("Servidor público iniciado na porta %s.", port)
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
