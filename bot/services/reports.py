from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud import PaymentInCRUD, PaymentOutCRUD
from bot.database.models import PaymentIn, PaymentOut


@dataclass
class DebitCreditReport:
    """Report with debit/credit information."""
    
    total_incoming: float
    total_outgoing: float
    incoming_count: int
    outgoing_count: int
    
    @property
    def balance(self) -> float:
        return self.total_incoming - self.total_outgoing


@dataclass
class BalanceReport:
    """Current balance report."""
    
    total_incoming: float
    total_outgoing: float
    
    @property
    def balance(self) -> float:
        return self.total_incoming - self.total_outgoing


class ReportsService:
    """Service for generating reports."""
    
    @staticmethod
    async def get_debit_credit(session: AsyncSession) -> DebitCreditReport:
        """Get debit/credit report."""
        total_incoming = await PaymentInCRUD.get_total_amount(session)
        total_outgoing = await PaymentOutCRUD.get_total_amount(session)
        incoming_count = await PaymentInCRUD.get_count(session)
        outgoing_count = await PaymentOutCRUD.get_count(session)
        
        return DebitCreditReport(
            total_incoming=total_incoming,
            total_outgoing=total_outgoing,
            incoming_count=incoming_count,
            outgoing_count=outgoing_count,
        )
    
    @staticmethod
    async def get_balance(session: AsyncSession) -> BalanceReport:
        """Get current balance."""
        total_incoming = await PaymentInCRUD.get_total_amount(session)
        total_outgoing = await PaymentOutCRUD.get_total_amount(session)
        
        return BalanceReport(
            total_incoming=total_incoming,
            total_outgoing=total_outgoing,
        )
    
    @staticmethod
    async def get_last_incoming(session: AsyncSession) -> PaymentIn | None:
        """Get the last incoming payment."""
        return await PaymentInCRUD.get_last(session)
    
    @staticmethod
    async def get_last_outgoing(session: AsyncSession) -> PaymentOut | None:
        """Get the last outgoing payment."""
        return await PaymentOutCRUD.get_last(session)
    
    @staticmethod
    async def get_last_7_days_incoming(session: AsyncSession) -> list[PaymentIn]:
        """Get incoming payments for the last 7 days."""
        return await PaymentInCRUD.get_last_7_days(session)
    
    @staticmethod
    async def get_last_7_days_outgoing(session: AsyncSession) -> list[PaymentOut]:
        """Get outgoing payments for the last 7 days."""
        return await PaymentOutCRUD.get_last_7_days(session)
