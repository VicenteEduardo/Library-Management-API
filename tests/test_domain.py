"""Testes das regras puras: um livro sem título, um empréstimo em atraso, etc."""
from datetime import date, timedelta

import pytest

from app.domain.entities import Book, Loan


def test_book_requires_title():
    with pytest.raises(ValueError):
        Book(title="", author="A", isbn="123")


def test_book_is_available():
    b = Book(title="T", author="A", isbn="1", total_copies=2)
    assert b.is_available is True


def test_loan_default_due_date_is_14_days():
    loan = Loan(book_id=1, member_id=1, loan_date=date(2026, 1, 1))
    assert loan.due_date == date(2026, 1, 15)


def test_loan_overdue_detection():
    loan = Loan(book_id=1, member_id=1,
                loan_date=date.today() - timedelta(days=20),
                due_date=date.today() - timedelta(days=5))
    assert loan.is_overdue is True


def test_return_twice_raises():
    loan = Loan(book_id=1, member_id=1)
    loan.mark_returned()
    with pytest.raises(ValueError):
        loan.mark_returned()
