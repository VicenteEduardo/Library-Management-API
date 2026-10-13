"""Testes dos casos de uso com repositórios a fingir (em memória), sem base de dados."""
from typing import Dict, List, Optional

import pytest

from app.application.use_cases import BorrowBook, CreateBook, ReturnBook
from app.domain.entities import Book, Loan, Member
from app.domain.exceptions import BusinessRuleError, ConflictError


class FakeBooks:
    def __init__(self):
        self.store: Dict[int, Book] = {}
        self.seq = 1

    def add(self, book: Book) -> Book:
        book.id = self.seq
        self.seq += 1
        self.store[book.id] = book
        return book

    def get_by_id(self, book_id: int) -> Optional[Book]:
        return self.store.get(book_id)

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return next((b for b in self.store.values() if b.isbn == isbn), None)

    def list(self, skip=0, limit=100) -> List[Book]:
        return list(self.store.values())[skip:skip + limit]

    def update(self, book: Book) -> Book:
        self.store[book.id] = book  # type: ignore
        return book

    def delete(self, book_id: int) -> None:
        self.store.pop(book_id, None)


class FakeMembers:
    def __init__(self):
        self.store: Dict[int, Member] = {1: Member(id=1, name="Ana",
                                                   email="ana@mail.com")}

    def get_by_id(self, member_id: int) -> Optional[Member]:
        return self.store.get(member_id)

    def get_by_email(self, email: str) -> Optional[Member]:
        return None

    def add(self, m: Member) -> Member:
        return m

    def list(self, skip=0, limit=100) -> List[Member]:
        return list(self.store.values())

    def update(self, m: Member) -> Member:
        return m

    def delete(self, member_id: int) -> None:
        pass


class FakeLoans:
    def __init__(self):
        self.store: Dict[int, Loan] = {}
        self.seq = 1

    def add(self, loan: Loan) -> Loan:
        loan.id = self.seq
        self.seq += 1
        self.store[loan.id] = loan
        return loan

    def get_by_id(self, loan_id: int) -> Optional[Loan]:
        return self.store.get(loan_id)

    def list(self, skip=0, limit=100) -> List[Loan]:
        return list(self.store.values())

    def list_active_by_member(self, member_id: int) -> List[Loan]:
        return [loan for loan in self.store.values()
                if loan.member_id == member_id and not loan.is_returned]

    def find_active(self, book_id: int, member_id: int) -> Optional[Loan]:
        return next((loan for loan in self.store.values()
                     if loan.book_id == book_id and loan.member_id == member_id
                     and not loan.is_returned), None)

    def update(self, loan: Loan) -> Loan:
        self.store[loan.id] = loan  # type: ignore
        return loan


def test_create_book_conflict_isbn():
    books = FakeBooks()
    CreateBook(books).execute("T", "A", "ISBN-1")
    with pytest.raises(ConflictError):
        CreateBook(books).execute("T2", "A2", "ISBN-1")


def test_borrow_decrements_availability_and_return_increments():
    books = FakeBooks()
    book = books.add(Book(title="T", author="A", isbn="X", total_copies=1))
    loans = FakeLoans()
    loan = BorrowBook(books, FakeMembers(), loans).execute(book.id, 1)
    assert book.available_copies == 0
    ReturnBook(books, loans).execute(loan.id)
    assert book.available_copies == 1


def test_borrow_without_copies_fails():
    books = FakeBooks()
    book = books.add(Book(title="T", author="A", isbn="X", total_copies=1,
                          available_copies=0))
    with pytest.raises(BusinessRuleError):
        BorrowBook(books, FakeMembers(), FakeLoans()).execute(book.id, 1)


def test_member_loan_limit():
    from datetime import date
    books = FakeBooks()
    book = books.add(Book(title="T", author="A", isbn="X", total_copies=10))
    loans = FakeLoans()
    for i in range(3):
        loans.add(Loan(book_id=100 + i, member_id=1, loan_date=date.today()))
    with pytest.raises(BusinessRuleError):
        BorrowBook(books, FakeMembers(), loans).execute(book.id, 1)
