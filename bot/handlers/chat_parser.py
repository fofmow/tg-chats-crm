import re
from dataclasses import dataclass
from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message, ReactionTypeEmoji

from bot.config import settings
from bot.database.crud import PaymentInCRUD, PaymentOutCRUD
from bot.database.models import Database

router = Router(name="chat_parser")


@dataclass
class ParseResult:
    """Result of parsing a message."""
    success: bool
    data: dict | None = None
    error: str | None = None


def parse_date(date_str: str) -> datetime.date:
    """Parse date from various formats."""
    date_str = date_str.strip()
    
    formats = [
        "%d.%m.%Y",  # 01.02.2026
        "%d.%m.%y",  # 01.02.26
        "%Y-%m-%d",  # 2026-02-01
        "%d/%m/%Y",  # 01/02/2026
        "%d-%m-%Y",  # 01-02-2026
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def parse_amount(amount_str: str) -> float | None:
    """Parse amount from string."""
    cleaned = re.sub(r"[^\d.,]", "", amount_str.strip())
    
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_payin_message(text: str) -> ParseResult:
    """
    Parse pay-in message format:
    date: 01.02.2026
    amount: 5000
    client: Ivanov
    teacher: Petrov
    """
    patterns = {
        "date": (r"(?:дата|date)\s*[:\-]\s*(.+)", "date"),
        "amount": (r"(?:сумма|amount|sum)\s*[:\-]\s*(.+)", "amount"),
        "client": (r"(?:клиент|client)\s*[:\-]\s*(.+)", "client"),
        "to": (r"(?:преподаватель|teacher|to)\s*[:\-]\s*(.+)", "to"),
    }
    
    result = {}
    missing_fields = []
    text_lower = text.lower()
    
    for key, (pattern, field_name) in patterns.items():
        match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
        if match:
            result[key] = match.group(1).strip()
        else:
            missing_fields.append(field_name)
    
    # Check for missing fields
    if missing_fields:
        return ParseResult(
            success=False,
            error=f"❌ Missing fields: {', '.join(missing_fields)}"
        )
    
    # Validate date
    parsed_date = parse_date(result["date"])
    if not parsed_date:
        return ParseResult(
            success=False,
            error=f"❌ Invalid date format: {result['date']}\nExpected: DD.MM.YYYY"
        )
    
    # Validate amount
    parsed_amount = parse_amount(result["amount"])
    if not parsed_amount:
        return ParseResult(
            success=False,
            error=f"❌ Invalid amount format: {result['amount']}"
        )
    
    # Get original case values
    for key in ["client", "to"]:
        pattern, _ = patterns[key]
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            result[key] = match.group(1).strip()
    
    return ParseResult(
        success=True,
        data={
            "date": parsed_date,
            "amount": parsed_amount,
            "client": result["client"],
            "teacher": result["to"],
        }
    )


def parse_payout_message(text: str) -> ParseResult:
    """
    Parse pay-out message format:
    date: 01.02.2026
    amount: 3000
    category: Salary
    to: Sidorov
    """
    patterns = {
        "date": (r"(?:дата|date)\s*[:\-]\s*(.+)", "date"),
        "amount": (r"(?:сумма|amount|sum)\s*[:\-]\s*(.+)", "amount"),
        "category": (r"(?:категория|category)\s*[:\-]\s*(.+)", "category"),
        "to": (r"(?:кому|to)\s*[:\-]\s*(.+)", "to"),
    }
    
    result = {}
    missing_fields = []
    text_lower = text.lower()
    
    for key, (pattern, field_name) in patterns.items():
        match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
        if match:
            result[key] = match.group(1).strip()
        else:
            missing_fields.append(field_name)
    
    # Check for missing fields
    if missing_fields:
        return ParseResult(
            success=False,
            error=f"❌ Missing fields: {', '.join(missing_fields)}"
        )
    
    # Validate date
    parsed_date = parse_date(result["date"])
    if not parsed_date:
        return ParseResult(
            success=False,
            error=f"❌ Invalid date format: {result['date']}\nExpected: DD.MM.YYYY"
        )
    
    # Validate amount
    parsed_amount = parse_amount(result["amount"])
    if not parsed_amount:
        return ParseResult(
            success=False,
            error=f"❌ Invalid amount format: {result['amount']}"
        )
    
    # Get original case values
    for key in ["category", "to"]:
        pattern, _ = patterns[key]
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            result[key] = match.group(1).strip()
    
    return ParseResult(
        success=True,
        data={
            "date": parsed_date,
            "amount": parsed_amount,
            "category": result["category"],
            "recipient": result["to"],
        }
    )


def looks_like_payment_message(text: str) -> bool:
    """Check if message looks like a payment record (has at least 2 relevant fields)."""
    keywords = [
        r"(?:дата|date)\s*[:\-]",
        r"(?:сумма|amount|sum)\s*[:\-]",
        r"(?:клиент|client)\s*[:\-]",
        r"(?:преподаватель|teacher|to)\s*[:\-]",
        r"(?:категория|category)\s*[:\-]",
        r"(?:кому|recipient|to)\s*[:\-]",
    ]
    matches = sum(1 for kw in keywords if re.search(kw, text, re.IGNORECASE))
    return matches >= 2


async def add_success_reaction(message: Message):
    """Add success reaction to message."""
    try:
        await message.react([ReactionTypeEmoji(emoji="👍")])
    except Exception as ex:
        # Reaction might fail if bot doesn't have permission
        print(ex)


async def add_cancel_reaction(message: Message):
    """Add cancel reaction to the original message."""
    try:
        await message.react([ReactionTypeEmoji(emoji="👎")])
    except Exception as ex:
        # Reaction might fail if bot doesn't have permission
        print(ex)


def is_cancel_command(text: str) -> bool:
    """Check if message is a cancel command."""
    return text.strip().lower() == "cancel"


@router.message(
    F.chat.id.in_([settings.ru_payin_chat_id, settings.eng_payin_chat_id]),
    F.reply_to_message,
    F.text,
)
async def handle_payin_cancel(message: Message, db: Database):
    """Handle cancel command for pay-in chats."""
    if not message.text or not is_cancel_command(message.text):
        return
    
    if not message.reply_to_message:
        return
    
    reply_message_id = message.reply_to_message.message_id
    chat_id = message.chat.id
    
    async with db.session_factory() as session:
        deleted = await PaymentInCRUD.delete_by_message_id(
            session=session,
            message_id=reply_message_id,
            chat_id=chat_id,
        )
    
    if deleted:
        await add_cancel_reaction(message.reply_to_message)
        await message.reply(
            f"✅ Transaction cancelled:\n"
            f"Amount: {deleted.amount:,.2f}\n"
            f"Client: {deleted.client}\n"
            f"Teacher: {deleted.teacher}"
        )
    else:
        await message.reply("❌ Transaction not found in database")


@router.message(
    F.chat.id == settings.payout_chat_id,
    F.reply_to_message,
    F.text,
)
async def handle_payout_cancel(message: Message, db: Database):
    """Handle cancel command for pay-out chat."""
    if not message.text or not is_cancel_command(message.text):
        return
    
    if not message.reply_to_message:
        return
    
    reply_message_id = message.reply_to_message.message_id
    chat_id = message.chat.id
    
    async with db.session_factory() as session:
        deleted = await PaymentOutCRUD.delete_by_message_id(
            session=session,
            message_id=reply_message_id,
            chat_id=chat_id,
        )
    
    if deleted:
        await add_cancel_reaction(message.reply_to_message)
        await message.reply(
            f"✅ Transaction cancelled:\n"
            f"Amount: {deleted.amount:,.2f}\n"
            f"Category: {deleted.category}\n"
            f"Recipient: {deleted.recipient}"
        )
    else:
        await message.reply("❌ Transaction not found in database")


@router.message(F.chat.id == settings.ru_payin_chat_id)
async def handle_ru_payin(message: Message, db: Database):
    """Handle messages from RU pay-in chat."""
    if not message.text:
        return
    
    # Skip messages that don't look like payment records
    if not looks_like_payment_message(message.text):
        return
    
    parsed = parse_payin_message(message.text)
    
    if not parsed.success:
        await message.reply(parsed.error)
        return
    
    async with db.session_factory() as session:
        await PaymentInCRUD.create(
            session=session,
            payment_date=parsed.data["date"],
            amount=parsed.data["amount"],
            client=parsed.data["client"],
            teacher=parsed.data["teacher"],
            chat_type="ru",
            message_id=message.message_id,
            chat_id=message.chat.id,
        )
    
    await add_success_reaction(message)


@router.message(F.chat.id == settings.eng_payin_chat_id)
async def handle_eng_payin(message: Message, db: Database):
    """Handle messages from ENG pay-in chat."""
    if not message.text:
        return
    
    if not looks_like_payment_message(message.text):
        return
    
    parsed = parse_payin_message(message.text)
    
    if not parsed.success:
        await message.reply(parsed.error)
        return
    
    async with db.session_factory() as session:
        await PaymentInCRUD.create(
            session=session,
            payment_date=parsed.data["date"],
            amount=parsed.data["amount"],
            client=parsed.data["client"],
            teacher=parsed.data["teacher"],
            chat_type="eng",
            message_id=message.message_id,
            chat_id=message.chat.id,
        )
    
    await add_success_reaction(message)


@router.message(F.chat.id == settings.payout_chat_id)
async def handle_payout(message: Message, db: Database):
    """Handle messages from pay-out chat."""
    if not message.text:
        return
    
    if not looks_like_payment_message(message.text):
        return
    
    parsed = parse_payout_message(message.text)
    
    if not parsed.success:
        await message.reply(parsed.error)
        return
    
    async with db.session_factory() as session:
        await PaymentOutCRUD.create(
            session=session,
            payment_date=parsed.data["date"],
            amount=parsed.data["amount"],
            category=parsed.data["category"],
            recipient=parsed.data["recipient"],
            message_id=message.message_id,
            chat_id=message.chat.id,
        )
    
    await add_success_reaction(message)
