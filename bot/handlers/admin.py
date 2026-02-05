from datetime import date

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.config import settings
from bot.database.models import Database
from bot.keyboards.menu import (
    MenuCallbacks,
    get_back_keyboard,
    get_main_menu_keyboard,
    get_reports_keyboard,
)
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
        "🏠 <b>Main Menu</b>\n\n"
        "Choose an action:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == MenuCallbacks.BACK_TO_MENU)
async def callback_back_to_menu(callback: CallbackQuery):
    """Handle back to menu button."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "🏠 <b>Main Menu</b>\n\n"
        "Choose an action:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == MenuCallbacks.DEBIT_CREDIT)
async def callback_debit_credit(callback: CallbackQuery, db: Database):
    """Handle debit/credit report."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    async with db.session_factory() as session:
        report = await ReportsService.get_debit_credit(session)

    text = (
        "📊 <b>Debit/Credit</b>\n\n"
        f"📥 <b>Incoming (debit):</b>\n"
        f"   Amount: {report.total_incoming:,.2f}\n"
        f"   Count: {report.incoming_count}\n\n"
        f"📤 <b>Outgoing (credit):</b>\n"
        f"   Amount: {report.total_outgoing:,.2f}\n"
        f"   Count: {report.outgoing_count}\n\n"
        f"💰 <b>Difference:</b> {report.balance:,.2f}"
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
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    async with db.session_factory() as session:
        report = await ReportsService.get_balance(session)

    balance_emoji = "📈" if report.balance >= 0 else "📉"

    text = (
        "💰 <b>Current Balance</b>\n\n"
        f"📥 Incoming: {report.total_incoming:,.2f}\n"
        f"📤 Outgoing: {report.total_outgoing:,.2f}\n\n"
        f"{balance_emoji} <b>Balance: {report.balance:,.2f}</b>"
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
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    async with db.session_factory() as session:
        payment = await ReportsService.get_last_incoming(session)

    if not payment:
        text = "📥 <b>Last Incoming Payment</b>\n\n❌ No payments yet"
    else:
        text = (
            "📥 <b>Last Incoming Payment</b>\n\n"
            f"📅 Date: {payment.date.strftime('%d.%m.%Y')}\n"
            f"💵 Amount: {payment.amount:,.2f}\n"
            f"👤 Client: {payment.client}\n"
            f"👨‍🏫 Teacher: {payment.teacher}\n"
            f"🌐 Chat: {payment.chat_type.upper()}"
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
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    async with db.session_factory() as session:
        payment = await ReportsService.get_last_outgoing(session)

    if not payment:
        text = "📤 <b>Last Outgoing Payment</b>\n\n❌ No payments yet"
    else:
        text = (
            "📤 <b>Last Outgoing Payment</b>\n\n"
            f"📅 Date: {payment.date.strftime('%d.%m.%Y')}\n"
            f"💵 Amount: {payment.amount:,.2f}\n"
            f"📁 Category: {payment.category}\n"
            f"👤 Recipient: {payment.recipient}"
        )

    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == MenuCallbacks.REPORTS)
async def callback_reports_menu(callback: CallbackQuery):
    """Handle reports menu."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    await callback.message.edit_text(
        "📅 <b>Reports</b>\n\n"
        "Select report period:",
        reply_markup=get_reports_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == MenuCallbacks.REPORT_7_DAYS)
async def callback_report_7_days(callback: CallbackQuery, db: Database):
    """Handle 7 days report - generate and send Excel file."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    await callback.answer("⏳ Generating report...")

    async with db.session_factory() as session:
        incoming = await ReportsService.get_last_7_days_incoming(session)
        outgoing = await ReportsService.get_last_7_days_outgoing(session)

    # Generate Excel file
    excel_file = ExcelService.generate_period_report(
        incoming, outgoing, period_name="Last 7 Days"
    )

    filename = f"report_7days_{date.today().strftime('%Y-%m-%d')}.xlsx"

    # Send file
    await callback.message.answer_document(
        BufferedInputFile(excel_file.read(), filename=filename),
        caption=(
            f"📅 <b>Report for the last 7 days</b>\n\n"
            f"📥 Incoming: {len(incoming)}\n"
            f"📤 Outgoing: {len(outgoing)}"
        ),
        parse_mode="HTML",
    )

    # Update original message
    await callback.message.edit_text(
        "📅 <b>Report for 7 days</b>\n\n"
        "✅ Report sent as Excel file above.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == MenuCallbacks.REPORT_CURRENT_MONTH)
async def callback_report_current_month(callback: CallbackQuery, db: Database):
    """Handle current month report - generate and send Excel file."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    await callback.answer("⏳ Generating report...")

    async with db.session_factory() as session:
        incoming = await ReportsService.get_current_month_incoming(session)
        outgoing = await ReportsService.get_current_month_outgoing(session)

    # Generate Excel file
    today = date.today()
    month_name = today.strftime("%B %Y")
    excel_file = ExcelService.generate_period_report(
        incoming, outgoing, period_name=f"Current Month ({month_name})"
    )

    filename = f"report_current_month_{today.strftime('%Y-%m')}.xlsx"

    # Send file
    await callback.message.answer_document(
        BufferedInputFile(excel_file.read(), filename=filename),
        caption=(
            f"📅 <b>Report for {month_name}</b>\n\n"
            f"📥 Incoming: {len(incoming)}\n"
            f"📤 Outgoing: {len(outgoing)}"
        ),
        parse_mode="HTML",
    )

    # Update original message
    await callback.message.edit_text(
        f"📅 <b>Report for {month_name}</b>\n\n"
        "✅ Report sent as Excel file above.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == MenuCallbacks.REPORT_PREVIOUS_MONTH)
async def callback_report_previous_month(callback: CallbackQuery, db: Database):
    """Handle previous month report - generate and send Excel file."""
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    await callback.answer("⏳ Generating report...")

    async with db.session_factory() as session:
        incoming = await ReportsService.get_previous_month_incoming(session)
        outgoing = await ReportsService.get_previous_month_outgoing(session)

    # Generate Excel file
    today = date.today()
    # Get previous month name
    if today.month == 1:
        prev_month = date(today.year - 1, 12, 1)
    else:
        prev_month = date(today.year, today.month - 1, 1)
    month_name = prev_month.strftime("%B %Y")

    excel_file = ExcelService.generate_period_report(
        incoming, outgoing, period_name=f"Previous Month ({month_name})"
    )

    filename = f"report_previous_month_{prev_month.strftime('%Y-%m')}.xlsx"

    # Send file
    await callback.message.answer_document(
        BufferedInputFile(excel_file.read(), filename=filename),
        caption=(
            f"📅 <b>Report for {month_name}</b>\n\n"
            f"📥 Incoming: {len(incoming)}\n"
            f"📤 Outgoing: {len(outgoing)}"
        ),
        parse_mode="HTML",
    )

    # Update original message
    await callback.message.edit_text(
        f"📅 <b>Report for {month_name}</b>\n\n"
        "✅ Report sent as Excel file above.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )
