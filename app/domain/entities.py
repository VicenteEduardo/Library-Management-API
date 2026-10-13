"""Aqui mora o coração da biblioteca: o que é um livro, um membro e um empréstimo.

Estas classes são propositadamente simples e não sabem nada de base de dados
ou de FastAPI — só guardam dados e garantem que nascem válidos."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    total_copies: int = 1
    published_year: Optional[int] = None
    id: Optional[int] = None
    available_copies: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("title é obrigatório")
        if not self.author or not self.author.strip():
            raise ValueError("author é obrigatório")
        if not self.isbn or not self.isbn.strip():
            raise ValueError("isbn é obrigatório")
        if self.total_copies < 1:
            raise ValueError("total_copies deve ser >= 1")
        if self.available_copies is None:
            self.available_copies = self.total_copies
        if self.available_copies < 0 or self.available_copies > self.total_copies:
            raise ValueError("available_copies inválido")

    @property
    def is_available(self) -> bool:
        return (self.available_copies or 0) > 0


@dataclass
class Member:
    name: str
    email: str
    id: Optional[int] = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("name é obrigatório")
        if "@" not in (self.email or ""):
            raise ValueError("email inválido")


@dataclass
class Loan:
    book_id: int
    member_id: int
    loan_date: date = field(default_factory=date.today)
    due_date: Optional[date] = None
    return_date: Optional[date] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.due_date is None:
            self.due_date = self.loan_date + timedelta(days=14)
        if self.due_date < self.loan_date:
            raise ValueError("due_date não pode ser anterior a loan_date")

    @property
    def is_returned(self) -> bool:
        return self.return_date is not None

    @property
    def is_overdue(self) -> bool:
        ref = self.return_date or date.today()
        return (not self.is_returned and ref > self.due_date) or (
            self.is_returned and self.return_date > self.due_date  # type: ignore
        )

    def mark_returned(self, return_date: Optional[date] = None) -> None:
        if self.is_returned:
            raise ValueError("empréstimo já devolvido")
        self.return_date = return_date or date.today()
