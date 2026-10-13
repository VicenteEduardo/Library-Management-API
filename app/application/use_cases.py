"""Os casos de uso: cada ação que a biblioteca sabe fazer.

Cada classe faz uma coisa só — criar um livro, emprestar, devolver, etc. —
e recebe os repositórios de fora, para ser fácil de testar com fakes."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from app.domain.entities import Book, Loan, Member
from app.domain.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.domain.repositories import BookRepository, LoanRepository, MemberRepository
from app.domain.services import validate_borrow


# ---------- Books ----------
class CreateBook:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, title: str, author: str, isbn: str,
                total_copies: int = 1,
                published_year: Optional[int] = None) -> Book:
        if self.books.get_by_isbn(isbn):
            raise ConflictError("ISBN já cadastrado")
        return self.books.add(Book(title=title, author=author, isbn=isbn,
                                   total_copies=total_copies,
                                   published_year=published_year))


class ListBooks:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, skip: int = 0, limit: int = 100) -> List[Book]:
        return self.books.list(skip=skip, limit=limit)


class GetBook:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, book_id: int) -> Book:
        book = self.books.get_by_id(book_id)
        if not book:
            raise NotFoundError("livro não encontrado")
        return book


class UpdateBook:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, book_id: int, **data) -> Book:
        book = GetBook(self.books).execute(book_id)
        if "isbn" in data and data["isbn"] is not None and data["isbn"] != book.isbn:
            if self.books.get_by_isbn(data["isbn"]):
                raise ConflictError("ISBN já cadastrado")
        for key, value in data.items():
            if value is not None and hasattr(book, key):
                setattr(book, key, value)
        # mantém available_copies coerente se total_copies mudar
        if book.available_copies is None:
            book.available_copies = book.total_copies
        if book.available_copies > book.total_copies:
            book.available_copies = book.total_copies
        # revalida invariantes
        book.__post_init__()
        return self.books.update(book)


class DeleteBook:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, book_id: int) -> None:
        GetBook(self.books).execute(book_id)
        self.books.delete(book_id)


# ---------- Members ----------
class CreateMember:
    def __init__(self, members: MemberRepository):
        self.members = members

    def execute(self, name: str, email: str) -> Member:
        if self.members.get_by_email(email):
            raise ConflictError("email já cadastrado")
        return self.members.add(Member(name=name, email=email))


class ListMembers:
    def __init__(self, members: MemberRepository):
        self.members = members

    def execute(self, skip: int = 0, limit: int = 100) -> List[Member]:
        return self.members.list(skip=skip, limit=limit)


class GetMember:
    def __init__(self, members: MemberRepository):
        self.members = members

    def execute(self, member_id: int) -> Member:
        member = self.members.get_by_id(member_id)
        if not member:
            raise NotFoundError("membro não encontrado")
        return member


class UpdateMember:
    def __init__(self, members: MemberRepository):
        self.members = members

    def execute(self, member_id: int, **data) -> Member:
        member = GetMember(self.members).execute(member_id)
        if "email" in data and data["email"] is not None and data["email"] != member.email:
            if self.members.get_by_email(data["email"]):
                raise ConflictError("email já cadastrado")
        for key, value in data.items():
            if value is not None and hasattr(member, key):
                setattr(member, key, value)
        member.__post_init__()
        return self.members.update(member)


class DeleteMember:
    def __init__(self, members: MemberRepository, loans: LoanRepository | None = None):
        self.members = members
        self.loans = loans

    def execute(self, member_id: int) -> None:
        GetMember(self.members).execute(member_id)
        if self.loans is not None:
            active = self.loans.list_active_by_member(member_id)
            if active:
                raise BusinessRuleError("membro possui empréstimos ativos")
        self.members.delete(member_id)


class GetLoan:
    def __init__(self, loans: LoanRepository):
        self.loans = loans

    def execute(self, loan_id: int) -> Loan:
        loan = self.loans.get_by_id(loan_id)
        if not loan:
            raise NotFoundError("empréstimo não encontrado")
        return loan


# ---------- Loans ----------
class BorrowBook:
    def __init__(self, books: BookRepository, members: MemberRepository,
                 loans: LoanRepository):
        self.books = books
        self.members = members
        self.loans = loans

    def execute(self, book_id: int, member_id: int,
                days: int = 14) -> Loan:
        book = self.books.get_by_id(book_id)
        if not book:
            raise NotFoundError("livro não encontrado")
        member = self.members.get_by_id(member_id)
        if not member:
            raise NotFoundError("membro não encontrado")
        if not member.is_active:
            raise BusinessRuleError("membro inativo")

        active = self.loans.list_active_by_member(member_id)
        validate_borrow(book, active)

        loan = Loan(book_id=book_id, member_id=member_id,
                    loan_date=date.today())
        if days:
            from datetime import timedelta
            loan.due_date = loan.loan_date + timedelta(days=days)

        saved = self.loans.add(loan)
        book.available_copies = (book.available_copies or 0) - 1
        self.books.update(book)
        return saved


class ReturnBook:
    def __init__(self, books: BookRepository, loans: LoanRepository):
        self.books = books
        self.loans = loans

    def execute(self, loan_id: int) -> Loan:
        loan = self.loans.get_by_id(loan_id)
        if not loan:
            raise NotFoundError("empréstimo não encontrado")
        loan.mark_returned()
        updated = self.loans.update(loan)
        book = self.books.get_by_id(loan.book_id)
        if book:
            book.available_copies = (book.available_copies or 0) + 1
            if book.available_copies > book.total_copies:
                book.available_copies = book.total_copies
            self.books.update(book)
        return updated


class ListLoans:
    def __init__(self, loans: LoanRepository):
        self.loans = loans

    def execute(self, skip: int = 0, limit: int = 100) -> List[Loan]:
        return self.loans.list(skip=skip, limit=limit)


class ListOverdueLoans:
    def __init__(self, loans: LoanRepository):
        self.loans = loans

    def execute(self) -> List[Loan]:
        return [loan for loan in self.loans.list(skip=0, limit=10000)
                if loan.is_overdue and not loan.is_returned]
