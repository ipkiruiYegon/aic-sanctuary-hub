from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.users.models import User
    from app.council.models import Church, District, Region

# Yearly Budget


class YearlyBudgetBase(SQLModel):
    year: int
    total_budget: Decimal
    description: Optional[str] = None


class YearlyBudgetCreate(YearlyBudgetBase):
    pass


class YearlyBudgetUpdate(SQLModel):
    total_budget: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class YearlyBudgetRead(YearlyBudgetBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class YearlyBudget(SQLModel, table=True):
    __tablename__ = "yearly_budgets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    year: int = Field(index=True)
    total_budget: Decimal = Field(decimal_places=2, max_digits=15)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now(), onupdate=func.now()))

    dcc_budgets: List["DCCBudget"] = Relationship(
        back_populates="yearly_budget")
    income_sources: List["BudgetIncomeSource"] = Relationship(
        back_populates="yearly_budget")


# -----------------------------
# DCC Budget
# -----------------------------
class DCCBudgetBase(SQLModel):
    yearly_budget_id: UUID
    dcc_id: UUID
    allocated_amount: Decimal


class DCCBudgetCreate(DCCBudgetBase):
    pass


class DCCBudgetUpdate(SQLModel):
    allocated_amount: Optional[Decimal] = None
    status: Optional[str] = None


class DCCBudgetRead(DCCBudgetBase):
    id: UUID
    status: str
    approval_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DCCBudget(SQLModel, table=True):
    __tablename__ = "dcc_budgets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    yearly_budget_id: UUID = Field(foreign_key="yearly_budgets.id", index=True)
    dcc_id: UUID = Field(foreign_key="churches.id", index=True)
    allocated_amount: Decimal = Field(decimal_places=2, max_digits=15)
    status: str = Field(default="pending")
    approval_date: Optional[datetime] = None
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now(), onupdate=func.now()))

    yearly_budget: YearlyBudget = Relationship(back_populates="dcc_budgets")
    dcc: "Church" = Relationship(back_populates="dcc_budgets")
    local_church_budgets: List["LocalChurchBudget"] = Relationship(
        back_populates="dcc_budget")
    vote_head_budgets: List["DCCVoteHeadBudget"] = Relationship(
        back_populates="dcc_budget")
    income_sources: List["BudgetIncomeSource"] = Relationship(
        back_populates="dcc_budget")


# -----------------------------
# Local Church Budget
# -----------------------------
class LocalChurchBudgetBase(SQLModel):
    dcc_budget_id: UUID
    local_church_id: UUID
    allocated_amount: Decimal


class LocalChurchBudgetCreate(LocalChurchBudgetBase):
    pass


class LocalChurchBudgetUpdate(SQLModel):
    allocated_amount: Optional[Decimal] = None
    status: Optional[str] = None


class LocalChurchBudgetRead(LocalChurchBudgetBase):
    id: UUID
    status: str
    approval_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocalChurchBudget(SQLModel, table=True):
    __tablename__ = "local_church_budgets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    dcc_budget_id: UUID = Field(foreign_key="dcc_budgets.id", index=True)
    local_church_id: UUID = Field(foreign_key="churches.id", index=True)
    allocated_amount: Decimal = Field(decimal_places=2, max_digits=15)
    status: str = Field(default="pending")
    approval_date: Optional[datetime] = None
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now(), onupdate=func.now()))

    dcc_budget: DCCBudget = Relationship(back_populates="local_church_budgets")
    local_church: "Church" = Relationship(back_populates="church_budgets")
    payments: List["BudgetPayment"] = Relationship(
        back_populates="local_church_budget")
    vote_head_budgets: List["LocalChurchVoteHeadBudget"] = Relationship(
        back_populates="local_church_budget"
    )
    income_sources: List["BudgetIncomeSource"] = Relationship(
        back_populates="local_church_budget")


# -----------------------------
# Budget Payment
# -----------------------------
class BudgetPaymentBase(SQLModel):
    local_church_budget_id: UUID
    payment_month: int = Field(ge=1, le=12)
    payment_year: int
    amount_paid: Decimal
    due_date: datetime
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class BudgetPaymentCreate(BudgetPaymentBase):
    pass


class BudgetPaymentUpdate(SQLModel):
    amount_paid: Optional[Decimal] = None
    payment_date: Optional[datetime] = None
    status: Optional[str] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class BudgetPaymentRead(BudgetPaymentBase):
    id: UUID
    payment_date: Optional[datetime]
    status: str
    recorded_by_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetPayment(SQLModel, table=True):
    __tablename__ = "budget_payments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    local_church_budget_id: UUID = Field(
        foreign_key="local_church_budgets.id", index=True)
    payment_month: int = Field(ge=1, le=12)
    payment_year: int
    amount_paid: Decimal = Field(decimal_places=2, max_digits=15)
    due_date: datetime
    payment_date: Optional[datetime] = None
    status: str = Field(default="pending")
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    recorded_by_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now(), onupdate=func.now()))

    local_church_budget: LocalChurchBudget = Relationship(
        back_populates="payments")
    recorded_by: "User" = Relationship(back_populates="budget_payments")


# -----------------------------
# Budget Report
# -----------------------------
class BudgetReportBase(SQLModel):
    report_type: str
    report_year: int
    report_month: Optional[int]
    dcc_id: Optional[UUID]
    local_church_id: Optional[UUID]
    total_budgeted: Decimal
    total_paid: Decimal
    total_pending: Decimal
    total_overdue: Decimal
    completion_percentage: float
    generated_by_id: UUID


class BudgetReportRead(BudgetReportBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class BudgetReport(SQLModel, table=True):
    __tablename__ = "budget_reports"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    report_type: str = Field(index=True)
    report_year: int
    report_month: Optional[int]
    dcc_id: Optional[UUID] = Field(foreign_key="churches.id")
    local_church_id: Optional[UUID] = Field(foreign_key="churches.id")
    total_budgeted: Decimal = Field(decimal_places=2, max_digits=15)
    total_paid: Decimal = Field(decimal_places=2, max_digits=15)
    total_pending: Decimal = Field(decimal_places=2, max_digits=15)
    total_overdue: Decimal = Field(decimal_places=2, max_digits=15)
    completion_percentage: float
    generated_by_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))

    generated_by: "User" = Relationship(back_populates="budget_reports")


# =============================
# Budget Income Sources
# =============================
class BudgetIncomeSourceBase(SQLModel):
    yearly_budget_id: Optional[UUID] = None
    dcc_budget_id: Optional[UUID] = None
    local_church_budget_id: Optional[UUID] = None
    source_type: str
    amount: Decimal = Field(decimal_places=2, max_digits=15)
    description: Optional[str] = None
    received_date: datetime = Field(default_factory=datetime.now)


class BudgetIncomeSourceCreate(BudgetIncomeSourceBase):
    pass


class BudgetIncomeSourceUpdate(SQLModel):
    source_type: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    received_date: Optional[datetime] = None


class BudgetIncomeSourceRead(BudgetIncomeSourceBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class BudgetIncomeSource(SQLModel, table=True):
    __tablename__ = "budget_income_sources"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    yearly_budget_id: Optional[UUID] = Field(
        default=None, foreign_key="yearly_budgets.id", index=True)
    dcc_budget_id: Optional[UUID] = Field(
        default=None, foreign_key="dcc_budgets.id", index=True)
    local_church_budget_id: Optional[UUID] = Field(
        default=None, foreign_key="local_church_budgets.id", index=True)
    source_type: str = Field(nullable=False)
    amount: Decimal = Field(decimal_places=2, max_digits=15)
    description: Optional[str] = None
    received_date: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))

    yearly_budget: Optional["YearlyBudget"] = Relationship(
        back_populates="income_sources")
    dcc_budget: Optional["DCCBudget"] = Relationship(
        back_populates="income_sources")
    local_church_budget: Optional["LocalChurchBudget"] = Relationship(
        back_populates="income_sources")


# =============================
# Vote Head (Regional Budget Categories)
# =============================
class VoteHeadBase(SQLModel):
    name: str
    code: str
    description: Optional[str] = None


class VoteHeadCreate(VoteHeadBase):
    pass


class VoteHeadUpdate(SQLModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class VoteHeadRead(VoteHeadBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VoteHead(SQLModel, table=True):
    __tablename__ = "vote_heads"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    code: str = Field(unique=True, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now(), onupdate=func.now()))

    dcc_vote_budgets: List["DCCVoteHeadBudget"] = Relationship(
        back_populates="vote_head")
    local_church_vote_budgets: List["LocalChurchVoteHeadBudget"] = Relationship(
        back_populates="vote_head")


# =============================
# DCC Vote Head Budget Allocation
# =============================
class DCCVoteHeadBudgetBase(SQLModel):
    dcc_budget_id: UUID
    vote_head_id: UUID
    allocated_amount: Decimal


class DCCVoteHeadBudgetCreate(DCCVoteHeadBudgetBase):
    pass


class DCCVoteHeadBudgetUpdate(SQLModel):
    allocated_amount: Optional[Decimal] = None


class DCCVoteHeadBudgetRead(DCCVoteHeadBudgetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DCCVoteHeadBudget(SQLModel, table=True):
    __tablename__ = "dcc_vote_head_budgets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    dcc_budget_id: UUID = Field(
        foreign_key="dcc_budgets.id", index=True)
    vote_head_id: UUID = Field(foreign_key="vote_heads.id", index=True)
    allocated_amount: Decimal = Field(decimal_places=2, max_digits=15)
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now(), onupdate=func.now()))

    dcc_budget: DCCBudget = Relationship(back_populates="vote_head_budgets")
    vote_head: VoteHead = Relationship(back_populates="dcc_vote_budgets")


# =============================
# Local Church Vote Head Budget Allocation
# =============================
class LocalChurchVoteHeadBudgetBase(SQLModel):
    local_church_budget_id: UUID
    vote_head_id: UUID
    allocated_amount: Decimal


class LocalChurchVoteHeadBudgetCreate(LocalChurchVoteHeadBudgetBase):
    pass


class LocalChurchVoteHeadBudgetUpdate(SQLModel):
    allocated_amount: Optional[Decimal] = None


class LocalChurchVoteHeadBudgetRead(LocalChurchVoteHeadBudgetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocalChurchVoteHeadBudget(SQLModel, table=True):
    __tablename__ = "local_church_vote_head_budgets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    local_church_budget_id: UUID = Field(
        foreign_key="local_church_budgets.id", index=True)
    vote_head_id: UUID = Field(foreign_key="vote_heads.id", index=True)
    allocated_amount: Decimal = Field(decimal_places=2, max_digits=15)
    spent_amount: Decimal = Field(default=0, decimal_places=2, max_digits=15)
    created_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(
        DateTime, server_default=func.now(), onupdate=func.now()))

    local_church_budget: LocalChurchBudget = Relationship(
        back_populates="vote_head_budgets")
    vote_head: VoteHead = Relationship(
        back_populates="local_church_vote_budgets")
