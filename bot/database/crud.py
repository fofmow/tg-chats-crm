from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PaymentIn, PaymentOut


class PaymentInCRUD:
    """CRUD operations for PaymentIn."""

    @staticmethod
    async def create(
        session: AsyncSession,
        payment_date: date,
        amount: float,
        client: str,
        teacher: str,
        chat_type: str,
        message_id: int,
        chat_id: int,
    ) -> PaymentIn:
        """Create a new incoming payment."""
        payment = PaymentIn(
            date=payment_date,
            amount=amount,
            client=client,
            teacher=teacher,
            chat_type=chat_type,
            message_id=message_id,
            chat_id=chat_id,
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

    @staticmethod
    async def get_last(session: AsyncSession) -> PaymentIn | None:
        """Get the last incoming payment."""
        result = await session.execute(
            select(PaymentIn).order_by(PaymentIn.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_total_amount(session: AsyncSession) -> float:
        """Get total amount of all incoming payments."""
        result = await session.execute(
            select(func.coalesce(func.sum(PaymentIn.amount), 0))
        )
        return result.scalar_one()

    @staticmethod
    async def get_count(session: AsyncSession) -> int:
        """Get count of all incoming payments."""
        result = await session.execute(select(func.count(PaymentIn.id)))
        return result.scalar_one()

    @staticmethod
    async def get_last_7_days(session: AsyncSession) -> list[PaymentIn]:
        """Get all incoming payments from the last 7 days."""
        week_ago = date.today() - timedelta(days=7)
        result = await session.execute(
            select(PaymentIn)
            .where(PaymentIn.date >= week_ago)
            .order_by(PaymentIn.date.desc(), PaymentIn.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_date_range(
        session: AsyncSession,
        start_date: date,
        end_date: date,
    ) -> list[PaymentIn]:
        """Get all incoming payments within a date range."""
        result = await session.execute(
            select(PaymentIn)
            .where(PaymentIn.date >= start_date)
            .where(PaymentIn.date <= end_date)
            .order_by(PaymentIn.date.desc(), PaymentIn.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_current_month(session: AsyncSession) -> list[PaymentIn]:
        """Get all incoming payments for the current month."""
        today = date.today()
        start_date = date(today.year, today.month, 1)
        result = await session.execute(
            select(PaymentIn)
            .where(PaymentIn.date >= start_date)
            .where(PaymentIn.date <= today)
            .order_by(PaymentIn.date.desc(), PaymentIn.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_previous_month(session: AsyncSession) -> list[PaymentIn]:
        """Get all incoming payments for the previous month."""
        today = date.today()
        # Calculate previous month start and end
        if today.month == 1:
            prev_month_start = date(today.year - 1, 12, 1)
            prev_month_end = date(today.year - 1, 12, 31)
        else:
            prev_month_start = date(today.year, today.month - 1, 1)
            # Calculate last day of previous month
            if today.month == 1:
                prev_month_end = date(today.year - 1, 12, 31)
            else:
                # First day of current month minus 1 day
                prev_month_end = date(today.year, today.month, 1) - timedelta(days=1)
        
        result = await session.execute(
            select(PaymentIn)
            .where(PaymentIn.date >= prev_month_start)
            .where(PaymentIn.date <= prev_month_end)
            .order_by(PaymentIn.date.desc(), PaymentIn.created_at.desc())
        )
        return list(result.scalars().all())


class PaymentOutCRUD:
    """CRUD operations for PaymentOut."""

    @staticmethod
    async def create(
        session: AsyncSession,
        payment_date: date,
        amount: float,
        category: str,
        recipient: str,
        message_id: int,
        chat_id: int,
    ) -> PaymentOut:
        """Create a new outgoing payment."""
        payment = PaymentOut(
            date=payment_date,
            amount=amount,
            category=category,
            recipient=recipient,
            message_id=message_id,
            chat_id=chat_id,
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

    @staticmethod
    async def get_last(session: AsyncSession) -> PaymentOut | None:
        """Get the last outgoing payment."""
        result = await session.execute(
            select(PaymentOut).order_by(PaymentOut.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_total_amount(session: AsyncSession) -> float:
        """Get total amount of all outgoing payments."""
        result = await session.execute(
            select(func.coalesce(func.sum(PaymentOut.amount), 0))
        )
        return result.scalar_one()

    @staticmethod
    async def get_count(session: AsyncSession) -> int:
        """Get count of all outgoing payments."""
        result = await session.execute(select(func.count(PaymentOut.id)))
        return result.scalar_one()

    @staticmethod
    async def get_last_7_days(session: AsyncSession) -> list[PaymentOut]:
        """Get all outgoing payments from the last 7 days."""
        week_ago = date.today() - timedelta(days=7)
        result = await session.execute(
            select(PaymentOut)
            .where(PaymentOut.date >= week_ago)
            .order_by(PaymentOut.date.desc(), PaymentOut.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_date_range(
        session: AsyncSession,
        start_date: date,
        end_date: date,
    ) -> list[PaymentOut]:
        """Get all outgoing payments within a date range."""
        result = await session.execute(
            select(PaymentOut)
            .where(PaymentOut.date >= start_date)
            .where(PaymentOut.date <= end_date)
            .order_by(PaymentOut.date.desc(), PaymentOut.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_current_month(session: AsyncSession) -> list[PaymentOut]:
        """Get all outgoing payments for the current month."""
        today = date.today()
        start_date = date(today.year, today.month, 1)
        result = await session.execute(
            select(PaymentOut)
            .where(PaymentOut.date >= start_date)
            .where(PaymentOut.date <= today)
            .order_by(PaymentOut.date.desc(), PaymentOut.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_previous_month(session: AsyncSession) -> list[PaymentOut]:
        """Get all outgoing payments for the previous month."""
        today = date.today()
        # Calculate previous month start and end
        if today.month == 1:
            prev_month_start = date(today.year - 1, 12, 1)
            prev_month_end = date(today.year - 1, 12, 31)
        else:
            prev_month_start = date(today.year, today.month - 1, 1)
            # Calculate last day of previous month
            if today.month == 1:
                prev_month_end = date(today.year - 1, 12, 31)
            else:
                # First day of current month minus 1 day
                prev_month_end = date(today.year, today.month, 1) - timedelta(days=1)
        
        result = await session.execute(
            select(PaymentOut)
            .where(PaymentOut.date >= prev_month_start)
            .where(PaymentOut.date <= prev_month_end)
            .order_by(PaymentOut.date.desc(), PaymentOut.created_at.desc())
        )
        return list(result.scalars().all())
