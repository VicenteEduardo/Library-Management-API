"""Liga os pontos: quando chega um pedido, diz que repositório usar."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories import (
    SQLAlchemyBookRepository,
    SQLAlchemyLoanRepository,
    SQLAlchemyMemberRepository,
)


def get_book_repo(db: Session = Depends(get_db)) -> SQLAlchemyBookRepository:
    return SQLAlchemyBookRepository(db)


def get_member_repo(db: Session = Depends(get_db)) -> SQLAlchemyMemberRepository:
    return SQLAlchemyMemberRepository(db)


def get_loan_repo(db: Session = Depends(get_db)) -> SQLAlchemyLoanRepository:
    return SQLAlchemyLoanRepository(db)
