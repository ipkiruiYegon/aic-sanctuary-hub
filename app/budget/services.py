from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from sqlmodel import Session, select, and_, or_
from typing import List, Optional
from app.budget.models import (
    YearlyBudget, DCCBudget, LocalChurchBudget,
    BudgetPayment, BudgetReport,
    VoteHead, DCCVoteHeadBudget, LocalChurchVoteHeadBudget,
    BudgetIncomeSource
)


class BudgetService:
    """Service layer for budget management"""

    # ==================== Yearly Budget Operations ====================

    @staticmethod
    async def create_yearly_budget(session: Session, year: int, total_budget: Decimal, description: Optional[str] = None) -> YearlyBudget:
        """Create a new yearly budget"""
        budget = YearlyBudget(
            year=year,
            total_budget=total_budget,
            description=description
        )
        session.add(budget)
        await session.commit()
        await session.refresh(budget)
        return budget

    @staticmethod
    async def get_yearly_budget(session: Session, budget_id: UUID) -> Optional[YearlyBudget]:
        """Get yearly budget by ID"""
        statement = select(YearlyBudget).where(YearlyBudget.id == budget_id)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_yearly_budgets(session: Session, year: Optional[int] = None) -> List[YearlyBudget]:
        """Get yearly budgets, optionally filtered by year"""
        statement = select(YearlyBudget)
        if year:
            statement = statement.where(YearlyBudget.year == year)
        statement = statement.order_by(YearlyBudget.year.desc())
        results = await session.exec(statement)
        return results.all()

    @staticmethod
    async def get_current_yearly_budget(session: Session) -> Optional[YearlyBudget]:
        """Get the current year's yearly budget"""
        current_year = datetime.now().year
        statement = select(YearlyBudget).where(
            and_(YearlyBudget.year == current_year,
                 YearlyBudget.is_active == True)
        )
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def update_yearly_budget(session: Session, budget_id: UUID, **kwargs) -> Optional[YearlyBudget]:
        """Update yearly budget"""
        statement = select(YearlyBudget).where(YearlyBudget.id == budget_id)
        result = await session.exec(statement)
        budget = result.first()
        if budget:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(budget, key, value)
            session.add(budget)
            await session.commit()
            await session.refresh(budget)
        return budget

    # ==================== DCC Budget Operations ====================

    @staticmethod
    async def create_dcc_budget(session: Session, yearly_budget_id: UUID, dcc_id: UUID, allocated_amount: Decimal) -> DCCBudget:
        """Allocate budget to DCC"""
        dcc_budget = DCCBudget(
            yearly_budget_id=yearly_budget_id,
            dcc_id=dcc_id,
            allocated_amount=allocated_amount
        )
        session.add(dcc_budget)
        await session.commit()
        await session.refresh(dcc_budget)
        return dcc_budget

    @staticmethod
    async def get_dcc_budget(session: Session, dcc_budget_id: UUID) -> Optional[DCCBudget]:
        """Get DCC budget by ID"""
        statement = select(DCCBudget).where(DCCBudget.id == dcc_budget_id)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_dcc_budgets_by_year(session: Session, year: int) -> List[DCCBudget]:
        """Get all DCC budgets for a specific year"""
        statement = select(DCCBudget).join(
            YearlyBudget).where(YearlyBudget.year == year)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def approve_dcc_budget(session: Session, dcc_budget_id: UUID) -> Optional[DCCBudget]:
        """Approve DCC budget allocation"""
        statement = select(DCCBudget).where(DCCBudget.id == dcc_budget_id)
        result = await session.exec(statement)
        budget = result.first()
        if budget:
            budget.status = "approved"
            budget.approval_date = datetime.now()
            session.add(budget)
            await session.commit()
            await session.refresh(budget)
        return budget

    @staticmethod
    async def reject_dcc_budget(session: Session, dcc_budget_id: UUID) -> Optional[DCCBudget]:
        """Reject DCC budget allocation"""
        statement = select(DCCBudget).where(DCCBudget.id == dcc_budget_id)
        result = await session.exec(statement)
        budget = result.first()
        if budget:
            budget.status = "rejected"
            session.add(budget)
            await session.commit()
            await session.refresh(budget)
        return budget

    @staticmethod
    async def create_vote_head(session: Session, name: str, code: str, description: Optional[str] = None) -> VoteHead:
        """Create a new regional vote head category"""
        vote_head = VoteHead(
            name=name,
            code=code,
            description=description
        )
        session.add(vote_head)
        await session.commit()
        await session.refresh(vote_head)
        return vote_head

    @staticmethod
    async def get_vote_heads(session: Session) -> List[VoteHead]:
        """List all vote head categories"""
        statement = select(VoteHead).order_by(VoteHead.name)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_vote_head(session: Session, vote_head_id: UUID) -> Optional[VoteHead]:
        """Get a vote head category by ID"""
        statement = select(VoteHead).where(VoteHead.id == vote_head_id)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def create_dcc_vote_head_budget(session: Session, dcc_budget_id: UUID, vote_head_id: UUID, allocated_amount: Decimal) -> DCCVoteHeadBudget:
        """Allocate a vote head budget to a DCC budget"""
        vote_budget = DCCVoteHeadBudget(
            dcc_budget_id=dcc_budget_id,
            vote_head_id=vote_head_id,
            allocated_amount=allocated_amount
        )
        session.add(vote_budget)
        await session.commit()
        await session.refresh(vote_budget)
        return vote_budget

    @staticmethod
    async def get_dcc_vote_head_budgets(session: Session, dcc_budget_id: UUID) -> List[DCCVoteHeadBudget]:
        """Get vote head allocations for a DCC budget"""
        statement = select(DCCVoteHeadBudget).where(
            DCCVoteHeadBudget.dcc_budget_id == dcc_budget_id
        )
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def create_local_church_vote_head_budget(session: Session, local_church_budget_id: UUID, vote_head_id: UUID, allocated_amount: Decimal) -> LocalChurchVoteHeadBudget:
        """Allocate a vote head budget to a local church budget"""
        vote_budget = LocalChurchVoteHeadBudget(
            local_church_budget_id=local_church_budget_id,
            vote_head_id=vote_head_id,
            allocated_amount=allocated_amount
        )
        session.add(vote_budget)
        await session.commit()
        await session.refresh(vote_budget)
        return vote_budget

    @staticmethod
    async def get_local_church_vote_head_budgets(session: Session, local_church_budget_id: UUID) -> List[LocalChurchVoteHeadBudget]:
        """Get vote head allocations for a local church budget"""
        statement = select(LocalChurchVoteHeadBudget).where(
            LocalChurchVoteHeadBudget.local_church_budget_id == local_church_budget_id
        )
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def create_budget_income_source(
        session: Session,
        source_type: str,
        amount: Decimal,
        description: Optional[str] = None,
        received_date: Optional[datetime] = None,
        yearly_budget_id: Optional[UUID] = None,
        dcc_budget_id: Optional[UUID] = None,
        local_church_budget_id: Optional[UUID] = None,
    ) -> BudgetIncomeSource:
        """Create an income source entry for a budget level"""
        if sum(bool(x) for x in [yearly_budget_id, dcc_budget_id, local_church_budget_id]) != 1:
            raise ValueError(
                "Exactly one budget level must be specified for an income source")

        source = BudgetIncomeSource(
            source_type=source_type,
            amount=amount,
            description=description,
            received_date=received_date or datetime.now(),
            yearly_budget_id=yearly_budget_id,
            dcc_budget_id=dcc_budget_id,
            local_church_budget_id=local_church_budget_id,
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
        return source

    @staticmethod
    async def get_yearly_budget_income_sources(session: Session, yearly_budget_id: UUID) -> List[BudgetIncomeSource]:
        """Get income sources for a yearly budget"""
        statement = select(BudgetIncomeSource).where(
            BudgetIncomeSource.yearly_budget_id == yearly_budget_id
        )
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_dcc_budget_income_sources(session: Session, dcc_budget_id: UUID) -> List[BudgetIncomeSource]:
        """Get income sources for a DCC budget"""
        statement = select(BudgetIncomeSource).where(
            BudgetIncomeSource.dcc_budget_id == dcc_budget_id
        )
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_local_church_budget_income_sources(session: Session, local_church_budget_id: UUID) -> List[BudgetIncomeSource]:
        """Get income sources for a local church budget"""
        statement = select(BudgetIncomeSource).where(
            BudgetIncomeSource.local_church_budget_id == local_church_budget_id
        )
        result = await session.exec(statement)
        return result.all()

    # ==================== Local Church Budget Operations ====================

    @staticmethod
    async def create_local_church_budget(session: Session, dcc_budget_id: UUID, local_church_id: UUID, allocated_amount: Decimal) -> LocalChurchBudget:
        """Allocate budget to local church"""
        church_budget = LocalChurchBudget(
            dcc_budget_id=dcc_budget_id,
            local_church_id=local_church_id,
            allocated_amount=allocated_amount
        )
        session.add(church_budget)
        await session.commit()
        await session.refresh(church_budget)
        return church_budget

    @staticmethod
    async def get_local_church_budget(session: Session, church_budget_id: UUID) -> Optional[LocalChurchBudget]:
        """Get local church budget by ID"""
        statement = select(LocalChurchBudget).where(
            LocalChurchBudget.id == church_budget_id)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_church_budgets_by_dcc(session: Session, dcc_budget_id: UUID) -> List[LocalChurchBudget]:
        """Get all church budgets under a DCC"""
        statement = select(LocalChurchBudget).where(
            LocalChurchBudget.dcc_budget_id == dcc_budget_id)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_all_church_budgets(session: Session) -> List[LocalChurchBudget]:
        """Get all church budgets across all DCCs"""
        statement = select(LocalChurchBudget)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def approve_church_budget(session: Session, church_budget_id: UUID) -> Optional[LocalChurchBudget]:
        """Approve church budget allocation"""
        statement = select(LocalChurchBudget).where(
            LocalChurchBudget.id == church_budget_id)
        result = await session.exec(statement)
        budget = result.first()
        if budget:
            budget.status = "approved"
            budget.approval_date = datetime.now()
            session.add(budget)
            await session.commit()
            await session.refresh(budget)
        return budget

    # ==================== Payment Tracking ====================

    @staticmethod
    async def create_payment(session: Session, local_church_budget_id: UUID, payment_month: int,
                             payment_year: int, amount_paid: Decimal, due_date: datetime,
                             recorded_by_id: UUID, payment_method: Optional[str] = None,
                             reference_number: Optional[str] = None, notes: Optional[str] = None) -> BudgetPayment:
        """Record a budget payment"""
        payment = BudgetPayment(
            local_church_budget_id=local_church_budget_id,
            payment_month=payment_month,
            payment_year=payment_year,
            amount_paid=amount_paid,
            due_date=due_date,
            payment_date=datetime.now(),
            status="paid",
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            recorded_by_id=recorded_by_id
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

    @staticmethod
    async def get_payment(session: Session, payment_id: UUID) -> Optional[BudgetPayment]:
        """Get payment by ID"""
        statement = select(BudgetPayment).where(BudgetPayment.id == payment_id)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_church_payments(session: Session, local_church_budget_id: UUID) -> List[BudgetPayment]:
        """Get all payments for a church budget"""
        statement = select(BudgetPayment).where(
            BudgetPayment.local_church_budget_id == local_church_budget_id
        ).order_by(BudgetPayment.payment_year.desc(), BudgetPayment.payment_month.desc())
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_overdue_payments(session: Session, local_church_budget_id: UUID) -> List[BudgetPayment]:
        """Get overdue payments for a church"""
        statement = select(BudgetPayment).where(
            and_(
                BudgetPayment.local_church_budget_id == local_church_budget_id,
                BudgetPayment.status == "pending",
                BudgetPayment.due_date < datetime.now()
            )
        )
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_monthly_pending_payments(session: Session, payment_year: int, payment_month: int) -> List[BudgetPayment]:
        """Get all pending payments for a specific month"""
        statement = select(BudgetPayment).where(
            and_(
                BudgetPayment.payment_year == payment_year,
                BudgetPayment.payment_month == payment_month,
                BudgetPayment.status == "pending"
            )
        )
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def update_payment(session: Session, payment_id: UUID, **kwargs) -> Optional[BudgetPayment]:
        """Update payment details"""
        statement = select(BudgetPayment).where(BudgetPayment.id == payment_id)
        result = await session.exec(statement)
        payment = result.first()
        if payment:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(payment, key, value)
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
        return payment

    # ==================== Reports ====================

    @staticmethod
    async def calculate_church_budget_summary(session: Session, church_budget_id: UUID) -> dict:
        """Calculate summary for a church budget"""
        statement = select(LocalChurchBudget).where(
            LocalChurchBudget.id == church_budget_id)
        result = await session.exec(statement)
        budget = result.first()

        if not budget:
            return {}

        # Get all payments
        payments = await BudgetService.get_church_payments(session, church_budget_id)

        total_paid = sum(p.amount_paid for p in payments if p.status == "paid")
        total_pending = Decimal(0)
        total_overdue = Decimal(0)

        for payment in payments:
            if payment.status == "pending":
                if payment.due_date < datetime.now():
                    total_overdue += payment.amount_paid
                else:
                    total_pending += payment.amount_paid

        return {
            "allocated_amount": budget.allocated_amount,
            "paid_amount": total_paid,
            "pending_amount": total_pending,
            "overdue_amount": total_overdue,
            "completion_percentage": float((total_paid / budget.allocated_amount * 100) if budget.allocated_amount > 0 else 0)
        }

    @staticmethod
    async def get_dashboard_summary(session: Session) -> BudgetReport:
        """Get dashboard summary of budget status"""
        current_budget = await BudgetService.get_current_yearly_budget(session)

        if not current_budget:
            return BudgetReport(
                total_budget=Decimal(0),
                total_allocated=Decimal(0),
                total_paid=Decimal(0),
                total_pending=Decimal(0),
                total_overdue=Decimal(0),
                budget_utilization=0,
                churches_count=0,
                payments_count=0,
                overdue_count=0
            )

        # Get all church budgets under current yearly budget
        statement = select(LocalChurchBudget).join(DCCBudget).where(
            DCCBudget.yearly_budget_id == current_budget.id
        )
        result = await session.exec(statement)
        church_budgets = result.all()

        total_allocated = sum(cb.allocated_amount for cb in church_budgets)
        total_paid = Decimal(0)
        total_pending = Decimal(0)
        total_overdue = Decimal(0)

        # Calculate payments
        payment_statement = select(BudgetPayment).where(
            BudgetPayment.local_church_budget_id.in_(
                [cb.id for cb in church_budgets])
        )
        payment_result = await session.exec(payment_statement)
        all_payments = payment_result.all()

        for payment in all_payments:
            if payment.status == "paid":
                total_paid += payment.amount_paid
            elif payment.status == "pending":
                if payment.due_date < datetime.now():
                    total_overdue += payment.amount_paid
                else:
                    total_pending += payment.amount_paid

        overdue_count = sum(1 for p in all_payments if p.status ==
                            "pending" and p.due_date < datetime.now())

        return {
            "total_budget": current_budget.total_budget,
            "total_allocated": total_allocated,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_overdue": total_overdue,
            "budget_utilization": float(
                (total_allocated / current_budget.total_budget * 100) if current_budget.total_budget > 0 else 0),
            "churches_count": len(church_budgets),
            "payments_count": len(all_payments),
            "overdue_count": overdue_count
        }
