from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.schemas.alert import AlertRecord
from app.schemas.callbacks import CallbackAction, CallbackPayload


def build_alerts_keyboard(alerts: list[AlertRecord], language: str = "ru") -> InlineKeyboardMarkup:
    details_label = "ℹ️ Details" if language == "en" else "ℹ️ Детали"
    rows: list[list[InlineKeyboardButton]] = []
    for alert in alerts:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"✅ {alert.id}",
                    callback_data=CallbackPayload(
                        action=CallbackAction.CONFIRM,
                        alert_id=alert.id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=f"❌ {alert.id}",
                    callback_data=CallbackPayload(
                        action=CallbackAction.REJECT,
                        alert_id=alert.id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=f"{details_label} {alert.id}",
                    callback_data=CallbackPayload(
                        action=CallbackAction.DETAILS,
                        alert_id=alert.id,
                    ).pack(),
                ),
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_back_to_alerts_keyboard(alert_id: str, language: str = "ru") -> InlineKeyboardMarkup:
    back_label = "⬅️ Back to alerts" if language == "en" else "⬅️ Назад к алертам"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=back_label,
                    callback_data=CallbackPayload(
                        action=CallbackAction.BACK,
                        alert_id=alert_id,
                    ).pack(),
                )
            ]
        ]
    )
