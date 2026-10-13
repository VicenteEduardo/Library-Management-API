from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases import (
    BorrowBook,
    GetLoan,
    ListLoans,
    ListOverdueLoans,
    ReturnBook,
)
from app.domain.exceptions import BusinessRuleError, NotFoundError
from app.infrastructure.repositories import (
    SQLAlchemyBookRepository,
    SQLAlchemyLoanRepository,
    SQLAlchemyMemberRepository,
)
from app.interfaces.api.dependencies import (
    get_book_repo,
    get_loan_repo,
    get_member_repo,
)
from app.interfaces.api.schemas import BorrowRequest, LoanResponse

router = APIRouter(prefix="/loans", tags=["loans"])


def _to_response(loan) -> LoanResponse:
    return LoanResponse(
        id=loan.id, book_id=loan.book_id, member_id=loan.member_id,
        loan_date=loan.loan_date, due_date=loan.due_date,
        return_date=loan.return_date, is_overdue=loan.is_overdue,
    )


@router.post("/borrow", response_model=LoanResponse,
             status_code=status.HTTP_201_CREATED, summary="Emprestar livro")
def borrow(payload: BorrowRequest,
           books: SQLAlchemyBookRepository = Depends(get_book_repo),
           members: SQLAlchemyMemberRepository = Depends(get_member_repo),
           loans: SQLAlchemyLoanRepository = Depends(get_loan_repo)):
    try:
        loan = BorrowBook(books, members, loans).execute(
            payload.book_id, payload.member_id, payload.days)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_response(loan)


@router.post("/{loan_id}/return", response_model=LoanResponse,
             summary="Devolver livro")
def return_loan(loan_id: int,
                books: SQLAlchemyBookRepository = Depends(get_book_repo),
                loans: SQLAlchemyLoanRepository = Depends(get_loan_repo)):
    try:
        return _to_response(ReturnBook(books, loans).execute(loan_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[LoanResponse],
            summary="Listar empréstimos")
def list_loans(skip: int = 0, limit: int = 100,
               loans: SQLAlchemyLoanRepository = Depends(get_loan_repo)):
    return [_to_response(loan) for loan in ListLoans(loans).execute(skip, limit)]


@router.get("/overdue", response_model=list[LoanResponse],
            summary="Listar empréstimos atrasados")
def list_overdue(loans: SQLAlchemyLoanRepository = Depends(get_loan_repo)):
    return [_to_response(loan) for loan in ListOverdueLoans(loans).execute()]


@router.get("/{loan_id}", response_model=LoanResponse,
            summary="Obter empréstimo")
def get_loan(loan_id: int,
             loans: SQLAlchemyLoanRepository = Depends(get_loan_repo)):
    try:
        return _to_response(GetLoan(loans).execute(loan_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
