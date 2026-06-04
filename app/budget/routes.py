from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import List

from app.db.database import get_session
from app.budget.models import (
    YearlyBudget, DCCBudget, LocalChurchBudget, BudgetPayment,
    VoteHead, DCCVoteHeadBudget, LocalChurchVoteHeadBudget
)
from app.budget.models import (
    YearlyBudgetCreate, YearlyBudgetUpdate, YearlyBudgetRead,
    DCCBudgetCreate, DCCBudgetUpdate, DCCBudgetRead,
    LocalChurchBudgetCreate, LocalChurchBudgetUpdate, LocalChurchBudgetRead,
    BudgetPaymentCreate, BudgetPaymentUpdate, BudgetPaymentRead,
    VoteHeadCreate, VoteHeadRead,
    DCCVoteHeadBudgetCreate, DCCVoteHeadBudgetRead,
    LocalChurchVoteHeadBudgetCreate, LocalChurchVoteHeadBudgetRead
)
from app.budget.services import BudgetService


router = APIRouter(prefix="/api/budget", tags=["budget"])


# ==================== Dashboard ====================

@router.get("/dashboard")
async def get_budget_dashboard(request: Request,
                               session: Session = Depends(get_session)
                               ):
    """Get budget dashboard summary"""
    current_user = request.state.user["user"]["user_id"]
    return await BudgetService.get_dashboard_summary(session)


# ==================== Yearly Budget Endpoints ====================

@router.post("/yearly", response_model=YearlyBudgetRead)
async def create_yearly_budget(request: Request,
                               budget_data: YearlyBudgetCreate,
                               session: Session = Depends(get_session),

                               ):
    """Create a new yearly budget (Admin only)"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.create_yearly_budget(
        session,
        year=budget_data.year,
        total_budget=budget_data.total_budget,
        description=budget_data.description
    )
    return budget


@router.get("/yearly/{budget_id}", response_model=YearlyBudgetRead)
async def get_yearly_budget(request: Request,
                            budget_id: UUID,
                            session: Session = Depends(get_session),

                            ):
    """Get yearly budget by ID"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.get_yearly_budget(session, budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


@router.get("/yearly", response_model=List[YearlyBudgetRead])
async def get_yearly_budgets(request: Request,
                             year: int = None,
                             session: Session = Depends(get_session),

                             ):
    """Get yearly budgets"""
    current_user = request.state.user["user"]["user_id"]
    budgets = await BudgetService.get_yearly_budgets(session, year=year)
    return budgets


@router.get("/yearly/current", response_model=YearlyBudgetRead)
async def get_current_yearly_budget(request: Request,
                                    session: Session = Depends(get_session),

                                    ):
    """Get current year's yearly budget"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.get_current_yearly_budget(session)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No budget for current year")
    return budget


@router.put("/yearly/{budget_id}", response_model=YearlyBudgetRead)
async def update_yearly_budget(request: Request,
                               budget_id: UUID,
                               budget_data: YearlyBudgetUpdate,
                               session: Session = Depends(get_session),

                               ):
    """Update yearly budget"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.update_yearly_budget(
        session,
        budget_id,
        **budget_data.dict(exclude_unset=True)
    )
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


# ==================== DCC Budget Endpoints ====================

@router.post("/dcc", response_model=DCCBudgetRead)
async def create_dcc_budget(request: Request,
                            budget_data: DCCBudgetCreate,
                            session: Session = Depends(get_session),

                            ):
    """Allocate budget to DCC"""
    current_user = request.state.user["user"]["user_id"]
    dcc_budget = await BudgetService.create_dcc_budget(
        session,
        yearly_budget_id=budget_data.yearly_budget_id,
        dcc_id=budget_data.dcc_id,
        allocated_amount=budget_data.allocated_amount
    )
    return dcc_budget


@router.get("/dcc/{dcc_budget_id}", response_model=DCCBudgetRead)
async def get_dcc_budget(request: Request,
                         dcc_budget_id: UUID,
                         session: Session = Depends(get_session),
                         ):
    """Get DCC budget by ID"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.get_dcc_budget(session, dcc_budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="DCC budget not found")
    return budget


@router.get("/dcc/year/{year}", response_model=List[DCCBudgetRead])
async def get_dcc_budgets_by_year(request: Request,
                                  year: int,
                                  session: Session = Depends(get_session),

                                  ):
    """Get all DCC budgets for a specific year"""
    current_user = request.state.user["user"]["user_id"]
    budgets = await BudgetService.get_dcc_budgets_by_year(session, year)
    return budgets


@router.post("/dcc/{dcc_budget_id}/vote-heads", response_model=DCCVoteHeadBudgetRead)
async def allocate_dcc_vote_head(request: Request,
                                 dcc_budget_id: UUID,
                                 vote_head_data: DCCVoteHeadBudgetCreate,
                                 session: Session = Depends(get_session),

                                 ):
    """Allocate a vote head budget to a DCC budget"""
    current_user = request.state.user["user"]["user_id"]
    return await BudgetService.create_dcc_vote_head_budget(
        session,
        dcc_budget_id=dcc_budget_id,
        vote_head_id=vote_head_data.vote_head_id,
        allocated_amount=vote_head_data.allocated_amount
    )


@router.get("/dcc/{dcc_budget_id}/vote-heads", response_model=List[DCCVoteHeadBudgetRead])
async def list_dcc_vote_head_allocations(request: Request,
                                         dcc_budget_id: UUID,
                                         session: Session = Depends(
                                             get_session),

                                         ):
    """Get vote head allocations for a DCC budget"""
    current_user = request.state.user["user"]["user_id"]
    return await BudgetService.get_dcc_vote_head_budgets(session, dcc_budget_id)


@router.get("/vote-heads", response_model=List[VoteHeadRead])
async def list_vote_heads(request: Request,
                          session: Session = Depends(get_session),

                          ):
    """Get all vote head categories"""
    current_user = request.state.user["user"]["user_id"]
    return await BudgetService.get_vote_heads(session)


@router.post("/vote-heads", response_model=VoteHeadRead)
async def create_vote_head(request: Request,
                           vote_head_data: VoteHeadCreate,
                           session: Session = Depends(get_session),

                           ):
    """Create a new vote head category"""
    current_user = request.state.user["user"]["user_id"]
    return await BudgetService.create_vote_head(
        session,
        name=vote_head_data.name,
        code=vote_head_data.code,
        description=vote_head_data.description
    )


@router.post("/dcc/{dcc_budget_id}/approve", response_model=DCCBudgetRead)
async def approve_dcc_budget(request: Request,
                             dcc_budget_id: UUID,
                             session: Session = Depends(get_session),

                             ):
    """Approve DCC budget allocation"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.approve_dcc_budget(session, dcc_budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="DCC budget not found")
    return budget


@router.post("/dcc/{dcc_budget_id}/reject", response_model=DCCBudgetRead)
async def reject_dcc_budget(request: Request,
                            dcc_budget_id: UUID,
                            session: Session = Depends(get_session),

                            ):
    """Reject DCC budget allocation"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.reject_dcc_budget(session, dcc_budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="DCC budget not found")
    return budget


# ==================== Local Church Budget Endpoints ====================

@router.post("/church", response_model=LocalChurchBudgetRead)
async def create_church_budget(request: Request,
                               budget_data: LocalChurchBudgetCreate,
                               session: Session = Depends(get_session),

                               ):
    """Allocate budget to local church"""
    current_user = request.state.user["user"]["user_id"]
    church_budget = await BudgetService.create_local_church_budget(
        session,
        dcc_budget_id=budget_data.dcc_budget_id,
        local_church_id=budget_data.local_church_id,
        allocated_amount=budget_data.allocated_amount
    )
    return church_budget


@router.get("/church/list/all", response_model=List[LocalChurchBudgetRead])
async def get_all_church_budgets(request: Request,
                                 session: Session = Depends(get_session),

                                 ):
    """Get all church budgets across all DCCs"""
    current_user = request.state.user["user"]["user_id"]
    budgets = await BudgetService.get_all_church_budgets(session)
    return budgets


@router.get("/church/{church_budget_id}", response_model=LocalChurchBudgetRead)
async def get_church_budget(request: Request,
                            church_budget_id: UUID,
                            session: Session = Depends(get_session),

                            ):
    """Get church budget by ID"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.get_local_church_budget(session, church_budget_id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Church budget not found")
    return budget


@router.get("/church/dcc/{dcc_budget_id}", response_model=List[LocalChurchBudgetRead])
async def get_church_budgets_by_dcc(request: Request,
                                    dcc_budget_id: UUID,
                                    session: Session = Depends(get_session),

                                    ):
    """Get all church budgets under a DCC"""
    current_user = request.state.user["user"]["user_id"]
    budgets = await BudgetService.get_church_budgets_by_dcc(session, dcc_budget_id)
    return budgets


@router.post("/church/{church_budget_id}/vote-heads", response_model=LocalChurchVoteHeadBudgetRead)
async def allocate_local_church_vote_head(request: Request,
                                          church_budget_id: UUID,
                                          vote_head_data: LocalChurchVoteHeadBudgetCreate,
                                          session: Session = Depends(
                                              get_session),

                                          ):
    """Allocate a vote head for a local church budget"""
    current_user = request.state.user["user"]["user_id"]
    return await BudgetService.create_local_church_vote_head_budget(
        session,
        local_church_budget_id=church_budget_id,
        vote_head_id=vote_head_data.vote_head_id,
        allocated_amount=vote_head_data.allocated_amount
    )


@router.get("/church/{church_budget_id}/vote-heads", response_model=List[LocalChurchVoteHeadBudgetRead])
async def list_local_church_vote_head_allocations(request: Request,
                                                  church_budget_id: UUID,
                                                  session: Session = Depends(
                                                      get_session),

                                                  ):
    """Get vote head allocations for a local church budget"""
    current_user = request.state.user["user"]["user_id"]
    return await BudgetService.get_local_church_vote_head_budgets(session, church_budget_id)


@router.post("/church/{church_budget_id}/approve", response_model=LocalChurchBudgetRead)
async def approve_church_budget(request: Request,
                                church_budget_id: UUID,
                                session: Session = Depends(get_session),

                                ):
    """Approve church budget allocation"""
    current_user = request.state.user["user"]["user_id"]
    budget = await BudgetService.approve_church_budget(session, church_budget_id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Church budget not found")
    return budget


@router.get("/church/{church_budget_id}/summary")
async def get_church_budget_summary(request: Request,
                                    church_budget_id: UUID,
                                    session: Session = Depends(get_session),

                                    ):
    """Get summary of church budget and payments"""
    current_user = request.state.user["user"]["user_id"]
    summary = await BudgetService.calculate_church_budget_summary(session, church_budget_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Church budget not found")
    return summary


# ==================== Payment Endpoints ====================

@router.post("/payment", response_model=BudgetPaymentRead)
async def record_payment(
    request: Request,
    payment_data: BudgetPaymentCreate,
    session: Session = Depends(get_session),

):
    """Record a budget payment"""
    current_user = request.state.user["user"]["user_id"]
    payment = await BudgetService.create_payment(
        session,
        local_church_budget_id=payment_data.local_church_budget_id,
        payment_month=payment_data.payment_month,
        payment_year=payment_data.payment_year,
        amount_paid=payment_data.amount_paid,
        due_date=payment_data.due_date,
        recorded_by_id=current_user.id,
        payment_method=payment_data.payment_method,
        reference_number=payment_data.reference_number,
        notes=payment_data.notes
    )
    return payment


@router.get("/payment/{payment_id}", response_model=BudgetPaymentRead)
async def get_payment(
    request: Request,
    payment_id: UUID,
    session: Session = Depends(get_session),

):
    """Get payment by ID"""
    current_user = request.state.user["user"]["user_id"]
    payment = await BudgetService.get_payment(session, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment


@router.get("/payments/church/{church_budget_id}", response_model=List[BudgetPaymentRead])
async def get_church_payments(
    request: Request,
    church_budget_id: UUID,
    session: Session = Depends(get_session),

):
    """Get all payments for a church"""
    current_user = request.state.user["user"]["user_id"]
    payments = await BudgetService.get_church_payments(session, church_budget_id)
    return payments


@router.get("/payments/overdue/{church_budget_id}", response_model=List[BudgetPaymentRead])
async def get_overdue_payments(
    request: Request,
    church_budget_id: UUID,
    session: Session = Depends(get_session),

):
    """Get overdue payments for a church"""
    current_user = request.state.user["user"]["user_id"]
    payments = await BudgetService.get_overdue_payments(session, church_budget_id)
    return payments


@router.get("/payments/monthly/{year}/{month}", response_model=List[BudgetPaymentRead])
async def get_monthly_payments(
    request: Request,
    year: int,
    month: int,
    session: Session = Depends(get_session),

):
    """Get all pending payments for a specific month"""
    current_user = request.state.user["user"]["user_id"]
    payments = await BudgetService.get_monthly_pending_payments(session, year, month)
    return payments


@router.put("/payment/{payment_id}", response_model=BudgetPaymentRead)
async def update_payment(
    request: Request,
    payment_id: UUID,
    payment_data: BudgetPaymentUpdate,
    session: Session = Depends(get_session),

):
    """Update payment details"""
    current_user = request.state.user["user"]["user_id"]
    payment = await BudgetService.update_payment(
        session,
        payment_id,
        **payment_data.dict(exclude_unset=True)
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment
