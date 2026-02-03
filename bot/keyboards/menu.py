from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class MenuCallbacks:
    """Callback data constants for menu buttons."""
    
    DEBIT_CREDIT = "menu:debit_credit"
    REPORT_7_DAYS = "menu:report_7_days"
    BALANCE = "menu:balance"
    LAST_INCOMING = "menu:last_incoming"
    LAST_OUTGOING = "menu:last_outgoing"
    BACK_TO_MENU = "menu:back"


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get the main admin menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Дебит/Кредит",
                    callback_data=MenuCallbacks.DEBIT_CREDIT,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Отчет за 7 дней",
                    callback_data=MenuCallbacks.REPORT_7_DAYS,
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Текущий баланс",
                    callback_data=MenuCallbacks.BALANCE,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 Последний входящий",
                    callback_data=MenuCallbacks.LAST_INCOMING,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📤 Последний исходящий",
                    callback_data=MenuCallbacks.LAST_OUTGOING,
                )
            ],
        ]
    )


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with back button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад в меню",
                    callback_data=MenuCallbacks.BACK_TO_MENU,
                )
            ]
        ]
    )
