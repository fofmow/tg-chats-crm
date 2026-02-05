from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class MenuCallbacks:
    """Callback data constants for menu buttons."""
    
    DEBIT_CREDIT = "menu:debit_credit"
    REPORTS = "menu:reports"
    REPORT_7_DAYS = "menu:report_7_days"
    REPORT_CURRENT_MONTH = "menu:report_current_month"
    REPORT_PREVIOUS_MONTH = "menu:report_previous_month"
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
                    text="📊 Debit/Credit",
                    callback_data=MenuCallbacks.DEBIT_CREDIT,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Reports",
                    callback_data=MenuCallbacks.REPORTS,
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Current Balance",
                    callback_data=MenuCallbacks.BALANCE,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 Last Incoming",
                    callback_data=MenuCallbacks.LAST_INCOMING,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📤 Last Outgoing",
                    callback_data=MenuCallbacks.LAST_OUTGOING,
                )
            ],
        ]
    )


def get_reports_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting report period."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Last 7 Days",
                    callback_data=MenuCallbacks.REPORT_7_DAYS,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📆 Current Month",
                    callback_data=MenuCallbacks.REPORT_CURRENT_MONTH,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📆 Previous Month",
                    callback_data=MenuCallbacks.REPORT_PREVIOUS_MONTH,
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back to Menu",
                    callback_data=MenuCallbacks.BACK_TO_MENU,
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
                    text="⬅️ Back to Menu",
                    callback_data=MenuCallbacks.BACK_TO_MENU,
                )
            ]
        ]
    )
