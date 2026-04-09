from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.schemas.callbacks import CallbackAction, CallbackPayload


def build_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data=CallbackPayload(
                        action=CallbackAction.SET_LANG,
                        alert_id="ru",
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data=CallbackPayload(
                        action=CallbackAction.SET_LANG,
                        alert_id="en",
                    ).pack(),
                ),
            ]
        ]
    )
