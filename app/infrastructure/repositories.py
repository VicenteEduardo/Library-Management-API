"""Aqui cumprimos o contrato: guardamos e vamos buscar coisas usando SQLAlchemy."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities import Book, Loan, Member
from app.domain.repositories import BookRepository, LoanRepository, MemberRepository
from app.infrastructure.models import BookModel, LoanModel, MemberModel


def _book_to_entity(m: BookModel) -> Book:
    return Book(id=m.id, title=m.title, author=m.author, isbn=m.isbn,
                total_copies=m.total_copies, available_copies=m.available_copies,
                published_year=m.published_year)


def _member_to_entity(m: MemberModel) -> Member:
    return Member(id=m.id, name=m.name, email=m.email, is_active=m.is_active)


def _loan_to_entity(m: LoanModel) -> Loan:
    return Loan(id=m.id, book_id=m.book_id, member_id=m.member_id,
                loan_date=m.loan_date, due_date=m.due_date,
                return_date=m.return_date)


class SQLAlchemyBookRepository(BookRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, book: Book) -> Book:
        model = BookModel(title=book.title, author=book.author, isbn=book.isbn,
                          total_copies=book.total_copies,
                          available_copies=book.available_copies,
                          published_year=book.published_year)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _book_to_entity(model)

    def get_by_id(self, book_id: int) -> Optional[Book]:
        m = self.db.get(BookModel, book_id)
        return _book_to_entity(m) if m else None

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        m = self.db.query(BookModel).filter(BookModel.isbn == isbn).first()
        return _book_to_entity(m) if m else None

    def list(self, skip: int = 0, limit: int = 100) -> List[Book]:
        rows = self.db.query(BookModel).offset(skip).limit(limit).all()
        return [_book_to_entity(m) for m in rows]

    def update(self, book: Book) -> Book:
        m = self.db.get(BookModel, book.id)
        assert m is not None
        m.title = book.title
        m.author = book.author
        m.isbn = book.isbn
        m.total_copies = book.total_copies
        m.available_copies = book.available_copies
        m.published_year = book.published_year
        self.db.commit()
        self.db.refresh(m)
        return _book_to_entity(m)

    def delete(self, book_id: int) -> None:
        m = self.db.get(BookModel, book_id)
        if m:
            self.db.delete(m)
            self.db.commit()


class SQLAlchemyMemberRepository(MemberRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, member: Member) -> Member:
        model = MemberModel(name=member.name, email=member.email,
                            is_active=member.is_active)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _member_to_entity(model)

    def get_by_id(self, member_id: int) -> Optional[Member]:
        m = self.db.get(MemberModel, member_id)
        return _member_to_entity(m) if m else None

    def get_by_email(self, email: str) -> Optional[Member]:
        m = self.db.query(MemberModel).filter(MemberModel.email == email).first()
        return _member_to_entity(m) if m else None

    def list(self, skip: int = 0, limit: int = 100) -> List[Member]:
        rows = self.db.query(MemberModel).offset(skip).limit(limit).all()
        return [_member_to_entity(m) for m in rows]

    def update(self, member: Member) -> Member:
        m = self.db.get(MemberModel, member.id)
        assert m is not None
        m.name = member.name
        m.email = member.email
        m.is_active = member.is_active
        self.db.commit()
        self.db.refresh(m)
        return _member_to_entity(m)

    def delete(self, member_id: int) -> None:
        m = self.db.get(MemberModel, member_id)
        if m:
            self.db.delete(m)
            self.db.commit()


class SQLAlchemyLoanRepository(LoanRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, loan: Loan) -> Loan:
        model = LoanModel(book_id=loan.book_id, member_id=loan.member_id,
                          loan_date=loan.loan_date, due_date=loan.due_date,
                          return_date=loan.return_date)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _loan_to_entity(model)

    def get_by_id(self, loan_id: int) -> Optional[Loan]:
        m = self.db.get(LoanModel, loan_id)
        return _loan_to_entity(m) if m else None

    def list(self, skip: int = 0, limit: int = 100) -> List[Loan]:
        rows = self.db.query(LoanModel).offset(skip).limit(limit).all()
        return [_loan_to_entity(m) for m in rows]

    def list_active_by_member(self, member_id: int) -> List[Loan]:
        rows = (self.db.query(LoanModel)
                .filter(LoanModel.member_id == member_id,
                        LoanModel.return_date.is_(None)).all())
        return [_loan_to_entity(m) for m in rows]

    def find_active(self, book_id: int, member_id: int) -> Optional[Loan]:
        m = (self.db.query(LoanModel)
             .filter(LoanModel.book_id == book_id,
                     LoanModel.member_id == member_id,
                     LoanModel.return_date.is_(None)).first())
        return _loan_to_entity(m) if m else None

    def update(self, loan: Loan) -> Loan:
        m = self.db.get(LoanModel, loan.id)
        assert m is not None
        m.return_date = loan.return_date
        m.due_date = loan.due_date
        self.db.commit()
        self.db.refresh(m)
        return _loan_to_entity(m)
