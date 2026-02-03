from datetime import date

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.config import settings
from bot.database.models import Database
from bot.keyboards.menu import MenuCallbacks, get_back_keyboard, get_main_menu_keyboard
from bot.services.excel import ExcelService
from bot.services.reports import ReportsService

router = Router(name="admin")


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in settings.admin_ids


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    if not message.from_user or not is_admin(message.from_user.id):
        return

    await message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == MenuCallbacks.BACK_TO_MENU)
async def callback_back_to_menu(callback: CallbackQuery):
    """Handle back to menu button."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == MenuCallbacks.DEBIT_CREDIT)
async def callback_debit_credit(callback: CallbackQuery, db: Database):
    """Handle debit/credit report."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return

    async with db.session_factory() as session:
        report = await ReportsService.get_debit_credit(session)

    text = (
        "📊 <b>Дебит/Кредит</b>\n\n"
        f"📥 <b>Входящие (дебит):</b>\n"
        f"   Сумма: {report.total_incoming:,.2f}\n"
        f"   Количество: {report.incoming_count}\n\n"
        f"📤 <b>Исходящие (кредит):</b>\n"
        f"   Сумма: {report.total_outgoing:,.2f}\n"
        f"   Количество: {report.outgoing_count}\n\n"
        f"💰 <b>Разница:</b> {report.balance:,.2f}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == MenuCallbacks.BALANCE)
async def callback_balance(callback: CallbackQuery, db: Database):
    """Handle balance report."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return

    async with db.session_factory() as session:
        report = await ReportsService.get_balance(session)

    balance_emoji = "📈" if report.balance >= 0 else "📉"

    text = (
        "💰 <b>Текущий баланс</b>\n\n"
        f"📥 Входящие: {report.total_incoming:,.2f}\n"
        f"📤 Исходящие: {report.total_outgoing:,.2f}\n\n"
        f"{balance_emoji} <b>Баланс: {report.balance:,.2f}</b>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == MenuCallbacks.LAST_INCOMING)
async def callback_last_incoming(callback: CallbackQuery, db: Database):
    """Handle last incoming payment."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return

    async with db.session_factory() as session:
        payment = await ReportsService.get_last_incoming(session)

    if not payment:
        text = "📥 <b>Последний входящий платеж</b>\n\n❌ Платежей пока нет"
    else:
        text = (
            "📥 <b>Последний входящий платеж</b>\n\n"
            f"📅 Дата: {payment.date.strftime('%d.%m.%Y')}\n"
            f"💵 Сумма: {payment.amount:,.2f}\n"
            f"👤 Клиент: {payment.client}\n"
            f"👨‍🏫 Преподаватель: {payment.teacher}\n"
            f"🌐 Чат: {payment.chat_type.upper()}"
        )

    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == MenuCallbacks.LAST_OUTGOING)
async def callback_last_outgoing(callback: CallbackQuery, db: Database):
    """Handle last outgoing payment."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return

    async with db.session_factory() as session:
        payment = await ReportsService.get_last_outgoing(session)

    if not payment:
        text = "📤 <b>Последний исходящий платеж</b>\n\n❌ Платежей пока нет"
    else:
        text = (
            "📤 <b>Последний исходящий платеж</b>\n\n"
            f"📅 Дата: {payment.date.strftime('%d.%m.%Y')}\n"
            f"💵 Сумма: {payment.amount:,.2f}\n"
            f"📁 Категория: {payment.category}\n"
            f"👤 Получатель: {payment.recipient}"
        )

    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == MenuCallbacks.REPORT_7_DAYS)
async def callback_report_7_days(callback: CallbackQuery, db: Database):
    """Handle 7 days report - generate and send Excel file."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return

    await callback.answer("⏳ Генерация отчета...")

    async with db.session_factory() as session:
        incoming = await ReportsService.get_last_7_days_incoming(session)
        outgoing = await ReportsService.get_last_7_days_outgoing(session)

    # Generate Excel file
    excel_file = ExcelService.generate_7_days_report(incoming, outgoing)

    filename = f"report_{date.today().strftime('%Y-%m-%d')}.xlsx"

    # Send file
    await callback.message.answer_document(
        BufferedInputFile(excel_file.read(), filename=filename),
        caption=(
            f"📅 <b>Отчет за последние 7 дней</b>\n\n"
            f"📥 Входящих: {len(incoming)}\n"
            f"📤 Исходящих: {len(outgoing)}"
        ),
        parse_mode="HTML",
    )

    # Update original message
    await callback.message.edit_text(
        "📅 <b>Отчет за 7 дней</b>\n\n"
        "✅ Отчет отправлен в виде Excel файла выше.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )
