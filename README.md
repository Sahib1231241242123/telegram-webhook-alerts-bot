<div align="center">

# Telegram Bot MVP
### Webhook-first • Async • Clean Architecture • Security-focused

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Webhook-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PTB](https://img.shields.io/badge/python--telegram--bot-20.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://python-telegram-bot.org)
[![Tests](https://img.shields.io/badge/coverage-87%25-success?style=for-the-badge)](#)

</div>

---

## 🌐 Language / Язык
- [English](#english)
- [Русский](#русский)

---

## English

### What it does
Production-ready MVP Telegram bot in **webhook mode** (no polling):
- `/report` with day/week metrics:
  - revenue
  - orders count
  - margin
  - top-3 SKU
- `/alerts` with inline actions:
  - ✅ Confirm
  - ❌ Reject
  - ℹ️ Details
- callback handling with **structured callback_data**
- FSM details state + back navigation
- async repository layer over JSON fixtures (`orders.json`, `alerts.json`)
- per-user language switching (`/language`) between **English** and **Russian**

### Architecture
```text
app/
  core/          # config, logging, errors, i18n, container
  handlers/      # commands, callbacks, fsm, error handler
  services/      # report, alerts, rate limiter, sanitizer
  repositories/  # async interfaces + JSON repos
  schemas/       # pydantic models + callback schema
  keyboards/     # inline keyboards (alerts + language)
  main.py        # FastAPI webhook app
fixtures/
tests/
```

### Security highlights
- env-only secrets (`BOT_TOKEN`, `WEBHOOK_URL`)
- callback_data validation (schema + length + action whitelist)
- safe fixture parsing with strict pydantic validation
- anti-abuse message length cap (`MAX_MESSAGE_LEN`)
- basic in-memory rate limiting (per user)
- centralized error handling with structured logging (`structlog`)

### Quick start
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
copy .env.example .env
```

Set `.env`:
- `BOT_TOKEN=...`
- `WEBHOOK_URL=https://<your-ngrok-or-domain>`

Run:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Health:
- `GET http://127.0.0.1:8080/health`

### Webhook with ngrok
```bash
ngrok http 8080
```
Use generated HTTPS URL as `WEBHOOK_URL`, restart app.

### QA / Tooling
```bash
pytest
ruff check .
black --check .
```

---

## Русский

### Что реализовано
Production-ready MVP Telegram-бот в **webhook-режиме** (без polling):
- `/report` с показателями day/week:
  - revenue
  - количество заказов
  - margin
  - top-3 SKU
- `/alerts` с inline-действиями:
  - ✅ Confirm
  - ❌ Reject
  - ℹ️ Details
- обработка callback через **структурированный callback_data**
- FSM-состояние для экрана деталей + возврат назад
- асинхронный репозиторий на JSON fixture (`orders.json`, `alerts.json`)
- выбор языка пользователем через `/language` (**Русский / English**)

### Архитектура
```text
app/
  core/          # config, logging, errors, i18n, container
  handlers/      # commands, callbacks, fsm, error handler
  services/      # report, alerts, rate limiter, sanitizer
  repositories/  # async интерфейсы + JSON реализации
  schemas/       # pydantic модели + callback schema
  keyboards/     # inline keyboards (alerts + language)
  main.py        # FastAPI webhook-приложение
fixtures/
tests/
```

### Безопасность
- секреты только из env (`BOT_TOKEN`, `WEBHOOK_URL`)
- строгая валидация callback_data (формат/длина/допустимые actions)
- безопасный парсинг fixture + pydantic-валидация полей
- ограничение длины сообщений (`MAX_MESSAGE_LEN`)
- базовый in-memory rate limit по пользователю
- централизованный error handler + структурные логи (`structlog`)

### Быстрый запуск
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
copy .env.example .env
```

Заполни `.env`:
- `BOT_TOKEN=...`
- `WEBHOOK_URL=https://<ваш-ngrok-или-домен>`

Запуск:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Проверка:
- `GET http://127.0.0.1:8080/health`

### Webhook через ngrok
```bash
ngrok http 8080
```
Скопируйте HTTPS URL в `WEBHOOK_URL` и перезапустите сервис.

### Проверки качества
```bash
pytest
ruff check .
black --check .
```

---

## Environment Variables
| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | yes | — | Telegram bot token |
| `WEBHOOK_URL` | yes | — | Public webhook base URL |
| `WEBHOOK_PATH` | no | `/webhook` | Webhook endpoint path |
| `MAX_MESSAGE_LEN` | no | `3500` | Max outgoing message size |
| `RATE_LIMIT_CALLS` | no | `10` | Allowed calls in window |
| `RATE_LIMIT_WINDOW_SEC` | no | `30` | Rate limit window in seconds |
| `LOG_LEVEL` | no | `INFO` | Log verbosity |
