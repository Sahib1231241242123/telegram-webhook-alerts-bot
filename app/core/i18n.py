SUPPORTED_LANGUAGES = {"ru", "en"}
DEFAULT_LANGUAGE = "ru"

MESSAGES: dict[str, dict[str, str]] = {
    "start": {
        "ru": (
            "Привет! Доступные команды:\n"
            "/report — сводный отчет за день и неделю\n"
            "/alerts — список активных алертов\n"
            "/language — выбрать язык"
        ),
        "en": (
            "Hi! Available commands:\n"
            "/report — summary report for day and week\n"
            "/alerts — active alerts list\n"
            "/language — choose language"
        ),
    },
    "language_prompt": {
        "ru": "Выберите язык интерфейса:",
        "en": "Choose interface language:",
    },
    "language_changed": {
        "ru": "Язык переключен на русский 🇷🇺",
        "en": "Language switched to English 🇬🇧",
    },
    "rate_limited": {
        "ru": "Слишком много запросов. Попробуйте через несколько секунд.",
        "en": "Too many requests. Try again in a few seconds.",
    },
    "callback_rate_limited": {
        "ru": "Слишком много запросов. Попробуйте чуть позже.",
        "en": "Too many requests. Please try again later.",
    },
    "invalid_callback": {
        "ru": "Некорректный callback. Обновите список алертов командой /alerts.",
        "en": "Malformed callback. Refresh alerts with /alerts.",
    },
    "unknown_callback_action": {
        "ru": "Неизвестное действие callback.",
        "en": "Unknown callback action.",
    },
    "report_data_unavailable": {
        "ru": "Не удалось сформировать отчет: данные временно недоступны.",
        "en": "Unable to build report: data is temporarily unavailable.",
    },
    "alerts_data_unavailable": {
        "ru": "Не удалось загрузить алерты: данные временно недоступны.",
        "en": "Unable to load alerts: data is temporarily unavailable.",
    },
    "alert_not_found": {
        "ru": "Алерт не найден.",
        "en": "Alert not found.",
    },
    "internal_error": {
        "ru": "Произошла ошибка при обработке запроса.",
        "en": "An error occurred while processing your request.",
    },
}


def normalize_language(value: str | None) -> str:
    if value and value.lower() in SUPPORTED_LANGUAGES:
        return value.lower()
    return DEFAULT_LANGUAGE


def get_user_language(user_data: dict) -> str:
    return normalize_language(user_data.get("language"))


def set_user_language(user_data: dict, language: str) -> str:
    lang = normalize_language(language)
    user_data["language"] = lang
    return lang


def translate(message_key: str, language: str) -> str:
    lang = normalize_language(language)
    catalog = MESSAGES.get(message_key, {})
    return catalog.get(lang) or catalog.get(DEFAULT_LANGUAGE) or message_key
